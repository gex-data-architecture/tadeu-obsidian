---
tipo: job-glue
ambiente: 
fluxo: 
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-05-12 17:06
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-silver-clickbank-dedup-oneshot

> Glue ETL · fluxo **—** · ambiente **?**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x10 |
| Timeout (min) | 480 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://aws-glue-assets-406933028738-us-east-1/scripts/gex-silver-clickbank-dedup-oneshot.py` |
| Criado | 2026-04-30 18:46:25.532000-03:00 |
| Modificado | 2026-05-12 17:06:36.710000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--JOB_NAME` | gex-silver-clickbank-dedup-oneshot |
| `--LOOKBACK_DAYS` | 390 |
| `--MIN_PARTITIONS_REQUIRED` | 2 |
| `--SOURCE_DATABASE` | gex_db_prod_bronze |
| `--TARGET_DATABASE` | gex_db_prod_silver |
| `--conf` | spark.eventLog.rolling.enabled=true |
| `--source_bucket` | gex-datalake-bronze-prod |
| `--target_bucket` | gex-datalake-silver-prod |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-05-12 17:06 | SUCCEEDED | 17m24s | — |
| 2026-05-05 02:38 | SUCCEEDED | 13m17s | — |
| 2026-05-05 02:01 | SUCCEEDED | 13m29s | — |
| 2026-05-04 18:46 | SUCCEEDED | 15m1s | — |
| 2026-05-04 18:16 | SUCCEEDED | 13m24s | — |
| 2026-04-30 19:28 | SUCCEEDED | 10m16s | — |
| 2026-04-30 18:48 | SUCCEEDED | 3m50s | — |
| 2026-04-30 18:46 | FAILED | 30s | LAUNCH ERROR / Error downloading from S3 for bucket: aws-glue-assets-406933028738-us-east-1, key: scripts/gex-silver-cli… |

## Script

> Fonte: `s3://aws-glue-assets-406933028738-us-east-1/scripts/gex-silver-clickbank-dedup-oneshot.py` — baixado do S3 (read-only).

````python
"""

Glue Job: gex-bronze-to-silver-{env}
Agrega eventos ClickBank (Sale/Refund/Chargeback/Fee) em 1 linha
por transaction_id, produzindo tb_gex_clickbank_physical_new.

Fontes Bronze:
  tb_bronze_clickbank_vendas_new             — nova API (fonte única)
  tb_bronze_exchange_rates                   — câmbio USD→BRL
  tb_bronze_clickbank_internal_affiliates    — house traffic
  tb_bronze_clickbank_products               — catálogo SKU→offer_name
  tb_bronze_general_product_costs            — custo unitário por vigência

Idempotente: rodar N vezes produz sempre o mesmo resultado.
"""

import sys
import copy
import urllib.parse
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job
from pyspark.sql import functions as F, DataFrame
from pyspark.sql.types import DecimalType, StringType, MapType, DoubleType, LongType, StructType, StructField
from pyspark.sql.window import Window

# ============================================================
# SETUP
# ============================================================
args = getResolvedOptions(sys.argv, [
    'JOB_NAME', 'SOURCE_DATABASE', 'TARGET_DATABASE', 'source_bucket', 'target_bucket'
])


def get_optional_arg(name: str, default: str) -> str:
    token = f"--{name}"
    if token in sys.argv:
        idx = sys.argv.index(token)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return default


LOOKBACK_DAYS = int(get_optional_arg("LOOKBACK_DAYS", "730"))
MIN_PARTITIONS_REQUIRED = int(get_optional_arg("MIN_PARTITIONS_REQUIRED", "1"))


def parse_bool(value: str, default: bool = True) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


ENABLE_SILVER_UPSERT = parse_bool(get_optional_arg("ENABLE_SILVER_UPSERT", "true"), True)
ALLOW_BOOTSTRAP_WITHOUT_HISTORY = parse_bool(
    get_optional_arg("ALLOW_BOOTSTRAP_WITHOUT_HISTORY", "false"),
    False,
)

sc          = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark       = glueContext.spark_session
spark.conf.set("spark.sql.session.timeZone", "America/Sao_Paulo")
job         = Job(glueContext)
job.init(args['JOB_NAME'], args)

SOURCE_DB     = args['SOURCE_DATABASE']
TARGET_DB     = args['TARGET_DATABASE']
SOURCE_BUCKET = args['source_bucket']
OUTPUT_PATH   = f"s3://{args['target_bucket']}/gex_clickbank_physical_new/"

# ============================================================
# HELPERS
# ============================================================
def read_bronze(table: str) -> DataFrame:
    return glueContext.create_dynamic_frame.from_catalog(
        database=SOURCE_DB, table_name=table
    ).toDF()


def read_silver_current(table: str) -> DataFrame:
    return glueContext.create_dynamic_frame.from_catalog(
        database=TARGET_DB, table_name=table
    ).toDF()


def status_rank_expr(col_expr: F.Column) -> F.Column:
    return (
        F.when(col_expr == F.lit("approved"), F.lit(1))
         .when(col_expr == F.lit("refunded_partial"), F.lit(2))
         .when(col_expr == F.lit("refunded"), F.lit(3))
         .when(col_expr == F.lit("chargeback"), F.lit(4))
         .otherwise(F.lit(0))
    )


def ensure(df: DataFrame, col_name: str, cast=StringType()) -> DataFrame:
    return df.withColumn(col_name, F.lit(None).cast(cast)) if col_name not in df.columns else df


def digits_only(col_expr: F.Column) -> F.Column:
    cleaned = F.regexp_replace(F.coalesce(col_expr, F.lit("")), r"[^0-9+]", "")
    return F.when(cleaned != F.lit(""), cleaned)  # "" → null


def title_case_name(first: F.Column, last: F.Column) -> F.Column:
    return F.initcap(F.trim(F.concat_ws(" ",
        F.trim(F.coalesce(first, F.lit(""))),
        F.trim(F.coalesce(last,  F.lit("")))
    )))


@F.udf(MapType(StringType(), StringType()))
def parse_sv(sv_str):
    """Parse querystring de sellervariables → dict."""
    if not sv_str:
        return {}
    result = {}
    for pair in sv_str.split('&'):
        key, _, val = pair.partition('=')
        key = key.strip()
        if key:
            result[key] = urllib.parse.unquote(val)
    return result


@F.udf(MapType(StringType(), StringType()))
def parse_vtid(vtid_str):
    """Parse vtid encapsulado com UTMs: src_X__med_Y__cmp_Z__cnt_W__trm_V."""
    if not vtid_str:
        return {}
    parts = {}
    for segment in vtid_str.split('__'):
        for prefix, key in [
            ('src_', 'utm_source'),  ('med_', 'utm_medium'),
            ('cmp_', 'utm_campaign'), ('cnt_', 'utm_content'),
            ('trm_', 'utm_term'),
        ]:
            if segment.startswith(prefix):
                parts[key] = segment[len(prefix):]
    return parts


# ============================================================
# 1. READ BRONZE NEW
# ============================================================
# Usar spark.read.schema().parquet() com schema explícito (do DESCRIBE da tabela).
#
# Por que não from_catalog:
#   - sem mergeSchema → usa schema físico de 1 partição representativa → partições
#     antigas não têm billingCustomerPhone fisicamente → coluna ausente no DataFrame
#   - com mergeSchema → SchemaMergeUtils.mergeSchemasInParallel detecta orderNumber
#     bigint (partições antigas) vs BINARY (novas) → SparkException
#
# Por que não spark.sql:
#   - Glue 3/4 não registra o Glue Catalog como Hive metastore na Spark session →
#     AnalysisException: Table or view not found
#
# spark.read.schema().parquet():
#   - Schema explícito = exatamente o que o DESCRIBE mostra (sem orderNumber)
#   - Parquet schema evolution: campos ausentes em partições antigas → NULL ✓
#   - orderNumber não está no schema explícito → coluna ignorada → sem conflito ✓
#   - enableVectorizedReader=false: tolerância residual a conflitos de tipo físico
_BRONZE_SCHEMA = StructType([
    StructField("ad",                        StringType(), True),
    StructField("adgroup",                   StringType(), True),
    StructField("affsub1",                   StringType(), True),
    StructField("affsub2",                   StringType(), True),
    StructField("affsub3",                   StringType(), True),
    StructField("affsub4",                   StringType(), True),
    StructField("affsub5",                   StringType(), True),
    StructField("affiliateearnings",         DoubleType(), True),
    StructField("billingcity",               StringType(), True),
    StructField("billingcountry",            StringType(), True),
    StructField("billingcustomeremail",      StringType(), True),
    StructField("billingcustomerfirstname",  StringType(), True),
    StructField("billingcustomerlastname",   StringType(), True),
    StructField("billingcustomerphone",      StringType(), True),
    StructField("billingpostalcode",         StringType(), True),
    StructField("billingstate",              StringType(), True),
    StructField("browser",                  StringType(), True),
    StructField("browserlang",              StringType(), True),
    StructField("browserversion",           StringType(), True),
    StructField("campaign",                 StringType(), True),
    StructField("cbpage",                   StringType(), True),
    StructField("city",                     StringType(), True),
    StructField("clickid",                  StringType(), True),
    StructField("clicktimestamp",           StringType(), True),
    StructField("commissiontype",           StringType(), True),
    StructField("contactid",               StringType(), True),
    StructField("country",                  StringType(), True),
    StructField("couponid",                 StringType(), True),
    StructField("creative",                 StringType(), True),
    StructField("customertax",              DoubleType(), True),
    StructField("declinedmarketing",        StringType(), True),
    StructField("devicebrand",              StringType(), True),
    StructField("devicemodel",              StringType(), True),
    StructField("devicetype",               StringType(), True),
    StructField("extclid",                  StringType(), True),
    StructField("fbclid",                   StringType(), True),
    StructField("foreignexchangefee",       DoubleType(), True),
    StructField("id",                       LongType(),   True),
    StructField("itemquantity",             LongType(),   True),
    StructField("jvaffiliateearnings",      DoubleType(), True),
    StructField("jvsellerearnings",         DoubleType(), True),
    StructField("lineitemtype",             StringType(), True),
    StructField("offer",                    StringType(), True),
    StructField("orderformtemplate",        StringType(), True),
    StructField("os",                       StringType(), True),
    StructField("osversion",                StringType(), True),
    StructField("parent_transaction_receipt", StringType(), True),
    StructField("paymentmethod",            StringType(), True),
    StructField("platformfee",              DoubleType(), True),
    StructField("primaryaffiliate",         StringType(), True),
    StructField("primaryseller",            StringType(), True),
    StructField("productdiscount",          DoubleType(), True),
    StructField("productitemnumber",        StringType(), True),
    StructField("productpurchaseprice",     DoubleType(), True),
    StructField("receiptnumber",            StringType(), True),
    StructField("region",                   StringType(), True),
    StructField("retrycount",               LongType(),   True),
    StructField("roleontransaction",        StringType(), True),
    StructField("salesaccount",             StringType(), True),
    StructField("sellerearnings",           DoubleType(), True),
    StructField("sellervariables",          StringType(), True),
    StructField("shippingandhandling",      DoubleType(), True),
    StructField("shippingcity",             StringType(), True),
    StructField("shippingcountry",          StringType(), True),
    StructField("shippingcustomeremail",    StringType(), True),
    StructField("shippingcustomerfirstname", StringType(), True),
    StructField("shippingcustomerlastname", StringType(), True),
    StructField("shippingcustomerphone",    StringType(), True),
    StructField("shippingpostalcode",       StringType(), True),
    StructField("shippingstate",            StringType(), True),
    StructField("state",                    StringType(), True),
    StructField("trackingid",               StringType(), True),
    StructField("trackingtype",             StringType(), True),
    StructField("trafficsource",            StringType(), True),
    StructField("traffictype",              StringType(), True),
    StructField("transactionamount",        DoubleType(), True),
    StructField("transactiondate",          StringType(), True),
    StructField("transactiontime",          StringType(), True),
    StructField("transactiontype",          StringType(), True),
    StructField("uniqueaffsub1",            StringType(), True),
    StructField("uniqueaffsub2",            StringType(), True),
    StructField("uniqueaffsub3",            StringType(), True),
    StructField("uniqueaffsub4",            StringType(), True),
    StructField("uniqueaffsub5",            StringType(), True),
    StructField("upsellflowid",             StringType(), True),
    StructField("upsellparentreceipt",      StringType(), True),
    StructField("upsellpath",               StringType(), True),
    StructField("useragent",                StringType(), True),
    StructField("yourearnings",             DoubleType(), True),
    StructField("account_owner",            StringType(), True),
    StructField("dt_proc",                  StringType(), True),
])

spark.conf.set("spark.sql.parquet.enableVectorizedReader", "false")
spark.conf.set("spark.sql.files.ignoreMissingFiles", "true")

BRONZE_ROOT_PREFIX = "clickbank/clickbank_vendas_new"
BRONZE_PATH = f"s3://{SOURCE_BUCKET}/{BRONZE_ROOT_PREFIX}/"
s3_client = boto3.client("s3")


def s3_prefix_has_objects(bucket: str, prefix: str) -> bool:
    resp = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
    return resp.get("KeyCount", 0) > 0


def build_candidate_dates(end_date_utc: datetime, lookback_days: int):
    return [(end_date_utc - timedelta(days=d)).date().isoformat() for d in range(lookback_days + 1)]


candidate_dates = build_candidate_dates(datetime.now(timezone.utc), LOOKBACK_DAYS)
existing_partition_paths = []
missing_partition_dates = []

for dt in candidate_dates:
    prefix = f"{BRONZE_ROOT_PREFIX}/dt_proc={dt}/"
    if s3_prefix_has_objects(SOURCE_BUCKET, prefix):
        existing_partition_paths.append(f"s3://{SOURCE_BUCKET}/{prefix}")
    else:
        missing_partition_dates.append(dt)

print(f"[INFO] LOOKBACK_DAYS={LOOKBACK_DAYS} | MIN_PARTITIONS_REQUIRED={MIN_PARTITIONS_REQUIRED}")
print(f"[INFO] Particoes candidatas: {len(candidate_dates)}")
print(f"[INFO] Particoes encontradas: {len(existing_partition_paths)}")
print(f"[INFO] Particoes ausentes: {len(missing_partition_dates)}")
if missing_partition_dates:
    print(f"[DEBUG] Datas ausentes: {missing_partition_dates}")

if len(existing_partition_paths) < MIN_PARTITIONS_REQUIRED:
    raise RuntimeError(
        "Particoes insuficientes para leitura incremental da Bronze. "
        f"Encontradas={len(existing_partition_paths)} | "
        f"Minimo exigido={MIN_PARTITIONS_REQUIRED} | "
        f"Lookback={LOOKBACK_DAYS} dias. "
        "Verifique ingestao upstream (lambda_polling_new / landing_to_bronze_new)."
    )

try:
    df_raw = (
        spark.read
        .schema(_BRONZE_SCHEMA)
        .option("basePath", f"s3://{SOURCE_BUCKET}/{BRONZE_ROOT_PREFIX}")
        .parquet(*existing_partition_paths)
    )
    print("[INFO] Leitura em lote concluida com sucesso.")
except Exception as batch_exc:
    print(f"[WARN] Leitura em lote falhou. Fallback por particao. Motivo: {str(batch_exc)[:500]}")
    part_dfs = []
    corrupted_partition_paths = []

    for path in existing_partition_paths:
        try:
            df_part = (
                spark.read
                .schema(_BRONZE_SCHEMA)
                .option("basePath", f"s3://{SOURCE_BUCKET}/{BRONZE_ROOT_PREFIX}")
                .parquet(path)
            )
            part_dfs.append(df_part)
        except Exception as part_exc:
            corrupted_partition_paths.append(path)
            print(f"[WARN] Particao ignorada por erro de leitura: {path} | {str(part_exc)[:300]}")

    if not part_dfs:
        raise RuntimeError(
            "Falha total na leitura incremental: nenhuma particao valida pode ser lida. "
            f"Particoes encontradas={len(existing_partition_paths)} | "
            f"Particoes corrompidas={len(corrupted_partition_paths)}"
        )

    df_raw = part_dfs[0]
    for dfi in part_dfs[1:]:
        df_raw = df_raw.unionByName(dfi, allowMissingColumns=True)

    print(
        "[INFO] Fallback por particao concluido. "
        f"Particoes validas={len(part_dfs)} | corrompidas={len(corrupted_partition_paths)}"
    )

# Schema já é lowercase e correto — .toDF() desnecessário mas mantido para
# garantia de consistência caso algum campo chegue em camelCase do Parquet.
df_raw = df_raw.toDF(*[c.lower() for c in df_raw.columns])

_total_raw = df_raw.count()
print(f"[DEBUG] df_raw lido da Bronze ({BRONZE_PATH}): {_total_raw} linhas")

for c in [
    "yourearnings", "jvaffiliateearnings", "jvsellerearnings",
    "upsellparentreceipt", "lineitemtype", "upsellflowid", "upsellpath",
    "shippingcustomerfirstname", "shippingcustomerlastname",
    "shippingcustomerphone", "shippingcustomeremail",
    "shippingcity", "shippingstate", "shippingpostalcode", "shippingcountry",
    "billingcustomerphone",
    "billingcity", "billingstate",
    "billingpostalcode", "billingcountry",
    "affsub1", "affsub2", "affsub3", "affsub4", "affsub5",
    "trafficsource", "campaign", "trackingid", "ad", "adgroup",
    "devicebrand", "devicemodel", "osversion", "browserversion",
    "browserlang", "useragent", "clickid", "offer",
    "paymentmethod", "contactid", "couponid",
]:
    df_raw = ensure(df_raw, c, StringType())

for c in ["foreignexchangefee", "productdiscount", "shippingandhandling"]:
    df_raw = ensure(df_raw, c, DoubleType())

for c in ["itemquantity", "retrycount"]:
    df_raw = ensure(df_raw, c, LongType())

# Normalizar lineitemtype para UPPERCASE antes do groupBy
# Partições antigas podem ter mixed case ou null — garantir consistência
df_raw = df_raw.withColumn("lineitemtype",
    F.when(
        F.col("lineitemtype").isNotNull() & (F.trim(F.col("lineitemtype")) != ""),
        F.upper(F.trim(F.col("lineitemtype")))
    ).otherwise(F.lit(None).cast("string"))
)

# Converter strings vazias "" → null nos campos de contato billing/shipping
# Partições antigas retornam "" em vez de null — first(ignorenulls=True) não filtra ""
_campos_contato = [
    "billingcustomerfirstname", "billingcustomerlastname",
    "billingcustomeremail", "billingcustomerphone",
    "billingcity", "billingstate", "billingpostalcode", "billingcountry",
    "shippingcustomerfirstname", "shippingcustomerlastname",
    "shippingcustomerphone", "shippingcustomeremail",
    "shippingcity", "shippingstate", "shippingpostalcode", "shippingcountry",
]
for _c in _campos_contato:
    df_raw = df_raw.withColumn(_c,
        F.when(
            F.col(_c).isNotNull() & (F.trim(F.col(_c)) != ""),
            F.col(_c)
        ).otherwise(F.lit(None).cast("string"))
    )

# ============================================================
# 2. DEDUP NÍVEL 1 — remove cópias de polling (chave: id + productitemnumber)
#    Todas as cópias são idênticas → first(ignorenulls=True) equivale a any_value
# ============================================================
def _first(col_name):
    return F.first(col_name, ignorenulls=True).alias(col_name)

def _first_cast(col_name, cast_type):
    return F.first(F.col(col_name).cast(cast_type), ignorenulls=True).alias(col_name)

df = (
    df_raw
    .groupBy("id", "productitemnumber")
    .agg(
        _first("receiptnumber"),
        _first("salesaccount"),
        _first("transactiontype"),
        _first("lineitemtype"),
        _first_cast("transactionamount",    "double"),
        _first_cast("sellerearnings",       "double"),
        _first_cast("yourearnings",         "double"),
        _first_cast("affiliateearnings",    "double"),
        _first_cast("productpurchaseprice", "double"),
        _first_cast("shippingandhandling",  "double"),
        _first_cast("customertax",          "double"),
        _first_cast("platformfee",          "double"),
        _first_cast("itemquantity",         "bigint"),
        _first("transactiondate"),
        _first("transactiontime"),
        _first("primaryaffiliate"),
        _first("sellervariables"),
        _first("upsellpath"),
        _first("upsellflowid"),
        _first("upsellparentreceipt"),
        _first("offer"),
        _first("billingcustomerfirstname"),
        _first("billingcustomerlastname"),
        _first("billingcustomeremail"),
        _first("billingcustomerphone"),
        _first("billingcity"),
        _first("billingstate"),
        _first("billingpostalcode"),
        _first("billingcountry"),
        _first("shippingcustomerfirstname"),
        _first("shippingcustomerlastname"),
        _first("shippingcustomerphone"),
        _first("shippingcustomeremail"),
        _first("shippingcity"),
        _first("shippingstate"),
        _first("shippingpostalcode"),
        _first("shippingcountry"),
        _first("affsub1"),
        _first("affsub2"),
        _first("affsub3"),
        _first("affsub4"),
        _first("affsub5"),
        _first("trafficsource"),
        _first("campaign"),
        _first("trackingid"),
        _first("ad"),
        _first("adgroup"),
        _first("devicetype"),
        _first("devicebrand"),
        _first("devicemodel"),
        _first("os"),
        _first("osversion"),
        _first("browser"),
        _first("browserversion"),
        _first("browserlang"),
        _first("useragent"),
        _first("clicktimestamp"),
        _first("clickid"),
        _first("couponid"),
        F.max("dt_proc").alias("dt_proc"),
    )
)
_dedup_total = df.count()
print(f"[DEBUG] df após dedup nível 1 (id+productitemnumber): {_dedup_total} linhas")

# ============================================================
# 3. DEDUP NÍVEL 2 — gerar transaction_id
#    BUMP → receiptnumber-B1, -B2, ...   |   demais → receiptnumber
# ============================================================
w_bump_sku = Window.partitionBy("receiptnumber").orderBy("productitemnumber")

# Rankia bump por SKU físico (apenas Sale) e reaplica o mesmo rank
# para Refund/Chargeback/Fee do mesmo bump SKU.
df_bump_rank = (
    df
    .filter(
        (F.upper(F.col("lineitemtype")) == "BUMP") &
        (F.initcap(F.trim(F.col("transactiontype"))) == "Sale")
    )
    .select("receiptnumber", "productitemnumber")
    .dropDuplicates(["receiptnumber", "productitemnumber"])
    .withColumn("_bump_rank", F.row_number().over(w_bump_sku))
)

df = (
    df
    .join(df_bump_rank, on=["receiptnumber", "productitemnumber"], how="left")
    .withColumn("transaction_id",
        F.when(
            # Refund/Chargeback/Fee de bumps podem chegar com lineitemtype nulo ou
            # diferente de BUMP; se o SKU recebeu bump_rank no par receipt+sku,
            # o evento pertence ao mesmo transaction_id do bump.
            F.col("_bump_rank").isNotNull(),
            F.concat(F.col("receiptnumber"), F.lit("-B"), F.col("_bump_rank").cast("string"))
        ).otherwise(F.col("receiptnumber"))
    )
    .drop("_bump_rank")
)

# ============================================================
# 3.5. QUANTIDADE REAL POR SKU
#      A API ClickBank sempre retorna itemquantity=1 (representa a linha do pedido,
#      não as unidades físicas do produto). A quantidade real de frascos está
#      codificada no SKU em quatro formatos:
#
#      Formato 1 — dash-separado:  pp-nst6units-aff         → 6
#                                  up1-nst12units-aff        → 12
#                                  pp-gst6units-emailmon     → 6
#      Formato 2 — CBIEG PP:       CBIEMMPPP6UNITSAFF        → 6
#                                  CBIEGLTPP6UNITSAFF        → 6
#      Formato 3 — CBIEG UP:       CBIEMMPUP112UNITSAFF      → 12
#                                  CBIEMLT150UP13UNITSAFF    → 3
#      Formato 4 — CBIEG DW:       CBIEGLTDW16UNITSAFF       → 6
#                                  CBIEGLTDW112UNITSAFF      → 12
#
#      Fallback: itemquantity (sempre 1) → F.lit(1)
# ============================================================
_sku_lower = F.lower(F.col("productitemnumber"))
_sku_upper = F.upper(F.col("productitemnumber"))

# O legado do N8N extrai a quantidade procurando o trecho imediatamente
# anterior a UNITS, aceitando na pratica 12 ou um unico digito.
# Isso evita inflar SKUs como DW1212UNITS para 212; o valor esperado e 12.
_qty_n8n_like = F.regexp_extract(_sku_upper, r'(12|[1-9])UNITS?', 1)

df = df.withColumn("_qty_from_sku",
    F.coalesce(
        F.when(_qty_n8n_like != F.lit(''), _qty_n8n_like.cast("int")),
        F.col("itemquantity").cast("int"),
        F.lit(1),
    )
)
print(f"[DEBUG] Amostra qty_from_sku:")
df.select("productitemnumber", "itemquantity", "_qty_from_sku") \
  .filter(F.col("_qty_from_sku") != F.col("itemquantity").cast("int")) \
  .show(10, truncate=False)

# Tipo normalizado e datetime completo
# - _datetime_platform_str: horário real da plataforma (EUA), sem conversão
# - _datetime_gmt3: horário local do Brasil para created_at_* e date_refunded
# Regra operacional: converter Pacific Time -> America/Sao_Paulo
# com timezone real (sem soma fixa de horas).
df = (
    df
    .withColumn("_type", F.initcap(F.trim(F.col("transactiontype"))))
    # transactiontime pode ser:
    #   Formato A (novo): "2026-04-07T19:49:08.000+00:00" — ISO completo
    #   Formato B (legado): "19:49:08" — só hora
    # Solução robusta: regex extrai sempre o HH:mm:ss e combina com transactiondate
    # Evita depender do comportamento de to_timestamp() com strings de hora pura
    # (Spark 3.3 pode retornar data-de-hoje + hora em vez de NULL para "HH:mm:ss")
    # _platform_dt_str: normaliza para "yyyy-MM-dd HH:mm:ss" sem timezone
    .withColumn("_platform_dt_str",
        F.when(
            F.col("transactiontime").rlike(r'^\d{4}-\d{2}-\d{2}T'),
            F.regexp_replace(
                F.regexp_extract(F.col("transactiontime"), r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', 1),
                "T",
                " "
            )
        ).otherwise(
            F.when(
                F.regexp_extract(F.col("transactiontime"), r'(\d{2}:\d{2}:\d{2})', 1) != "",
                F.concat_ws(
                    " ",
                    F.col("transactiondate"),
                    F.regexp_extract(F.col("transactiontime"), r'(\d{2}:\d{2}:\d{2})', 1)
                )
            )
        )
    )
    # timestamp sem timezone, interpretado como hora da plataforma EUA
    .withColumn("_platform_ts", F.to_timestamp(F.col("_platform_dt_str"), "yyyy-MM-dd HH:mm:ss"))
    # Converte horário da plataforma (US Pacific) -> BR considerando timezone.
    .withColumn(
        "_datetime_gmt3",
        F.from_utc_timestamp(
            F.to_utc_timestamp(F.col("_platform_ts"), "America/Los_Angeles"),
            "America/Sao_Paulo"
        )
    )
    .withColumn(
        "_datetime_platform_str",
        F.col("_platform_dt_str")
    )
    .drop("_platform_dt_str", "_platform_ts")
)

df.cache()
df.count()  # materializa cache antes dos múltiplos groupBy

# ============================================================
# 4. AGREGADOS POR transaction_id
# ============================================================

# 4a. Commission = SUM(COALESCE(sellerearnings, yourearnings)) — todos os eventos
#     sellerearnings já carrega sinal correto: Sale(+), Refund/CBK/Fee(-)
df_commission = (
    df
    .groupBy("transaction_id")
    .agg(
        F.sum(
            F.coalesce(F.col("sellerearnings"), F.col("yourearnings"), F.lit(0.0))
        ).alias("commission_usd")
    )
)

# 4b. Account Amount — snapshot do último evento principal por transaction_id.
#     Considera apenas Sale/Refund/Chargeback e ignora Fee, para manter
#     conciliação com o dashboard ClickBank e separar multas em campos próprios.
w_last_ev = Window.partitionBy("transaction_id").orderBy(F.col("_datetime_gmt3").desc())
df_last_event = (
    df
    .filter(F.col("_type").isin("Sale", "Refund", "Chargeback"))
    .withColumn("_rn_last", F.row_number().over(w_last_ev))
    .filter(F.col("_rn_last") == 1)
    .select(
        "transaction_id",
        F.coalesce(
            F.col("sellerearnings"), F.col("yourearnings"), F.lit(0.0)
        ).alias("_last_event_amount"),
    )
)

# 4c. Refund — total_refund_usd cobre apenas Refund (regra: Chargeback não preenche este campo).
#     date_refunded cobre Refund E Chargeback via _rfnd_dt + fallback _cb_dt (ver passo 16).
df_rfnd = (
    df.filter(F.col("_type").isin("Refund", "Chargeback"))
    .groupBy("transaction_id")
    .agg(
        F.sum(F.abs(F.col("productpurchaseprice"))).alias("total_refund_usd"),
        F.min(F.struct(
            F.col("_datetime_gmt3").alias("dt"),
            F.col("_datetime_platform_str").alias("dt_platform_str"),
        )).alias("_rfnd_ts"),
    )
    .withColumn("_rfnd_dt",     F.col("_rfnd_ts.dt"))
    .withColumn("_rfnd_dt_platform_str", F.col("_rfnd_ts.dt_platform_str"))
    .drop("_rfnd_ts")
)

# 4d. Chargeback
df_cb = (
    df.filter(F.col("_type") == "Chargeback")
    .groupBy("transaction_id")
    .agg(
        F.lit(True).cast("boolean").alias("_has_chargeback"),
        F.min(F.struct(
            F.col("_datetime_gmt3").alias("dt"),
            F.col("_datetime_platform_str").alias("dt_platform_str"),
        )).alias("_cb_ts"),
    )
    .withColumn("_cb_dt",     F.col("_cb_ts.dt"))
    .withColumn("_cb_dt_platform_str", F.col("_cb_ts.dt_platform_str"))
    .drop("_cb_ts")
)

# 4e. Fee — chargeback fee
#     Regra: fee aplica somente no transaction_id STANDARD (sem sufixo -B).
#     Fonte principal: SKU cgbk-* (independe de transactiontype textual).
#     Fallback: transactiontype=Fee + primaryaffiliate=debitcgbk.
df_fee_cbk = (
    df.filter(
        (~F.col("transaction_id").rlike(r"-B\d+$")) &
        (
            F.lower(F.coalesce(F.col("productitemnumber"), F.lit(""))).rlike(r"^cgbk-") |
            (
                (F.col("_type") == "Fee") &
                (F.lower(F.coalesce(F.col("primaryaffiliate"), F.lit(""))) == F.lit("debitcgbk"))
            )
        )
    )
    .groupBy("transaction_id")
    .agg(F.sum(F.abs(F.col("transactionamount"))).alias("chargeback_fee_usd"))
)

# 4f. Fee — refund fee
#     Regra: fee aplica somente no transaction_id STANDARD (sem sufixo -B).
#     Fonte principal: SKU rfnd-* (independe de transactiontype textual).
#     Fallback: transactiontype=Fee + primaryaffiliate=debitrfnd.
df_fee_rfnd = (
    df.filter(
        (~F.col("transaction_id").rlike(r"-B\d+$")) &
        (
            F.lower(F.coalesce(F.col("productitemnumber"), F.lit(""))).rlike(r"^rfnd-") |
            (
                (F.col("_type") == "Fee") &
                (F.lower(F.coalesce(F.col("primaryaffiliate"), F.lit(""))) == F.lit("debitrfnd"))
            )
        )
    )
    .groupBy("transaction_id")
    .agg(F.sum(F.abs(F.col("transactionamount"))).alias("refund_fee_usd"))
)

# ============================================================
# 5. SALE BASE — 1 linha por transaction_id (Sale mais recente)
# ============================================================
w_sale = Window.partitionBy("transaction_id").orderBy(F.col("_datetime_gmt3").desc())

sale_base = (
    # Rebill tem mesma estrutura financeira da Sale (platformfee, customertax preenchidos)
    df.filter(F.col("_type").isin("Sale", "Rebill"))
    .withColumn("_rn", F.row_number().over(w_sale))
    .filter(F.col("_rn") == 1)
    .drop("_rn")
    .withColumnRenamed("_datetime_gmt3", "_sale_dt")
    .withColumnRenamed("_datetime_platform_str", "_sale_dt_platform_str")
)
print(f"[DEBUG] sale_base: {sale_base.count()} linhas")

# ============================================================
# 6. ORPHAN BASE — transaction_ids sem Sale (Refund/CBK chegou antes da Sale)
#    Para orphans, usamos os dados disponíveis do evento Refund/CBK como proxy:
#    - transactiondate mantido para exchange_rate lookup e created_at_date
#    - productpurchaseprice: ABS() para total_price_usd (vem negativo no Refund)
#    - transactionamount mantido para total_collected_usd
#    - affiliateearnings mantido
#    - itemquantity mantido (para _qty_from_sku que já foi calculado)
#    Quando Sale chegar em execução futura: overwrite com dados corretos da Sale
#    Aplica para qualquer lineitemtype (STANDARD, BUMP, UPSELL)
# ============================================================
sale_tids = sale_base.select("transaction_id").distinct()
w_orphan  = Window.partitionBy("transaction_id").orderBy(F.col("_datetime_gmt3"))

orphan_base = (
    df.filter(F.col("_type") != "Fee")
    .join(sale_tids, on="transaction_id", how="left_anti")
    .withColumn("_rn", F.row_number().over(w_orphan))
    .filter(F.col("_rn") == 1)
    .drop("_rn")
    # productpurchaseprice vem negativo em Refund/CBK → usar ABS para total_price_usd
    .withColumn("productpurchaseprice", F.abs(F.col("productpurchaseprice")))
    .withColumn("shippingandhandling", F.abs(F.col("shippingandhandling")))
    # customertax e platformfee não existem em Refund/CBK → null
    .withColumn("customertax",          F.lit(None).cast("double"))
    .withColumn("platformfee",          F.lit(None).cast("double"))
    # transactionamount: null para orphans — CBK/Refund têm valor negativo →
    # total_collected_usd ficaria negativo sem este null (campo pertence à Sale)
    .withColumn("transactionamount",    F.lit(None).cast("double"))
    # affiliateearnings: null para orphans — CBK pode retornar valor negativo →
    # affiliate_amount_usd ficaria negativo sem este null
    .withColumn("affiliateearnings",    F.lit(None).cast("double"))
    .withColumnRenamed("_datetime_gmt3", "_sale_dt")
    .withColumnRenamed("_datetime_platform_str", "_sale_dt_platform_str")
)
print(f"[DEBUG] orphan_base: {orphan_base.count()} linhas")

# ============================================================
# 7. BASE COMPLETA = Sale + Orphans
# ============================================================
base = sale_base.unionByName(orphan_base, allowMissingColumns=True)
print(f"[DEBUG] base após UNION (sale + orphan): {base.count()} linhas")

# ============================================================
# 8. JOIN AGREGADOS
# ============================================================
result = (
    base
    .join(df_commission,  on="transaction_id", how="left")
    .join(df_last_event,  on="transaction_id", how="left")
    .join(df_rfnd,        on="transaction_id", how="left")
    .join(df_cb,          on="transaction_id", how="left")
    .join(df_fee_cbk,     on="transaction_id", how="left")
    .join(df_fee_rfnd,    on="transaction_id", how="left")
)
print(f"[DEBUG] result após JOINs de agregados: {result.count()} linhas")

# ============================================================
# 9. LOOKUP — exchange rate (câmbio fixo no dia da Sale, nunca sobrescrito)
# ============================================================
df_rates = (
    read_bronze("tb_bronze_exchange_rates")
    .filter(
        (F.col("source_currency") == "USD") &
        (F.col("target_currency") == "BRL")
    )
    .select(
        F.col("date").cast("date").alias("_rd"),
        F.col("rate").cast("double").alias("exchange_rate"),
    )
)

_latest_rate   = df_rates.orderBy(F.col("_rd").desc()).select("exchange_rate").first()
_fallback_rate = _latest_rate["exchange_rate"] if _latest_rate else 5.10

result = (
    result
    .withColumn("_sale_date", F.to_date(F.col("transactiondate")))
    .join(df_rates, F.col("_sale_date") == F.col("_rd"), "left")
    .drop("_rd")
    .withColumn("exchange_rate",
        F.when(F.col("_sale_date").isNotNull(),
            F.coalesce(F.col("exchange_rate"), F.lit(_fallback_rate))
        )
    )
)

# ============================================================
# 10. LOOKUP — internal affiliates (house traffic + traffic_source + traffic_manager)
# ============================================================
df_ia = (
    read_bronze("tb_bronze_clickbank_internal_affiliates")
    .select(
        F.lower(F.col("affiliate_name")).alias("_ia_name"),
        F.col("traffic_source").alias("_ia_ts"),
        F.col("traffic_manager").alias("_ia_tm"),
    )
    .distinct()
)

result = (
    result
    .join(
        df_ia,
        F.lower(F.coalesce(F.col("primaryaffiliate"), F.lit(""))) == F.col("_ia_name"),
        "left"
    )
    .withColumn("is_house_traffic", F.col("_ia_name").isNotNull())
    .withColumnRenamed("_ia_ts", "traffic_source")
    .withColumnRenamed("_ia_tm", "traffic_manager")
    .drop("_ia_name")
)

# ============================================================
# 11. LOOKUP — product catalog (offer_name por productitemnumber + salesaccount)
# ============================================================
df_prod_raw = read_bronze("tb_bronze_clickbank_products")
df_prod_raw = ensure(df_prod_raw, "product_name", StringType())

# productitemnumber na Bronze New chega LOWERCASE (ex: cbiegpzpp6unitsaff)
# product_id na tabela de produtos é UPPERCASE (ex: CBIEGPZPP6UNITSAFF)
# Dedup: tabela pode ter múltiplas linhas por product_id+account_name,
# algumas com offer_name null — priorizar linha com valor preenchido
w_prod = Window.partitionBy(
    F.lower(F.col("product_id")),
    F.lower(F.col("account_name"))
).orderBy(
    F.col("offer_name").isNull().asc(),    # prioriza linha com offer_name preenchido
    F.col("product_name").isNull().asc(),  # desempate: prioriza linha com product_name preenchido
)

df_prod = (
    df_prod_raw
    .withColumn("_rn", F.row_number().over(w_prod))
    .filter(F.col("_rn") == 1)
    .drop("_rn")
    .select(
        F.lower(F.col("product_id")).alias("_lk_pid"),
        F.lower(F.col("account_name")).alias("_lk_acc"),
        F.col("offer_name").alias("_lk_offer_name"),
        F.col("product_name").alias("_lk_product_name"),
    )
)

result = (
    result
    .join(
        df_prod,
        (F.lower(F.coalesce(F.col("productitemnumber"), F.lit(""))) == F.col("_lk_pid")) &
        (F.lower(F.coalesce(F.col("salesaccount"), F.lit(""))) == F.col("_lk_acc")),
        "left"
    )
    .drop("_lk_pid", "_lk_acc")
    .withColumn(
        "offer_name",
        F.coalesce(F.col("_lk_offer_name"), F.col("offer"), F.col("productitemnumber"))
    )
    .withColumn(
        "product_name",
        F.coalesce(F.col("_lk_product_name"), F.col("offer"), F.col("productitemnumber"))
    )
    .drop("_lk_offer_name", "_lk_product_name")
)

# ============================================================
# 11.5. ENRICH OFFER_NAME — house traffic
#       Replica a lógica da procedure MySQL fill_clickbank_offer_names:
#       1. Para is_house_traffic=TRUE com 'Affiliate Marketing' no offer_name:
#          - Substitui 'Affiliate Marketing' por traffic_source
#          - Insere '[Gestor de Tráfego: <traffic_manager>]' no penúltimo bloco
#       2. Demais linhas: offer_name permanece inalterado
# ============================================================

# Passo 1 — replace Affiliate Marketing por traffic_source
_offer_replaced = F.when(
    F.col("is_house_traffic") &
    F.col("traffic_source").isNotNull() &
    F.col("offer_name").contains("Affiliate Marketing"),
    F.expr("replace(offer_name, 'Affiliate Marketing', traffic_source)")
).otherwise(F.col("offer_name"))

# Passo 2 — localiza a última ocorrência de '] [' via reverse + instr
_has_multi_block = _offer_replaced.contains("] [")

# Prefixo sem o último bloco: "A [B] [C]" -> "A [B"
_offer_prefix = F.regexp_replace(_offer_replaced, r"\] \[[^\[\]]+\]$", "")

# Último bloco sem colchetes: "A [B] [C]" -> "C"
_offer_last_block = F.regexp_extract(_offer_replaced, r"\] \[([^\[\]]+)\]$", 1)

# Passo 3 — monta o offer_name final só para is_house_traffic com 'Affiliate Marketing'
_should_enrich = (
    F.col("is_house_traffic") &
    F.col("traffic_source").isNotNull() &
    F.col("traffic_manager").isNotNull() &
    F.col("offer_name").contains("Affiliate Marketing")
)

_enriched_multi = F.concat(
    _offer_prefix,
    F.lit(" [Gestor de Tráfego: "),
    F.col("traffic_manager"),
    F.lit("] ["),
    _offer_last_block,
    F.lit("]")
)

_enriched_single = F.concat(
    _offer_replaced,
    F.lit(" [Gestor de Tráfego: "),
    F.col("traffic_manager"),
    F.lit("]")
)

result = result.withColumn(
    "offer_name",
    F.when(_should_enrich,
        F.when(_has_multi_block, _enriched_multi).otherwise(_enriched_single)
    ).otherwise(F.col("offer_name"))
)

print("[DEBUG] Sample offer_name após enriquecimento (house_traffic=1):")
result.filter(F.col("is_house_traffic") == True).select(
    "transaction_id", "primaryaffiliate", "traffic_source", "traffic_manager", "offer_name"
).show(5, truncate=False)

_non_product_cost_item = (
    F.lower(F.coalesce(F.col("productitemnumber"), F.lit(""))).rlike(r"^priorityshipping") |
    F.lower(F.coalesce(F.col("product_name"), F.lit(""))).rlike(r"priority\s*\+?\s*insured\s*shipping") |
    F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).rlike(r"priority\s*\+?\s*insured\s*shipping") |
    F.lower(F.coalesce(F.col("product_name"), F.lit(""))).rlike(r"\bbuy\s+\d+\s*[,/-]?\s*get\s+\d+\s+free\b(?!\s*bottles?)") |
    F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).rlike(r"\bbuy\s+\d+\s*[,/-]?\s*get\s+\d+\s+free\b(?!\s*bottles?)")
)

result = result.withColumn(
    "_effective_qty",
    F.when(_non_product_cost_item, F.lit(0)).otherwise(
        F.coalesce(F.col("_qty_from_sku"), F.col("itemquantity").cast("int"), F.lit(1))
    )
)

# ============================================================
# 12. LOOKUP — product cost (itemquantity × unit_cost_usd por vigência de data)
# ============================================================
df_costs = (
    read_bronze("tb_bronze_general_product_costs")
    .select(
        F.col("unit_cost_usd").cast("double").alias("_ucost"),
        F.col("valid_from").cast("date").alias("_cf"),
        F.coalesce(
            F.col("valid_until").cast("date"),
            F.lit("9999-12-31").cast("date")
        ).alias("_cu"),
    )
)

result = (
    result
    .join(
        df_costs,
        (F.coalesce(F.col("_sale_date"), F.current_date()) >= F.col("_cf")) &
        (F.coalesce(F.col("_sale_date"), F.current_date()) <= F.col("_cu")),
        "left"
    )
    .drop("_cf", "_cu")
    .withColumn("product_cost_usd",
        F.when(F.col("_sale_date").isNotNull(),
            F.col("_effective_qty").cast("double") *
            F.coalesce(F.col("_ucost"), F.lit(5.0))
        )
    )
    .drop("_ucost")
)

# ============================================================
# 13. PARSE SELLERVARIABLES (Regra 14)
#     Prioridade: campo direto > sellervariables > vtid parse
# ============================================================
result = result.withColumn("_sv_map",   parse_sv(F.col("sellervariables")))
result = result.withColumn("_vtid_raw", F.coalesce(F.col("trackingid"), F.col("_sv_map").getItem("vtid")))
result = result.withColumn("_vtid_map", parse_vtid(F.col("_vtid_raw")))

result = (
    result
    .withColumn("src",          F.col("_sv_map").getItem("src"))
    .withColumn("vtid",
        F.when(
            F.col("_vtid_raw").rlike(r"^\{.*\}$"),  # placeholder literal {vtid}, {tid}, etc.
            F.lit(None)
        ).otherwise(F.col("_vtid_raw"))
    )
    .withColumn("cbfid",        F.coalesce(F.col("upsellflowid"), F.col("_sv_map").getItem("cbfid")))
    .withColumn("utm_source",   F.coalesce(
        F.col("trafficsource"),
        F.col("_sv_map").getItem("utm_source"),
        F.col("_vtid_map").getItem("utm_source"),
    ))
    .withColumn("utm_medium",   F.coalesce(
        F.col("_sv_map").getItem("utm_medium"),
        F.col("_vtid_map").getItem("utm_medium"),
    ))
    .withColumn("utm_campaign", F.coalesce(
        F.col("campaign"),
        F.col("_sv_map").getItem("utm_campaign"),
        F.col("_vtid_map").getItem("utm_campaign"),
    ))
    .withColumn("utm_content",  F.coalesce(
        F.col("_sv_map").getItem("utm_content"),
        F.col("_vtid_map").getItem("utm_content"),
    ))
    .withColumn("utm_term",     F.coalesce(
        F.col("_sv_map").getItem("utm_term"),
        F.col("_vtid_map").getItem("utm_term"),
    ))
    .withColumn("aff_sub",  F.coalesce(F.col("affsub1"), F.col("_sv_map").getItem("affSub")))
    .withColumn("aff_sub2", F.coalesce(F.col("affsub2"), F.col("_sv_map").getItem("affSub2")))
    .withColumn("aff_sub3", F.coalesce(F.col("affsub3"), F.col("_sv_map").getItem("affSub3")))
    .withColumn("aff_sub4", F.coalesce(F.col("affsub4"), F.col("_sv_map").getItem("affSub4")))
    .withColumn("aff_sub5", F.coalesce(F.col("affsub5"), F.col("_sv_map").getItem("affSub5")))
    .drop("_sv_map", "_vtid_raw", "_vtid_map")
)

# ============================================================
# 13.5. COUPON CODE — couponid direto > cbitems de sellervariables
#       couponid: campo nativo STRING (ex: "15999") confirmado pelo DESCRIBE
#       sellervariables: fallback extraindo cbitems=XX da querystring
# ============================================================
result = result.withColumn("coupon_code",
    F.coalesce(
        F.when(
            F.col("couponid").isNotNull() & (F.trim(F.col("couponid")) != ""),
            F.col("couponid")
        ),
        F.when(
            F.regexp_extract(F.col("sellervariables"), r"cbitems=([^&]+)", 1) != "",
            F.regexp_extract(F.col("sellervariables"), r"cbitems=([^&]+)", 1)
        )
    )
)

# ============================================================
# 14. SALES TYPE (Regra 7) — fonte: lineitemtype (STANDARD/BUMP/UPSELL)
#     Fallback 1: prefixo do productitemnumber (nova API não retorna lineitemtype)
#       pp-*     → Produto Principal
#       up<n>-*  → Venda de Funil
#       bump-*   → Order Bump
#     Fallback 2: tags estruturadas no offer_name ("[Produto Principal]", "[Upsell", "[Order Bump]")
# ============================================================
result = result.withColumn("sales_type",
    # BUMP e UPSELL explícitos do lineitemtype são definitivos
    F.when(F.col("lineitemtype") == "BUMP",   F.lit("Order Bump"))
     .when(F.col("lineitemtype") == "UPSELL", F.lit("Venda de Funil"))
     # Prefixo do SKU tem prioridade sobre STANDARD — necessário para Rebill:
     # ClickBank envia lineitemtype=STANDARD em alguns Rebills mesmo para produtos upsell
     # (ex: up3-kitrglt5units-aff com lineitemtype=STANDARD deve ser "Venda de Funil")
     .when(F.col("productitemnumber").rlike(r"^(up|dw)\d+-"), F.lit("Venda de Funil"))
     .when(F.col("productitemnumber").rlike(r"^bump-"),        F.lit("Order Bump"))
     .when(F.col("productitemnumber").rlike(r"-ob$"),           F.lit("Order Bump"))
     # Tags no offer_name — captura CBIEGs e outros SKUs sem prefixo estruturado
     .when(F.col("offer_name").contains("[Upsell"),             F.lit("Venda de Funil"))
     .when(F.col("offer_name").contains("[Downsell"),           F.lit("Venda de Funil"))
     .when(F.col("offer_name").contains("[Order Bump]"),        F.lit("Order Bump"))
     # STANDARD do lineitemtype ou prefixo pp- = Produto Principal
     .when(F.col("lineitemtype") == "STANDARD",                  F.lit("Produto Principal"))
     .when(F.col("productitemnumber").rlike(r"^pp-"),            F.lit("Produto Principal"))
     .when(F.col("offer_name").contains("[Produto Principal]"),  F.lit("Produto Principal"))
     .otherwise(F.lit("Não Identificado"))
)

# ============================================================
# 15. PAYMENT STATUS — só avança, nunca regride (Regra 4)
#     chargeback > refunded > refunded_partial > approved
#     Tax-only refund: total_refund_usd < 0.01 → cobre naturalmente via refunded_partial
# ============================================================
result = result.withColumn("payment_status",
    F.when(
        F.col("_has_chargeback").isNotNull() & F.col("_has_chargeback"),
        F.lit("chargeback")
    ).when(
        F.col("total_refund_usd").isNotNull() &
        (F.col("total_refund_usd") >= F.lit(0.01)) &
        (F.col("total_refund_usd") >= F.coalesce(
            F.col("productpurchaseprice"),
            F.lit(0.0)
        )),
        F.lit("refunded")
    ).when(
        F.col("total_refund_usd").isNotNull(),
        F.lit("refunded_partial")
    ).otherwise(
        F.lit("approved")
    )
)

# ============================================================
# 16. DATAS GMT-3 (Regra 6)
#     date_refunded cobre Refund E Chargeback — sem campo chargeback_date separado
# ============================================================
result = (
    result
    .withColumn(
        "_total_price_usd",
        F.round(
            F.coalesce(F.col("productpurchaseprice"), F.lit(0.0)) +
            F.coalesce(F.col("shippingandhandling"), F.lit(0.0)),
            2
        )
    )
    .withColumn("created_at_date",
        F.when(F.col("_sale_dt").isNotNull(),
            F.date_format(F.col("_sale_dt"), "yyyy-MM-dd")
        )
    )
    .withColumn("created_at_hour",
        F.when(F.col("_sale_dt").isNotNull(),
            F.date_format(F.col("_sale_dt"), "HH:mm:ss")
        )
    )
    .withColumn("datetime_platform",
        F.col("_sale_dt_platform_str")
    )
    .withColumn("date_refunded",
        F.when(F.col("_rfnd_dt").isNotNull(),
            F.date_format(F.col("_rfnd_dt"), "yyyy-MM-dd")
        ).when(F.col("_cb_dt").isNotNull(),
            F.date_format(F.col("_cb_dt"), "yyyy-MM-dd")
        )
    )
    .withColumn("datetime_refunded_platform",
        F.coalesce(F.col("_rfnd_dt_platform_str"), F.col("_cb_dt_platform_str"))
    )
)

# ============================================================
# 17. CAMPOS BRL (Regra 9) — exchange_rate fixo do dia da Sale
# ============================================================
result = (
    result
    .withColumn("total_price",
        F.round(F.col("_total_price_usd") * F.col("exchange_rate"), 4))
    .withColumn("total_collected_brl",
        F.round(F.col("transactionamount") * F.col("exchange_rate"), 4))
    .withColumn("affiliate_amount",
        F.round(F.col("affiliateearnings") * F.col("exchange_rate"), 4))
    .withColumn("commission_brl",
        F.round(F.col("commission_usd") * F.col("exchange_rate"), 4))
    .withColumn("account_amount_event",
        F.round(
            F.coalesce(F.col("_last_event_amount"), F.lit(0.0)) *
            F.col("exchange_rate"), 4
        ))
    .withColumn("product_cost",
        F.round(F.col("product_cost_usd") * F.col("exchange_rate"), 4))
    .withColumn("taxes",
        F.round(F.col("platformfee") * F.col("exchange_rate"), 4))
    .withColumn("total_refund",
        F.round(F.col("total_refund_usd") * F.col("exchange_rate"), 4))
    .withColumn("refund_fee",
        F.round(F.col("refund_fee_usd") * F.col("exchange_rate"), 4))
    .withColumn("chargeback_fee",
        F.round(F.col("chargeback_fee_usd") * F.col("exchange_rate"), 4))
)

# Garantia de regra: Fee só no transaction_id STANDARD (sem sufixo -B).
# Em caso de qualquer resíduo de join/partição, zera fee para bumps.
result = (
    result
    .withColumn(
        "chargeback_fee_usd",
        F.when(F.col("transaction_id").rlike(r"-B\d+$"), F.lit(0.0)).otherwise(F.col("chargeback_fee_usd"))
    )
    .withColumn(
        "refund_fee_usd",
        F.when(F.col("transaction_id").rlike(r"-B\d+$"), F.lit(0.0)).otherwise(F.col("refund_fee_usd"))
    )
    .withColumn(
        "chargeback_fee",
        F.when(F.col("transaction_id").rlike(r"-B\d+$"), F.lit(0.0)).otherwise(F.col("chargeback_fee"))
    )
    .withColumn(
        "refund_fee",
        F.when(F.col("transaction_id").rlike(r"-B\d+$"), F.lit(0.0)).otherwise(F.col("refund_fee"))
    )
)

# Garantia final: 1 linha por transaction_id na Silver.
_w_final_tid = Window.partitionBy("transaction_id").orderBy(
    F.col("_sale_dt").desc_nulls_last(),
    F.col("_rfnd_dt").desc_nulls_last(),
    F.col("_cb_dt").desc_nulls_last(),
    F.col("dt_proc").desc_nulls_last(),
)
result = (
    result
    .withColumn("_rn_tid", F.row_number().over(_w_final_tid))
    .filter(F.col("_rn_tid") == 1)
    .drop("_rn_tid")
)

# ============================================================
# 18. SCHEMA FINAL — alinhado 100% com clickbank_physical_new MySQL
# ============================================================
spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")
print(f"[INFO] Modo de escrita: dynamic overwrite (partições não tocadas preservadas automaticamente)")

# Pré-computar account_amount_event_usd para reutilizar duas vezes no select
# sem repetir a expressão (_last_event_amount está no resultado do JOIN 4b)
result = result.withColumn("account_amount_event_usd",
    F.col("_last_event_amount").cast(DecimalType(10, 2))
)

silver = result.select(
    # Identificação / Status
    F.col("transaction_id").cast("string"),
    F.col("payment_status").cast("string"),
    # Cliente
    title_case_name(
        F.col("billingcustomerfirstname"), F.col("billingcustomerlastname")
    ).alias("client_name"),
    F.lower(F.coalesce(F.col("billingcustomeremail"), F.col("shippingcustomeremail"))).cast("string").alias("client_email"),
    # client_phone: regexp_replace([^0-9]) é mais robusto que cast(Decimal) para strings com "+"
    # A Bronze nova retorna phone como "+15306809279" — o cast(Decimal) pode retornar null em
    # alguns ambientes Spark quando o sinal "+" está presente. coalesce billing → shipping.
    F.when(
        F.regexp_replace(
            F.coalesce(F.col("billingcustomerphone"), F.col("shippingcustomerphone"), F.lit("")),
            r"[^0-9]", ""
        ) != F.lit(""),
        F.regexp_replace(
            F.coalesce(F.col("billingcustomerphone"), F.col("shippingcustomerphone"), F.lit("")),
            r"[^0-9]", ""
        )
    ).alias("client_phone"),
    # client_zip/country/state/city: coalesce billing → shipping
    # Billing é preferred (endereço do cartão). Shipping como fallback para linhas de UPSELL
    # onde o campo billing pode ser null mesmo a API retornando os dados no campo shipping.
    F.coalesce(F.col("billingpostalcode"), F.col("shippingpostalcode")).cast("string").alias("client_zip"),
    F.coalesce(F.col("billingcountry"),    F.col("shippingcountry")).cast("string").alias("client_country"),
    F.coalesce(F.col("billingstate"),      F.col("shippingstate")).cast("string").alias("client_state"),
    F.coalesce(F.col("billingcity"),       F.col("shippingcity")).cast("string").alias("client_city"),
    # client_street: API ClickBank não fornece rua/logradouro — null por design
    F.lit(None).cast("string").alias("client_street"),
    # Produto
    F.col("product_name").cast("string"),
    F.col("productitemnumber").cast("string").alias("product_sku"),
    F.col("product_cost").cast(DecimalType(12, 4)),
    F.col("product_cost_usd").cast(DecimalType(10, 2)),
    # quantity: extraída do SKU (API sempre envia itemquantity=1)
    F.col("_effective_qty").cast("int").alias("quantity"),
    F.col("offer_name").cast("string"),
    F.col("sales_type").cast("string"),
    F.col("coupon_code").cast("string"),
    # Funil
    F.col("upsellparentreceipt").cast("string").alias("upsell_parent_receipt"),
    # Financeiro
    F.col("total_price").cast(DecimalType(12, 4)),
    F.col("_total_price_usd").cast(DecimalType(10, 2)).alias("total_price_usd"),
    F.col("transactionamount").cast(DecimalType(10, 2)).alias("total_collected_usd"),
    F.col("taxes").cast(DecimalType(12, 4)),
    F.col("platformfee").cast(DecimalType(10, 2)).alias("taxes_usd"),
    F.col("customertax").cast(DecimalType(10, 2)).alias("iva_usd"),
    F.col("exchange_rate").cast(DecimalType(10, 4)),
    F.col("commission_brl").cast(DecimalType(12, 4)).alias("commission"),
    F.col("commission_usd").cast(DecimalType(10, 2)),
    # account_amount_event_usd aparece duas vezes: como auditoria e como alias MySQL
    F.col("account_amount_event_usd").cast(DecimalType(10, 2)).alias("account_amount_event_usd"),
    F.col("affiliate_amount").cast(DecimalType(12, 4)),
    F.col("affiliateearnings").cast(DecimalType(10, 2)).alias("affiliate_amount_usd"),
    F.col("total_refund").cast(DecimalType(12, 4)),
    F.col("total_refund_usd").cast(DecimalType(10, 2)),
    F.col("refund_fee").cast(DecimalType(12, 4)),
    F.col("refund_fee_usd").cast(DecimalType(10, 2)),
    F.col("chargeback_fee").cast(DecimalType(12, 4)),
    F.col("chargeback_fee_usd").cast(DecimalType(10, 2)),
    # Vendor / Afiliado
    F.lower(F.col("primaryaffiliate")).cast("string").alias("affiliate_name"),
    F.col("is_house_traffic").cast("int"),
    F.lower(F.col("salesaccount")).cast("string").alias("vendor_name"),
    # Datas GMT-3
    F.col("created_at_date").cast("string"),
    F.col("created_at_hour").cast("string"),
    F.col("datetime_platform").cast("string"),
    F.col("date_refunded").cast("string"),
    F.col("datetime_refunded_platform").cast("string"),
    # UTMs / Tracking
    F.col("utm_content").cast("string"),
    F.col("utm_source").cast("string"),
    F.col("utm_medium").cast("string"),
    F.col("utm_term").cast("string"),
    F.col("utm_campaign").cast("string"),
    F.col("src").cast("string"),
    # Controle
    F.lit("clickbank").cast("string").alias("platform"),
    F.col("_sale_dt").cast("timestamp").alias("created_at"),
    F.current_timestamp().alias("updated_at"),
    F.col("_type").cast("string").alias("transaction_type"),
    # Aliases MySQL finais para account_amount
    F.col("account_amount_event_usd").cast(DecimalType(10, 2)).alias("account_amount_usd"),
    F.col("account_amount_event").cast(DecimalType(12, 4)).alias("account_amount"),
    # Partição S3
    F.coalesce(
        F.to_date(F.col("created_at_date")),
        F.current_date()
    ).cast("date").alias("dt_proc"),
)

print(f"[INFO] Silver do lote novo: {silver.count()} linhas antes do merge com histórico")

# ============================================================
# MERGE COM HISTÓRICO — manter TODO histórico em TODAS execuções
# ============================================================
# Regra: ler existing_silver (se existir) + UNION com novo batch
# Isso garante que dados históricos nunca sejam perdidos.
# Depois, dedup final remove qualquer duplicata.

silver_table_name = "tb_gex_clickbank_physical_new"
try:
    existing_silver = read_silver_current(silver_table_name)
    existing_count = existing_silver.count()
    print(f"[INFO] Histórico encontrado na Silver: {existing_count} linhas")

    # UNION: combinar existing + new
    silver = existing_silver.unionByName(silver, allowMissingColumns=True)
    print(f"[INFO] UNION histórico + novo: {silver.count()} linhas (antes dedup)")

except Exception as ex_read:
    msg = str(ex_read)
    is_table_missing = ("EntityNotFoundException" in msg) or ("Entity Not Found" in msg)
    if is_table_missing and ALLOW_BOOTSTRAP_WITHOUT_HISTORY:
        print(
            "[WARN] Bootstrap explícito habilitado sem histórico Silver. "
            "Prosseguindo apenas com lote novo."
        )
    else:
        raise RuntimeError(
            "Falha ao carregar histórico Silver. Execução abortada para proteger o histórico consolidado. "
            "Para bootstrap explícito sem histórico, use --ALLOW_BOOTSTRAP_WITHOUT_HISTORY=true. "
            f"Detalhe: {msg[:500]}"
        )

# Preserva a data da venda principal ao combinar histórico + lote novo.
# Se um Refund/Chargeback chegar sem Sale no lookback (orphan), não deve
# sobrescrever created_at_date já consolidado pela Sale no histórico.
_w_sale_anchor = Window.partitionBy("transaction_id")
silver = (
    silver
    .withColumn(
        "_sale_created_at_date_hist",
        F.max(
            F.when(F.col("total_collected_usd").isNotNull(), F.col("created_at_date"))
        ).over(_w_sale_anchor)
    )
    .withColumn(
        "created_at_date",
        F.coalesce(F.col("_sale_created_at_date_hist"), F.col("created_at_date"))
    )
    .drop("_sale_created_at_date_hist")
)

# Proteção de merge incremental: quando a janela curta (ex.: 14 dias) trouxer
# apenas eventos parciais (ex.: só Chargeback), preservar campos consolidados
# de venda e evitar regressão de acumulados já materializados no histórico.
_w_tid_merge = Window.partitionBy("transaction_id")
silver = (
    silver
    .withColumn(
        "_sale_total_collected_usd_hist",
        F.max(F.when(F.col("total_collected_usd").isNotNull(), F.col("total_collected_usd"))).over(_w_tid_merge)
    )
    .withColumn(
        "_sale_total_price_usd_hist",
        F.max(F.when(F.col("total_collected_usd").isNotNull(), F.col("total_price_usd"))).over(_w_tid_merge)
    )
    .withColumn(
        "_sale_total_price_hist",
        F.max(F.when(F.col("total_collected_usd").isNotNull(), F.col("total_price"))).over(_w_tid_merge)
    )
    .withColumn(
        "_sale_exchange_rate_hist",
        F.max(F.when(F.col("total_collected_usd").isNotNull(), F.col("exchange_rate"))).over(_w_tid_merge)
    )
    .withColumn(
        "_sale_created_at_hist",
        F.max(F.when(F.col("total_collected_usd").isNotNull(), F.col("created_at"))).over(_w_tid_merge)
    )
    .withColumn(
        "_sale_created_at_hour_hist",
        F.max(F.when(F.col("total_collected_usd").isNotNull(), F.col("created_at_hour"))).over(_w_tid_merge)
    )
    .withColumn(
        "_sale_datetime_platform_hist",
        F.max(F.when(F.col("total_collected_usd").isNotNull(), F.col("datetime_platform"))).over(_w_tid_merge)
    )
    .withColumn("total_collected_usd", F.coalesce(F.col("_sale_total_collected_usd_hist"), F.col("total_collected_usd")))
    .withColumn("total_price_usd", F.coalesce(F.col("_sale_total_price_usd_hist"), F.col("total_price_usd")))
    .withColumn("total_price", F.coalesce(F.col("_sale_total_price_hist"), F.col("total_price")))
    .withColumn("exchange_rate", F.coalesce(F.col("_sale_exchange_rate_hist"), F.col("exchange_rate")))
    .withColumn("created_at", F.coalesce(F.col("_sale_created_at_hist"), F.col("created_at")))
    .withColumn("created_at_hour", F.coalesce(F.col("_sale_created_at_hour_hist"), F.col("created_at_hour")))
    .withColumn("datetime_platform", F.coalesce(F.col("_sale_datetime_platform_hist"), F.col("datetime_platform")))
    .withColumn("_max_total_refund_usd_hist", F.max(F.col("total_refund_usd")).over(_w_tid_merge))
    .withColumn("_max_total_refund_hist", F.max(F.col("total_refund")).over(_w_tid_merge))
    .withColumn("_max_chargeback_fee_usd_hist", F.max(F.col("chargeback_fee_usd")).over(_w_tid_merge))
    .withColumn("_max_chargeback_fee_hist", F.max(F.col("chargeback_fee")).over(_w_tid_merge))
    .withColumn("_max_refund_fee_usd_hist", F.max(F.col("refund_fee_usd")).over(_w_tid_merge))
    .withColumn("_max_refund_fee_hist", F.max(F.col("refund_fee")).over(_w_tid_merge))
    .withColumn("total_refund_usd", F.coalesce(F.col("_max_total_refund_usd_hist"), F.col("total_refund_usd")))
    .withColumn("total_refund", F.coalesce(F.col("_max_total_refund_hist"), F.col("total_refund")))
    .withColumn("chargeback_fee_usd", F.coalesce(F.col("_max_chargeback_fee_usd_hist"), F.col("chargeback_fee_usd")))
    .withColumn("chargeback_fee", F.coalesce(F.col("_max_chargeback_fee_hist"), F.col("chargeback_fee")))
    .withColumn("refund_fee_usd", F.coalesce(F.col("_max_refund_fee_usd_hist"), F.col("refund_fee_usd")))
    .withColumn("refund_fee", F.coalesce(F.col("_max_refund_fee_hist"), F.col("refund_fee")))
    .drop(
        "_sale_total_collected_usd_hist",
        "_sale_total_price_usd_hist",
        "_sale_total_price_hist",
        "_sale_exchange_rate_hist",
        "_sale_created_at_hist",
        "_sale_created_at_hour_hist",
        "_sale_datetime_platform_hist",
        "_max_total_refund_usd_hist",
        "_max_total_refund_hist",
        "_max_chargeback_fee_usd_hist",
        "_max_chargeback_fee_hist",
        "_max_refund_fee_usd_hist",
        "_max_refund_fee_hist",
    )
)

# ============================================================
# Dedup final OBRIGATÓRIA — remove duplicatas entre execuções
# Garante idempotência: mesma execução 2x = mesmo resultado
# ============================================================
_w_dedup_final = Window.partitionBy("transaction_id").orderBy(
    F.col("updated_at").desc_nulls_last(),
    F.col("dt_proc").desc_nulls_last(),
    F.col("created_at").desc_nulls_last(),
)

silver = (
    silver
    .withColumn("_rn_dedup_final", F.row_number().over(_w_dedup_final))
    .filter(F.col("_rn_dedup_final") == 1)
    .drop("_rn_dedup_final")
)

print(f"[INFO] Dedup final aplicado: {silver.count()} linhas garantidas por transaction_id")

silver.write.mode("overwrite").partitionBy("dt_proc").parquet(OUTPUT_PATH)

print(f"Silver escrita em {OUTPUT_PATH}")
print(f"[DEBUG] SILVER COUNT FINAL: {silver.count()} linhas gravadas")

SILVER_TABLE_NAME = "tb_gex_clickbank_physical_new"
written_partitions = [
    row["dt_proc"]
    for row in silver.select(F.col("dt_proc").cast("string").alias("dt_proc")).distinct().collect()
    if row["dt_proc"] is not None and row["dt_proc"] != ""
]

if not written_partitions:
    raise RuntimeError("Nenhuma particao dt_proc foi produzida para registrar no Glue Catalog.")

written_partitions = sorted(set(written_partitions))
print(f"[INFO] Particoes dt_proc escritas: {written_partitions}")

glue_client = boto3.client("glue")
table_resp = glue_client.get_table(DatabaseName=TARGET_DB, Name=SILVER_TABLE_NAME)
table_obj = table_resp["Table"]
table_sd = table_obj["StorageDescriptor"]

allowed_sd_keys = [
    "Columns",
    "Location",
    "InputFormat",
    "OutputFormat",
    "Compressed",
    "NumberOfBuckets",
    "SerdeInfo",
    "BucketColumns",
    "SortColumns",
    "Parameters",
    "StoredAsSubDirectories",
    "SchemaReference",
    "SkewedInfo",
]

base_sd = {k: copy.deepcopy(v) for k, v in table_sd.items() if k in allowed_sd_keys}

created_count = 0
exists_count = 0

for dt in written_partitions:
    part_location = f"{OUTPUT_PATH}dt_proc={dt}/"
    part_sd = copy.deepcopy(base_sd)
    part_sd["Location"] = part_location

    partition_input = {
        "Values": [dt],
        "StorageDescriptor": part_sd,
    }

    try:
        glue_client.create_partition(
            DatabaseName=TARGET_DB,
            TableName=SILVER_TABLE_NAME,
            PartitionInput=partition_input,
        )
        created_count += 1
        print(f"[INFO] Particao criada no Catalog: dt_proc={dt}")
    except (glue_client.exceptions.AlreadyExistsException, ClientError) as ex:
        code = getattr(ex, "response", {}).get("Error", {}).get("Code", "")
        if isinstance(ex, glue_client.exceptions.AlreadyExistsException) or code == "AlreadyExistsException":
            glue_client.update_partition(
                DatabaseName=TARGET_DB,
                TableName=SILVER_TABLE_NAME,
                PartitionValueList=[dt],
                PartitionInput=partition_input,
            )
            exists_count += 1
            print(f"[INFO] Particao atualizada no Catalog: dt_proc={dt}")
        else:
            raise

print(
    "[INFO] Registro de particoes concluido no Glue Catalog | "
    f"criadas={created_count} | existentes={exists_count} | total={len(written_partitions)}"
)

job.commit()
````

## Relacionados
[[00-Data-Lake]]
