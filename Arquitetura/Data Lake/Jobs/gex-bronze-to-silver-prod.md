---
tipo: job-glue
ambiente: prod
fluxo: bronze-to-silver
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-12 09:05
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-bronze-to-silver-prod

> Glue ETL · fluxo **bronze-to-silver** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x10 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/bronze_to_silver_clickbank.py` |
| Criado | 2026-03-25 09:47:36.900000-03:00 |
| Modificado | 2026-05-14 10:56:24.386000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--ALLOW_BOOTSTRAP_WITHOUT_HISTORY` | false |
| `--LOOKBACK_DAYS` | 14 |
| `--MIN_PARTITIONS_REQUIRED` | 2 |
| `--SOURCE_DATABASE` | gex_db_prod_bronze |
| `--TARGET_DATABASE` | gex_db_prod_silver |
| `--source_bucket` | gex-datalake-bronze-prod |
| `--target_bucket` | gex-datalake-silver-prod |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-12 09:05 | SUCCEEDED | 38m55s | — |
| 2026-06-12 07:05 | SUCCEEDED | 36m2s | — |
| 2026-06-12 05:05 | SUCCEEDED | 36m45s | — |
| 2026-06-12 03:05 | SUCCEEDED | 37m52s | — |
| 2026-06-12 01:05 | SUCCEEDED | 35m54s | — |
| 2026-06-11 23:05 | SUCCEEDED | 37m2s | — |
| 2026-06-11 21:05 | SUCCEEDED | 40m58s | — |
| 2026-06-11 19:05 | SUCCEEDED | 36m30s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/bronze_to_silver_clickbank.py` — baixado do S3 (read-only).

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
import urllib.parse
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
sc          = SparkContext()
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

BRONZE_PATH = f"s3://{SOURCE_BUCKET}/clickbank/clickbank_vendas_new/"
df_raw = (
    spark.read
    .schema(_BRONZE_SCHEMA)
    .option("recursiveFileLookup", "true")
    .parquet(BRONZE_PATH)
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

# 4c. Refund / Chargeback — total_refund_usd deve incluir ambos os tipos
#     Chargeback também representa reembolso ao cliente e não pode deixar
#     total_refund_usd nulo.
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
        F.col("offer_name_locked").alias("_lk_offer_name_locked"),
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
# 11.5. HOUSE TRAFFIC OFFER NAME ENRICHMENT (cenários 2, 3 e 4)
#       Regras:
#       - replace('Affiliate Marketing', traffic_source)
#       - se multi-segmento (contém '] ['): inserir [Gestor de Tráfego: X]
#         antes do último segmento
#       - senão: concatenar [Gestor de Tráfego: X] no final
#       Aplica somente quando:
#       is_house_traffic=true, _lk_offer_name_locked=true,
#       offer_name não vazio, traffic_source não nulo, traffic_manager não nulo
# ============================================================
def _build_house_offer_name(offer_col: str, traffic_source_col: str, traffic_manager_col: str) -> F.Column:
    replaced = F.expr(f"replace({offer_col}, 'Affiliate Marketing', {traffic_source_col})")
    has_multi_segment = F.instr(replaced, "] [") > 0
    prefix = F.regexp_extract(replaced, r"^(.*)\] \[(.*)$", 1)
    last_segment = F.regexp_extract(replaced, r"^(.*)\] \[(.*)$", 2)
    with_manager_before_last = F.concat(
        prefix,
        F.lit("] [Gestor de Tráfego: "),
        F.col(traffic_manager_col),
        F.lit("] ["),
        last_segment,
    )
    with_manager_at_end = F.concat(
        replaced,
        F.lit(" [Gestor de Tráfego: "),
        F.col(traffic_manager_col),
        F.lit("]"),
    )
    return F.when(has_multi_segment, with_manager_before_last).otherwise(with_manager_at_end)


_house_offer_condition = (
    (F.col("is_house_traffic") == F.lit(True)) &
    (F.coalesce(F.col("_lk_offer_name_locked"), F.lit(False)) == F.lit(True)) &
    F.col("offer_name").isNotNull() &
    (F.trim(F.col("offer_name")) != "") &
    F.col("traffic_source").isNotNull() &
    F.col("traffic_manager").isNotNull()
)

result = (
    result
    .withColumn(
        "offer_name",
        F.when(
            _house_offer_condition,
            _build_house_offer_name("offer_name", "traffic_source", "traffic_manager")
        ).otherwise(F.col("offer_name"))
    )
    .drop("_lk_offer_name_locked")
)

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

# ============================================================
# 19. UPSERT COM LEITURA DA SILVER EXISTENTE
#     Preservação de campos imutáveis (taxes_usd, iva_usd, etc.)
#     que nunca devem ser sobrescritos por eventos posteriores (Refund/CBK/Fee)
# ============================================================

# Tentar ler Silver existente — primeira execução pode não ter dados ainda
current_silver = None
try:
    current_silver = spark.read.parquet(OUTPUT_PATH).cache()
    print("[INFO] Silver existente lida com sucesso")
except Exception as e:
    print(f"[INFO] Primeira execução ou Silver vazia — criando nova: {str(e)}")

if current_silver is not None and len(current_silver.take(1)) > 0:
    # ================================================================
    # Silver existente encontrada — aplicar UPSERT com COALESCE
    # ================================================================

    # Chaves do batch atual: usadas para reduzir custo dos joins com histórico
    batch_tids = silver.select("transaction_id").distinct().cache()
    
    # Extrair chave primária + campos imutáveis da Silver existente com alias
    # Para evitar conflito de nomes no join, renomear com sufixo _silver_prev
    current_immutables = (
        current_silver
        .select(
            F.col("transaction_id"),
            F.col("created_at").alias("created_at_prev"),
            F.col("taxes_usd").alias("taxes_usd_prev"),
            F.col("iva_usd").alias("iva_usd_prev"),
            F.col("total_price_usd").alias("total_price_usd_prev"),
            F.col("total_collected_usd").alias("total_collected_usd_prev"),
            F.col("affiliate_amount_usd").alias("affiliate_amount_usd_prev"),
            F.col("exchange_rate").alias("exchange_rate_prev"),
            F.col("total_price").alias("total_price_prev"),
            F.col("total_collected_brl").alias("total_collected_brl_prev"),
            F.col("affiliate_amount").alias("affiliate_amount_prev"),
            F.col("taxes").alias("taxes_prev"),
        )
        .join(F.broadcast(batch_tids), on="transaction_id", how="inner")
        .dropDuplicates(["transaction_id"])
    )
    
    # Fazer COALESCE para campos imutáveis no batch atual
    # Regra: se o batch trouxe NULL (orphan) mas Silver tem valor, usar Silver anterior
    silver_with_immutables = (
        silver
        .join(current_immutables, on="transaction_id", how="left")
        .withColumn("taxes_usd",
            F.coalesce(F.col("taxes_usd"), F.col("taxes_usd_prev"))
        )
        .withColumn("iva_usd",
            F.coalesce(F.col("iva_usd"), F.col("iva_usd_prev"))
        )
        .withColumn("total_price_usd",
            F.coalesce(F.col("total_price_usd"), F.col("total_price_usd_prev"))
        )
        .withColumn("total_collected_usd",
            F.coalesce(F.col("total_collected_usd"), F.col("total_collected_usd_prev"))
        )
        .withColumn("affiliate_amount_usd",
            F.coalesce(F.col("affiliate_amount_usd"), F.col("affiliate_amount_usd_prev"))
        )
        .withColumn("exchange_rate",
            F.coalesce(F.col("exchange_rate"), F.col("exchange_rate_prev"))
        )
        .withColumn("total_price",
            F.coalesce(F.col("total_price"), F.col("total_price_prev"))
        )
        .withColumn("total_collected_brl",
            F.coalesce(F.col("total_collected_brl"), F.col("total_collected_brl_prev"))
        )
        .withColumn("affiliate_amount",
            F.coalesce(F.col("affiliate_amount"), F.col("affiliate_amount_prev"))
        )
        .withColumn("taxes",
            F.coalesce(F.col("taxes"), F.col("taxes_prev"))
        )
        .withColumn("created_at",
            # Preservar created_at original se existir na Silver anterior
            F.coalesce(F.col("created_at_prev"), F.col("created_at"))
        )
        .withColumn("updated_at", F.current_timestamp())
        .drop(
            "created_at_prev",
            "taxes_usd_prev",
            "iva_usd_prev",
            "total_price_usd_prev",
            "total_collected_usd_prev",
            "affiliate_amount_usd_prev",
            "exchange_rate_prev",
            "total_price_prev",
            "total_collected_brl_prev",
            "affiliate_amount_prev",
            "taxes_prev",
        )
    )
    
    # Linhas da Silver não presentes no batch atual — preservar integralmente
    untouched_silver = (
        current_silver
        .join(F.broadcast(batch_tids), on="transaction_id", how="left_anti")
    )
    
    print("[INFO] UPSERT: batch enriquecido com campos imutáveis da Silver")
    print("[INFO] UPSERT: linhas históricas não tocadas preservadas")
    
    # Fazer UNION preservando schema completo
    upserted = silver_with_immutables.unionByName(untouched_silver, allowMissingColumns=True)
    print("[INFO] UPSERT final consolidado")

    batch_tids.unpersist()
    current_silver.unpersist()
    
else:
    # ================================================================
    # Primeira execução ou Silver vazia — escrever batch conforme está
    # ================================================================
    print("[INFO] Primeira execução — escrevendo batch diretamente")
    upserted = silver

# Campo de controle do pipeline (GMT-3): atualizado a cada execução do job,
# sem sobrescrever/redefinir os campos já existentes created_at e updated_at.
pipeline_updated_at_expr = F.expr(
    "from_utc_timestamp(current_timestamp(), 'America/Sao_Paulo')"
)
upserted = upserted.withColumn("pipeline_updated_at", pipeline_updated_at_expr)

# Escrever resultado final com overwrite dinâmico
upserted.write.mode("overwrite").partitionBy("dt_proc").parquet(OUTPUT_PATH)

print(f"[INFO] Silver FINAL escrita em {OUTPUT_PATH}")
print("[INFO] Escrita concluída")

job.commit()
````

## Relacionados
[[00-Data-Lake]]
