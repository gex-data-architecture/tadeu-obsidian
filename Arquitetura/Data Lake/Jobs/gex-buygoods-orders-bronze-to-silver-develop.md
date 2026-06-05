---
tipo: job-glue
ambiente: develop
fluxo: bronze-to-silver
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: —
ultimo_estado: —
tags: [datalake, glue-job]
---

# gex-buygoods-orders-bronze-to-silver-develop

> Glue ETL · fluxo **bronze-to-silver** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x4 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-develop` |
| Script | `s3://gex-datalake-bronze-develop/scripts/buygoods_orders_bronze_to_silver.py` |
| Criado | 2026-06-01 13:14:34.217000-03:00 |
| Modificado | 2026-06-01 13:14:34.217000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--DEFAULT_EXCHANGE_RATE` | 5.10 |
| `--DEFAULT_UNIT_COST_USD` | 5.00 |
| `--REF_DATABASE` | gex_db_develop_bronze |
| `--SOURCE_DATABASE` | gex_db_develop_bronze |
| `--SOURCE_PATH` | s3://gex-datalake-bronze-develop/buygoods_orders/raw/ |
| `--SOURCE_TABLE` | buygoods_orders |
| `--TARGET_DATABASE` | gex_db_develop_silver |
| `--TARGET_TABLE` | buygoods_orders_dev |
| `--target_bucket` | gex-datalake-silver-develop |

## Últimas execuções

> Sem histórico de execuções (job nunca rodou ou sem acesso ao histórico).

## Script

> Fonte: `s3://gex-datalake-bronze-develop/scripts/buygoods_orders_bronze_to_silver.py` — baixado do S3 (read-only).

````python
"""
Glue Job: buygoods_bronze_to_silver (develop)

Constroi a Silver buygoods_orders a partir da Bronze buygoods_orders extraida
direto da API da BuyGoods (gex_db_develop_bronze.buygoods_orders).

Diferencas em relacao ao job de prod (bronze-to-silver-buygoods-prod):
  - A bronze nova ja vem com 1 linha por order_id_global no ESTADO FINAL
    (action_type in {neworder, refund, cancel, chargeback}). Nao existe mais
    logica de eventos/agrupamento (sale_snapshot / agg_events / last_event).
  - Campos lidos como colunas reais (nao querystring/payload_map).
  - Inclui o campo cancel_reason.
  - total_price_usd = total_amount_charged - taxes.
  - datetime_refunded_platform = date_refunded (SEM mudanca de fuso).
  - date_refunded = date_refunded (COM mudanca de fuso GMT-4 -> GMT-3).
  - subid* renomeados para utm_* (utm_source/content/campaign/term/medium).
  - created_at / pipeline_updated_at derivados de _extracted_at; dt_proc = date(_extracted_at);
    updated_at = horario desta rodada.
  - Tabelas de referencia (products, internal_affiliates, exchange_rates,
    general_product_costs) lidas de REF_DATABASE (gex_db_prod_bronze).

UPSERT por transaction_id preservando campos imutaveis da Silver existente.
"""

import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import Window
from pyspark.sql.types import DoubleType


args = getResolvedOptions(
    sys.argv,
    ["JOB_NAME", "SOURCE_DATABASE", "TARGET_DATABASE", "target_bucket"],
)


def get_optional_arg(name: str, default: str) -> str:
    token = f"--{name}"
    if token in sys.argv:
        idx = sys.argv.index(token)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return default


SOURCE_TABLE = get_optional_arg("SOURCE_TABLE", "buygoods_orders")
# A bronze usa partition projection (Athena) -> o catalogo Glue NAO tem particoes
# registradas; por isso lemos direto do S3 (Spark descobre acct_id/year_month).
SOURCE_PATH = get_optional_arg("SOURCE_PATH", "s3://api-buygoods-teste-tadeu/bronze/buygoods/orders/")
TARGET_TABLE = get_optional_arg("TARGET_TABLE", "buygoods_orders")
REF_DATABASE = get_optional_arg("REF_DATABASE", "gex_db_prod_bronze")
PRODUCTS_TABLE = get_optional_arg("PRODUCTS_TABLE", "tb_bronze_buygoods_products")
INTERNAL_AFFILIATES_TABLE = get_optional_arg("INTERNAL_AFFILIATES_TABLE", "tb_bronze_buygoods_internal_affiliates")
EXCHANGE_RATES_TABLE = get_optional_arg("EXCHANGE_RATES_TABLE", "tb_bronze_exchange_rates")
PRODUCT_COSTS_TABLE = get_optional_arg("PRODUCT_COSTS_TABLE", "tb_bronze_general_product_costs")
DEFAULT_EXCHANGE_RATE = float(get_optional_arg("DEFAULT_EXCHANGE_RATE", "5.10"))
DEFAULT_UNIT_COST_USD = float(get_optional_arg("DEFAULT_UNIT_COST_USD", "5.00"))


sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
spark.conf.set("spark.sql.session.timeZone", "America/Sao_Paulo")

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

SOURCE_DB = args["SOURCE_DATABASE"]
TARGET_DB = args["TARGET_DATABASE"]
OUTPUT_PATH = f"s3://{args['target_bucket']}/{TARGET_TABLE}/"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def try_read_table(database: str, table_name: str) -> DataFrame:
    try:
        df = glueContext.create_dynamic_frame.from_catalog(
            database=database, table_name=table_name,
        ).toDF()
        return df.toDF(*[c.lower() for c in df.columns])
    except Exception as exc:
        print(f"[WARN] Nao foi possivel ler {database}.{table_name}: {exc}")
        return spark.createDataFrame([], "dummy string").drop("dummy")


def parse_money(col: F.Column) -> F.Column:
    cleaned = F.regexp_replace(F.coalesce(col, F.lit("")), r"[^0-9.\-]", "")
    return F.when(cleaned == "", None).otherwise(cleaned.cast(DoubleType()))


def parse_bg_datetime(col: F.Column) -> F.Column:
    return F.to_timestamp(F.trim(col), "yyyy-MM-dd HH:mm:ss")


def to_gmt3_from_gmt4(col: F.Column) -> F.Column:
    return col + F.expr("INTERVAL 1 HOUR")


def dec2(col: F.Column) -> F.Column:
    return F.round(col, 2).cast("decimal(10,2)")


def dec4(col: F.Column) -> F.Column:
    return F.round(col, 4).cast("decimal(12,4)")


def has_col(df: DataFrame, name: str) -> bool:
    return name in df.columns


def opt(df: DataFrame, name: str) -> F.Column:
    return F.col(name) if name in df.columns else F.lit(None)


# --------------------------------------------------------------------------- #
# 1) Bronze (1 linha por order_id_global, estado final)
#    Lida direto do S3 (partition projection -> sem particoes no catalogo).
# --------------------------------------------------------------------------- #
try:
    bronze = spark.read.parquet(SOURCE_PATH)
    bronze = bronze.toDF(*[c.lower() for c in bronze.columns])
    print(f"[INFO] Bronze lida de {SOURCE_PATH}")
except Exception as e:
    print(f"[INFO] Bronze inacessivel/vazia em {SOURCE_PATH}: {str(e)}")
    job.commit()
    sys.exit(0)

if len(bronze.take(1)) == 0:
    print("[INFO] Bronze vazia. Nada a processar.")
    job.commit()
    sys.exit(0)

# Filtros base: transaction_id valido e descarta compras de teste
bronze = (
    bronze
    .withColumn("transaction_id", F.trim(F.col("order_id_global")))
    .filter(F.col("transaction_id").isNotNull() & (F.col("transaction_id") != ""))
    .filter(F.coalesce(F.col("is_test"), F.lit("0")) != "1")
    # descarta pedidos cancelados (action_type = cancel) a pedido
    .filter(F.lower(F.trim(F.coalesce(F.col("action_type"), F.lit("")))) != "cancel")
)

# Garantia de unicidade: 1 linha por transaction_id (mais recente por _extracted_at)
w_dedup = Window.partitionBy("transaction_id").orderBy(
    F.col("_extracted_at").desc_nulls_last()
)
bronze = (
    bronze
    .withColumn("_rn", F.row_number().over(w_dedup))
    .filter(F.col("_rn") == 1)
    .drop("_rn")
)

# --------------------------------------------------------------------------- #
# 2) Normalizacao de campos da bronze
# --------------------------------------------------------------------------- #
b = (
    bronze
    .withColumn("action_type", F.lower(F.trim(F.col("action_type"))))
    # estado
    .withColumn("is_chargeback", F.col("action_type") == F.lit("chargeback"))
    .withColumn("is_refund", F.col("action_type") == F.lit("refund"))
    .withColumn("is_cancel", F.col("action_type") == F.lit("cancel"))
    # datas/fuso
    .withColumn("rr_createdate_ts", parse_bg_datetime(F.col("rr_createdate")))
    .withColumn("rr_createdate_ts_gmt3", to_gmt3_from_gmt4(F.col("rr_createdate_ts")))
    .withColumn("date_refunded_raw", F.trim(F.col("date_refunded")))
    .withColumn("date_refunded_ts", parse_bg_datetime(F.col("date_refunded")))
    .withColumn("extracted_at_ts", F.coalesce(
        F.to_timestamp(F.trim(F.col("_extracted_at"))),
        F.to_timestamp(F.regexp_replace(F.trim(F.col("_extracted_at")), "T", " ")),
    ))
    # monetarios (USD cru)
    .withColumn("total_clean_v", parse_money(F.col("total_clean")))
    .withColumn("total_amount_charged_v", parse_money(F.col("total_amount_charged")))
    .withColumn("taxes_v", parse_money(F.col("taxes")))
    .withColumn("merchant_commission_v", parse_money(F.col("merchant_commission")))
    .withColumn("aff_commission_v", parse_money(F.col("aff_commission")))
    .withColumn("refund_amount_v", parse_money(F.col("refund_amount")))
    .withColumn("chargeback_fee_usd_v", parse_money(F.col("chargeback_fee")))
    # ids / textos
    .withColumn("account_id_v", F.trim(F.col("account_id")))
    .withColumn("affiliate_id_v", F.trim(F.col("aff_id")))
    .withColumn("affiliate_name_v", F.regexp_replace(F.lower(F.trim(F.col("aff_name"))), r"\s+", " "))
    .withColumn("product_codename_v", F.trim(F.col("product_codename")))
    .withColumn("product_id_v", parse_money(F.col("product_id")).cast("int"))
    .withColumn("product_name_v", F.trim(F.coalesce(F.col("product_name"), F.col("product"))))
    .withColumn("product_sku_v", F.trim(F.col("sku")))
    .withColumn("cancel_reason_v", F.trim(F.col("cancel_reason")))
    # cliente (conforme de-para: campos base, nao shipping_*)
    .withColumn("client_name_v", F.initcap(F.trim(F.col("customer_name"))))
    .withColumn("client_email_v", F.lower(F.trim(F.col("customer_emailaddress"))))
    .withColumn("client_phone_v", F.regexp_replace(F.coalesce(F.col("customer_phone"), F.lit("")), r"[^0-9]", ""))
    .withColumn("client_zip_v", F.trim(F.col("zip")))
    .withColumn("client_country_v", F.upper(F.trim(F.coalesce(F.col("country_2letter"), F.col("country")))))
    .withColumn("client_state_v", F.trim(F.col("state")))
    .withColumn("client_city_v", F.trim(F.col("city")))
    .withColumn("client_street_v", F.trim(F.col("address")))
    # utm / upsell
    .withColumn("utm_source_v", F.trim(F.col("subid")))
    .withColumn("utm_content_v", F.trim(F.col("subid2")))
    .withColumn("utm_campaign_v", F.trim(F.col("subid3")))
    .withColumn("utm_term_v", F.trim(F.col("subid4")))
    .withColumn("utm_medium_v", F.trim(F.col("subid5")))
    .withColumn("upsell_parent_receipt_v", F.trim(F.col("sessid2")))
)

# --------------------------------------------------------------------------- #
# 3) Tabelas de referencia (REF_DATABASE = gex_db_prod_bronze)
# --------------------------------------------------------------------------- #
products_raw = try_read_table(REF_DATABASE, PRODUCTS_TABLE)
if products_raw.rdd.isEmpty():
    products = spark.createDataFrame([], "product_key string, account_key string, offer_name string")
else:
    products = (
        products_raw
        .withColumn("product_key", F.lower(F.trim(F.coalesce(
            opt(products_raw, "product_codename"),
            opt(products_raw, "product_id"),
            opt(products_raw, "base_sku"),
        ))))
        .withColumn("account_key", F.lower(F.trim(F.coalesce(
            opt(products_raw, "account_id"),
            opt(products_raw, "account_name"),
        ))))
        .withColumn("offer_name", F.trim(F.coalesce(
            opt(products_raw, "offer_name"),
            opt(products_raw, "product_name"),
        )))
        .select("product_key", "account_key", "offer_name")
        .where(F.col("product_key").isNotNull() & (F.col("product_key") != ""))
        .dropDuplicates(["product_key", "account_key"])
    )

internal_raw = try_read_table(REF_DATABASE, INTERNAL_AFFILIATES_TABLE)
if internal_raw.rdd.isEmpty():
    internal_aff = spark.createDataFrame([], "affiliate_name string, is_internal_flag int")
else:
    internal_aff = (
        internal_raw
        .withColumn("affiliate_name", F.regexp_replace(F.lower(F.trim(opt(internal_raw, "affiliate_name"))), r"\s+", " "))
        .withColumn("is_internal_flag", F.lit(1))
        .select("affiliate_name", "is_internal_flag")
        .where(F.col("affiliate_name").isNotNull() & (F.col("affiliate_name") != ""))
        .dropDuplicates(["affiliate_name"])
    )

rates_raw = try_read_table(REF_DATABASE, EXCHANGE_RATES_TABLE)
if rates_raw.rdd.isEmpty():
    rates = spark.createDataFrame([], "rate_date date, exchange_rate decimal(10,4)")
else:
    rates_tmp = rates_raw
    if has_col(rates_tmp, "source_currency"):
        rates_tmp = rates_tmp.where(
            (F.upper(F.trim(F.col("source_currency"))) == "USD")
            | F.col("source_currency").isNull()
        )
    if has_col(rates_tmp, "target_currency"):
        rates_tmp = rates_tmp.where(
            (F.upper(F.trim(F.col("target_currency"))) == "BRL")
            | F.col("target_currency").isNull()
        )
    rates = (
        rates_tmp
        .withColumn("rate_date", F.to_date(F.coalesce(
            opt(rates_tmp, "date"),
            opt(rates_tmp, "dt"),
            opt(rates_tmp, "transactiondate"),
        )))
        .withColumn("exchange_rate", F.coalesce(
            opt(rates_tmp, "exchange_rate"),
            opt(rates_tmp, "rate"),
        ).cast("decimal(10,4)"))
        .select("rate_date", "exchange_rate")
        .where(F.col("rate_date").isNotNull() & F.col("exchange_rate").isNotNull())
        .dropDuplicates(["rate_date"])
    )

costs_raw = try_read_table(REF_DATABASE, PRODUCT_COSTS_TABLE)
unit_cost_value = DEFAULT_UNIT_COST_USD
if not costs_raw.rdd.isEmpty():
    costs = (
        costs_raw
        .withColumn("valid_from", F.to_date(F.coalesce(
            opt(costs_raw, "valid_from"), opt(costs_raw, "start_date"),
        )))
        .withColumn("unit_cost_usd", F.coalesce(
            opt(costs_raw, "unit_cost_usd"),
            opt(costs_raw, "unit_cost"),
            opt(costs_raw, "cost_usd"),
        ).cast("decimal(10,2)"))
        .where(F.col("unit_cost_usd").isNotNull())
    )
    first_cost = costs.orderBy(F.col("valid_from").desc_nulls_last()).first()
    if first_cost and first_cost["unit_cost_usd"] is not None:
        unit_cost_value = float(first_cost["unit_cost_usd"])
print(f"[INFO] unit_cost_usd fixo aplicado: {unit_cost_value}")

# --------------------------------------------------------------------------- #
# 4) Enriquecimento (joins) + derivacoes
# --------------------------------------------------------------------------- #
enriched = (
    b
    .withColumn("account_key", F.lower(F.trim(F.col("account_id_v"))))
    .withColumn("product_key", F.lower(F.trim(F.col("product_codename_v"))))
    .join(products, on=["product_key", "account_key"], how="left")
    .join(internal_aff, F.col("affiliate_name_v") == internal_aff["affiliate_name"], how="left")
    .join(rates, F.to_date(F.col("rr_createdate_ts_gmt3")) == rates["rate_date"], how="left")
    .withColumn("exchange_rate", F.coalesce(F.col("exchange_rate"), F.lit(DEFAULT_EXCHANGE_RATE)).cast("decimal(10,4)"))
    .withColumn("unit_cost_usd", F.lit(unit_cost_value).cast("decimal(10,2)"))
)

# quantity a partir do SKU
quantity_expr = F.when(
    F.regexp_extract(F.coalesce(F.col("product_sku_v"), F.lit("")), r"(12|[1-9])UNITS", 1) != "",
    F.regexp_extract(F.col("product_sku_v"), r"(12|[1-9])UNITS", 1).cast("int"),
).otherwise(F.lit(1))
enriched = enriched.withColumn("quantity", quantity_expr)

# payment_status (vocabulario silver, derivado do action_type)
payment_status_expr = (
    F.when(F.col("is_chargeback"), F.lit("chargeback"))
     .when(
        F.col("is_refund")
        & F.col("total_clean_v").isNotNull()
        & (F.coalesce(F.col("refund_amount_v"), F.lit(0.0)) >= F.col("total_clean_v")),
        F.lit("refunded"),
    )
     .when(F.col("is_refund"), F.lit("refunded_partial"))
     .when(F.col("is_cancel"), F.lit("canceled"))
     .otherwise(F.lit("approved"))
)

# transaction_type: refund/chargeback -> Cancel ; neworder -> Sale
transaction_type_expr = (
    F.when(F.col("is_chargeback"), F.lit("Cancel"))
     .when(F.col("is_refund"), F.lit("Cancel"))
     .when(F.col("is_cancel"), F.lit("Cancel"))
     .otherwise(F.lit("Sale"))
)

# sales_type a partir do offer_name
sales_type_expr = (
    F.when(F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).rlike("upsell|downsell"), F.lit("Venda de Funil"))
     .when(F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).contains("order bump"), F.lit("Order Bump"))
     .otherwise(F.lit("Produto Principal"))
)

# total_refund_usd: chargeback -> total_clean ; refund -> refund_amount ; senao 0
total_refund_usd_expr = (
    F.when(F.col("is_chargeback"), F.coalesce(F.col("total_clean_v"), F.lit(0.0)))
     .when(F.col("is_refund"), F.coalesce(F.col("refund_amount_v"), F.lit(0.0)))
     .otherwise(F.lit(0.0))
)

refund_fee_usd_expr = F.when(F.col("is_refund"), F.lit(1.0)).otherwise(F.lit(0.0))

# total_price_usd = total_amount_charged - taxes  (ajuste solicitado)
total_price_usd_val = F.coalesce(F.col("total_amount_charged_v"), F.lit(0.0)) - F.coalesce(F.col("taxes_v"), F.lit(0.0))

# commission_usd por status (sempre sobre colunas USD; base = total_price_usd)
#   approved : total_price_usd - taxes_usd(merchant) - affiliate_amount_usd
#   refunded : total_price_usd - affiliate_amount_usd - refund_fee_usd
#   chargeback: total_price_usd - affiliate_amount_usd - chargeback_fee_usd
commission_usd_expr = (
    F.when(
        F.col("is_chargeback"),
        total_price_usd_val
        - F.coalesce(F.col("aff_commission_v"), F.lit(0.0))
        - F.coalesce(F.col("chargeback_fee_usd_v"), F.lit(0.0)),
    )
     .when(
        F.col("is_refund"),
        total_price_usd_val
        - F.coalesce(F.col("aff_commission_v"), F.lit(0.0))
        - refund_fee_usd_expr,
    )
     .otherwise(
        total_price_usd_val
        - F.coalesce(F.col("merchant_commission_v"), F.lit(0.0))
        - F.coalesce(F.col("aff_commission_v"), F.lit(0.0))
    )
)

# date_refunded (com fuso) e datetime_refunded_platform (sem fuso)
date_refunded_expr = F.when(
    F.col("date_refunded_ts").isNotNull(),
    F.to_date(to_gmt3_from_gmt4(F.col("date_refunded_ts"))),
)
datetime_refunded_platform_expr = F.when(
    F.col("date_refunded_raw").isNotNull() & (F.col("date_refunded_raw") != ""),
    F.col("date_refunded_raw"),
)

result = (
    enriched
    .withColumn("transaction_type", transaction_type_expr)
    .withColumn("payment_status", payment_status_expr)
    .withColumn("cancel_reason", F.col("cancel_reason_v"))
    .withColumn("platform", F.lit("buygoods"))
    .withColumn("client_name", F.col("client_name_v"))
    .withColumn("client_email", F.col("client_email_v"))
    .withColumn("client_phone", F.col("client_phone_v"))
    .withColumn("client_zip", F.col("client_zip_v"))
    .withColumn("client_country", F.col("client_country_v"))
    .withColumn("client_state", F.col("client_state_v"))
    .withColumn("client_city", F.col("client_city_v"))
    .withColumn("client_street", F.col("client_street_v"))
    .withColumn("product_name", F.col("product_name_v"))
    .withColumn("product_sku", F.col("product_sku_v"))
    .withColumn("product_codename", F.col("product_codename_v"))
    .withColumn("product_id", F.col("product_id_v"))
    .withColumn("offer_name", F.col("offer_name"))
    .withColumn("sales_type", sales_type_expr)
    .withColumn("vendor_name", F.lit(None).cast("string"))
    .withColumn("product_cost_usd", dec2(F.col("quantity") * F.coalesce(F.col("unit_cost_usd"), F.lit(0.0))))
    .withColumn("product_cost", dec4(F.col("quantity") * F.coalesce(F.col("unit_cost_usd"), F.lit(0.0)) * F.col("exchange_rate")))
    .withColumn("total_collected_usd", dec2(F.col("total_clean_v")))
    .withColumn("total_price_usd", dec2(total_price_usd_val))
    .withColumn("iva_usd", dec2(F.col("taxes_v")))
    .withColumn("taxes_usd", dec2(F.col("merchant_commission_v")))
    .withColumn("affiliate_amount_usd", dec2(F.col("aff_commission_v")))
    .withColumn("total_price", dec4(total_price_usd_val * F.col("exchange_rate")))
    .withColumn("taxes", dec4(F.col("merchant_commission_v") * F.col("exchange_rate")))
    .withColumn("iva", dec4(F.col("taxes_v") * F.col("exchange_rate")))
    .withColumn("affiliate_amount", dec4(F.col("aff_commission_v") * F.col("exchange_rate")))
    .withColumn("commission_usd", dec2(commission_usd_expr))
    .withColumn("commission", dec4(commission_usd_expr * F.col("exchange_rate")))
    .withColumn("total_refund_usd", dec2(total_refund_usd_expr))
    .withColumn("total_refund", dec4(total_refund_usd_expr * F.col("exchange_rate")))
    .withColumn("refund_fee_usd", dec2(refund_fee_usd_expr))
    .withColumn("refund_fee", dec4(refund_fee_usd_expr * F.col("exchange_rate")))
    .withColumn("chargeback_fee_usd", dec2(F.col("chargeback_fee_usd_v")))
    .withColumn("chargeback_fee", dec4(F.col("chargeback_fee_usd_v") * F.col("exchange_rate")))
    .withColumn("date_refunded", date_refunded_expr)
    .withColumn("datetime_refunded_platform", datetime_refunded_platform_expr)
    .withColumn("affiliate_id", F.col("affiliate_id_v"))
    .withColumn("account_id", F.col("account_id_v"))
    .withColumn("affiliate_name", F.col("affiliate_name_v"))
    .withColumn("is_house_traffic", F.when(F.col("is_internal_flag").isNotNull(), F.lit(True)).otherwise(F.lit(False)))
    .withColumn("utm_source", F.col("utm_source_v"))
    .withColumn("utm_content", F.col("utm_content_v"))
    .withColumn("utm_campaign", F.col("utm_campaign_v"))
    .withColumn("utm_term", F.col("utm_term_v"))
    .withColumn("utm_medium", F.col("utm_medium_v"))
    .withColumn("upsell_parent_receipt", F.col("upsell_parent_receipt_v"))
    .withColumn("created_at_date", F.to_date(F.col("rr_createdate_ts_gmt3")))
    .withColumn("created_at_hour", F.date_format(F.col("rr_createdate_ts_gmt3"), "HH:mm:ss"))
    .withColumn("datetime_platform", F.date_format(F.col("rr_createdate_ts"), "yyyy-MM-dd HH:mm:ss"))
    .withColumn("created_at", F.col("extracted_at_ts"))
    .withColumn("updated_at", F.current_timestamp())
    .withColumn("pipeline_updated_at", F.date_format(F.col("extracted_at_ts"), "yyyy-MM-dd HH:mm:ss"))
    .withColumn("dt_proc", F.to_date(F.col("extracted_at_ts")))
)

result = result.select(
    "transaction_id",
    "transaction_type",
    "payment_status",
    "cancel_reason",
    "platform",
    "client_name",
    "client_email",
    "client_phone",
    "client_zip",
    "client_country",
    "client_state",
    "client_city",
    "client_street",
    "product_name",
    "product_sku",
    "product_codename",
    "product_id",
    "offer_name",
    "quantity",
    "sales_type",
    "vendor_name",
    "product_cost",
    "product_cost_usd",
    "total_collected_usd",
    "total_price_usd",
    "iva_usd",
    "taxes_usd",
    "affiliate_amount_usd",
    "exchange_rate",
    "total_price",
    "taxes",
    "iva",
    "affiliate_amount",
    "commission_usd",
    "commission",
    "total_refund_usd",
    "total_refund",
    "refund_fee_usd",
    "refund_fee",
    "chargeback_fee_usd",
    "chargeback_fee",
    "date_refunded",
    "datetime_refunded_platform",
    "affiliate_id",
    "account_id",
    "affiliate_name",
    "is_house_traffic",
    "utm_source",
    "utm_content",
    "utm_campaign",
    "utm_term",
    "utm_medium",
    "upsell_parent_receipt",
    "created_at_date",
    "created_at_hour",
    "datetime_platform",
    "created_at",
    "updated_at",
    "pipeline_updated_at",
    "dt_proc",
)

# --------------------------------------------------------------------------- #
# 5) UPSERT por transaction_id (preserva imutaveis da Silver existente)
# --------------------------------------------------------------------------- #
IMMUTABLE_FIELDS = [
    "client_name", "client_email", "client_phone", "client_zip", "client_country",
    "client_state", "client_city", "client_street", "product_name", "product_sku",
    "product_codename", "product_id", "offer_name", "quantity", "sales_type",
    "vendor_name", "total_collected_usd", "total_price_usd", "iva_usd", "taxes_usd",
    "affiliate_amount_usd", "exchange_rate", "total_price", "taxes", "iva",
    "affiliate_amount", "affiliate_id", "affiliate_name", "utm_source", "utm_content",
    "utm_campaign", "utm_term", "utm_medium", "upsell_parent_receipt", "account_id",
    "created_at_date", "created_at_hour", "datetime_platform", "created_at",
]

current_silver = None
try:
    current_silver = spark.read.parquet(OUTPUT_PATH)
    print("[INFO] Silver existente lida com sucesso")
except Exception as e:
    print(f"[INFO] Primeira execucao ou Silver vazia: {str(e)}")

if current_silver is not None and len(current_silver.take(1)) > 0:
    current_silver = current_silver.toDF(*[c.lower() for c in current_silver.columns])
    if "date_refunded" in current_silver.columns:
        current_silver = current_silver.withColumn("date_refunded", F.to_date(F.col("date_refunded")))

    batch_tids = result.select("transaction_id").distinct()

    prev_cols = [F.col("transaction_id")] + [
        F.col(c).alias(f"{c}_prev") for c in IMMUTABLE_FIELDS if c in current_silver.columns
    ]
    current_immutables = (
        current_silver.select(*prev_cols)
        .join(F.broadcast(batch_tids), on="transaction_id", how="inner")
        .dropDuplicates(["transaction_id"])
    )

    result_with_immutables = result.join(current_immutables, on="transaction_id", how="left")
    for c in IMMUTABLE_FIELDS:
        if f"{c}_prev" in result_with_immutables.columns:
            if c == "created_at":
                # preserva o created_at original (prev tem prioridade)
                result_with_immutables = result_with_immutables.withColumn(
                    c, F.coalesce(F.col(f"{c}_prev"), F.col(c))
                )
            else:
                result_with_immutables = result_with_immutables.withColumn(
                    c, F.coalesce(F.col(c), F.col(f"{c}_prev"))
                )
    result_with_immutables = result_with_immutables.drop(
        *[f"{c}_prev" for c in IMMUTABLE_FIELDS if f"{c}_prev" in result_with_immutables.columns]
    )

    untouched_silver = current_silver.join(F.broadcast(batch_tids), on="transaction_id", how="left_anti")
    upserted = result_with_immutables.unionByName(untouched_silver, allowMissingColumns=True)
else:
    upserted = result

# --------------------------------------------------------------------------- #
# 6) Escrita (particionado por dt_proc)
# --------------------------------------------------------------------------- #
# IMPORTANTE: `upserted` deriva da leitura da PROPRIA silver (untouched_silver
# vem de OUTPUT_PATH). Gravar com mode("overwrite") DIRETO em OUTPUT_PATH apaga
# os arquivos que o scan lazy ainda precisa ler -> FileNotFound/"No such file".
# Solucao: gravar primeiro num STAGING path, reler de la (lineage passa a
# independer de OUTPUT_PATH) e so entao sobrescrever o destino final.
import uuid as _uuid, boto3 as _boto3
from urllib.parse import urlparse as _urlparse

STAGING_PATH = f"s3://{args['target_bucket']}/_staging_{TARGET_TABLE}/run_{_uuid.uuid4().hex}/"

total = upserted.count()
print(f"[INFO] Gravando {total} linhas em STAGING {STAGING_PATH}")
upserted.write.mode("overwrite").partitionBy("dt_proc").parquet(STAGING_PATH)

# Re-le do staging: agora o DataFrame nao depende mais de OUTPUT_PATH.
staged = spark.read.parquet(STAGING_PATH)
print(f"[INFO] Sobrescrevendo destino final {OUTPUT_PATH}")
staged.write.mode("overwrite").partitionBy("dt_proc").parquet(OUTPUT_PATH)

# Limpa o staging (best-effort) para nao acumular lixo no bucket.
try:
    _u = _urlparse(STAGING_PATH)
    _bucket, _prefix = _u.netloc, _u.path.lstrip("/")
    _s3 = _boto3.client("s3")
    _paginator = _s3.get_paginator("list_objects_v2")
    _to_del = []
    for _page in _paginator.paginate(Bucket=_bucket, Prefix=_prefix):
        for _obj in _page.get("Contents", []):
            _to_del.append({"Key": _obj["Key"]})
            if len(_to_del) == 1000:
                _s3.delete_objects(Bucket=_bucket, Delete={"Objects": _to_del})
                _to_del = []
    if _to_del:
        _s3.delete_objects(Bucket=_bucket, Delete={"Objects": _to_del})
    print(f"[INFO] Staging limpo: {STAGING_PATH}")
except Exception as _e:
    print(f"[WARN] Falha ao limpar staging (ignorado): {_e}")

job.commit()
````

## Relacionados
[[00-Data-Lake]]
