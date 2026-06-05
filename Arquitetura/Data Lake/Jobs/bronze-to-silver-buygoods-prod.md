---
tipo: job-glue
ambiente: prod
fluxo: bronze-to-silver
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-03 13:34
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# bronze-to-silver-buygoods-prod

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
| Script | `s3://gex-datalake-bronze-prod/scripts/bronze_to_silver_buygoods.py` |
| Criado | 2026-05-14 16:39:51.009000-03:00 |
| Modificado | 2026-05-15 11:33:54.141000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--BRONZE_BUCKET` | gex-datalake-bronze-prod |
| `--CONNECTION_NAME` |  |
| `--SOURCE_DATABASE` | gex_db_prod_bronze |
| `--TARGET_DATABASE` | gex_db_prod_silver |
| `--TRANSACTION_TYPE_MODE` | lifecycle |
| `--db_table` | buygoods_physical_new |
| `--target_bucket` | gex-datalake-silver-prod |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-03 13:34 | SUCCEEDED | 6m46s | — |
| 2026-06-03 13:14 | SUCCEEDED | 6m36s | — |
| 2026-06-03 11:34 | SUCCEEDED | 7m7s | — |
| 2026-06-03 09:34 | SUCCEEDED | 7m7s | — |
| 2026-06-03 07:33 | SUCCEEDED | 6m58s | — |
| 2026-06-03 05:33 | SUCCEEDED | 6m37s | — |
| 2026-06-03 03:33 | SUCCEEDED | 6m53s | — |
| 2026-06-03 01:33 | SUCCEEDED | 6m40s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/bronze_to_silver_buygoods.py` — baixado do S3 (read-only).

````python
"""
Glue Job: gex-bronze-to-silver-buygoods-{env}

Builds Silver table buygoods_physical_new from Bronze webhook payloads.

Key rules implemented:
- UPSERT by transaction_id (order_id_global)
- Financial immutability from neworder only
- Payment status only-advance hierarchy
- sales_type derived from offer_name
- commission_usd formula by lifecycle (SALE/RFND/CGBK)
- rr_createdate conversion GMT-4 -> GMT-3
"""

import sys
import urllib.parse

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import Window
from pyspark.sql.types import DoubleType, MapType, StringType


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


SOURCE_TABLE = get_optional_arg("SOURCE_TABLE", "tb_bronze_buygoods")
TARGET_TABLE = get_optional_arg("TARGET_TABLE", "buygoods_physical_new")
PRODUCTS_TABLE = get_optional_arg("PRODUCTS_TABLE", "tb_bronze_buygoods_products")
INTERNAL_AFFILIATES_TABLE = get_optional_arg("INTERNAL_AFFILIATES_TABLE", "tb_bronze_buygoods_internal_affiliates")
EXCHANGE_RATES_TABLE = get_optional_arg("EXCHANGE_RATES_TABLE", "tb_bronze_exchange_rates")
PRODUCT_COSTS_TABLE = get_optional_arg("PRODUCT_COSTS_TABLE", "tb_bronze_general_product_costs")
TRANSACTION_TYPE_MODE = get_optional_arg("TRANSACTION_TYPE_MODE", "lifecycle").strip().lower()


sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
spark.conf.set("spark.sql.session.timeZone", "America/Sao_Paulo")

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

SOURCE_DB = args["SOURCE_DATABASE"]
TARGET_DB = args["TARGET_DATABASE"]
OUTPUT_PATH = f"s3://{args['target_bucket']}/buygoods_physical_new/"


def try_read_table(database: str, table_name: str, empty_df: DataFrame = None) -> DataFrame:
    try:
        return glueContext.create_dynamic_frame.from_catalog(
            database=database,
            table_name=table_name,
        ).toDF()
    except Exception as exc:
        print(f"[WARN] Could not read table {database}.{table_name}: {exc}")
        if empty_df is not None:
            return empty_df
        return spark.createDataFrame([], "dummy string").drop("dummy")


@F.udf(MapType(StringType(), StringType()))
def parse_querystring(payload: str):
    if not payload:
        return {}
    parsed = urllib.parse.parse_qs(urllib.parse.unquote_plus(payload), keep_blank_values=True)
    return {k: (v[0] if v else "") for k, v in parsed.items()}


def parse_money(col: F.Column) -> F.Column:
    cleaned = F.regexp_replace(F.coalesce(col, F.lit("")), r"[^0-9.\-]", "")
    return F.when(cleaned == "", None).otherwise(cleaned.cast(DoubleType()))


def parse_ts(col: F.Column) -> F.Column:
    return F.to_timestamp(F.regexp_replace(F.trim(col), "T", " "))


def parse_bg_datetime(col: F.Column) -> F.Column:
    return F.to_timestamp(F.trim(col), "yyyy-MM-dd HH:mm:ss")


def to_gmt3_from_gmt4(col: F.Column) -> F.Column:
    return col + F.expr("INTERVAL 1 HOUR")


def dec2(col: F.Column) -> F.Column:
    return F.round(col, 2).cast("decimal(10,2)")


def dec4(col: F.Column) -> F.Column:
    return F.round(col, 4).cast("decimal(12,4)")


bronze = try_read_table(SOURCE_DB, SOURCE_TABLE)

if bronze.rdd.isEmpty():
    print("[INFO] No data in Bronze source table. Nothing to process.")
    job.commit()
    sys.exit(0)

bronze = bronze.toDF(*[c.lower() for c in bronze.columns])


def pick_column(*names: str) -> F.Column:
    for name in names:
        if name in bronze.columns:
            return F.col(name)
    return F.lit(None)

base_payload = (
    bronze
    .withColumn("payload_querystring", F.coalesce(
        F.get_json_object(pick_column("raw_payload"), "$.raw_payload"),
        pick_column("raw_payload"),
    ))
    .withColumn("event_received_raw", F.coalesce(
        F.get_json_object(pick_column("raw_payload"), "$._received_at"),
        pick_column("_received_at", "ingested_at", "source_modification_time"),
    ))
    .withColumn("payload_map", parse_querystring(F.col("payload_querystring")))
)


def q(field: str) -> F.Column:
    return F.element_at(F.col("payload_map"), F.lit(field))


def q_any(*fields: str) -> F.Column:
    return F.coalesce(*[q(field) for field in fields])


events = (
    base_payload
    .withColumn("transaction_id", F.trim(q("order_id_global")))
    .withColumn("action_type_raw", F.lower(F.trim(q_any("action_type", "type"))))
    .withColumn(
        "action_type",
        F.when(F.col("action_type_raw") == "neworder", F.lit("sale"))
         .when(F.col("action_type_raw") == "refund", F.lit("refund"))
         .when(F.col("action_type_raw") == "cancel", F.lit("cancel"))
         .when(F.col("action_type_raw") == "chargeback", F.lit("chargeback"))
         .otherwise(F.col("action_type_raw"))
    )
    .withColumn("rr_createdate_raw", q_any("rr_createdate", "order_date_time"))
    .withColumn("rr_createdate_ts", parse_bg_datetime(q_any("rr_createdate", "order_date_time")))
    .withColumn("rr_createdate_ts_gmt3", to_gmt3_from_gmt4(F.col("rr_createdate_ts")))
    .withColumn("event_received_ts", parse_ts(F.col("event_received_raw")))
    .withColumn("event_ts", F.coalesce(F.col("event_received_ts"), F.col("rr_createdate_ts_gmt3")))
    .withColumn("date_refunded_payload_ts", parse_bg_datetime(q_any("date_refunded")))
    .withColumn("date_chargedback_payload_ts", parse_bg_datetime(q_any("date_chargedback")))
    .withColumn("refund_effective_ts", F.coalesce(F.col("event_received_ts"), F.col("date_refunded_payload_ts")))
    .withColumn("chargeback_effective_ts", F.coalesce(F.col("date_chargedback_payload_ts"), F.col("event_received_ts")))
    .withColumn("total_clean", parse_money(q("total_clean")))
    .withColumn("product_subtotal", parse_money(q("product_subtotal")))
    .withColumn("total_amount_charged", parse_money(q("total_amount_charged")))  # AJUSTE - novo campo
    .withColumn("taxes_bg", parse_money(q("taxes")))
    .withColumn("merchant_commission", parse_money(q("merchant_commission")))
    .withColumn("aff_commission", parse_money(q("aff_commission")))
    .withColumn("refund_amount", parse_money(q("refund_amount")))
    .withColumn("chargeback_fee_usd", parse_money(q("chargeback_fee")))
    .withColumn("account_id", F.trim(q("account_id")))
    .withColumn("affiliate_id", F.trim(q("aff_id")))
    .withColumn("affiliate_name", F.lower(F.trim(q("aff_name"))))
    .withColumn("product_codename", F.trim(q("product_codename")))
    .withColumn("product_id", parse_money(q("product_id")).cast("int"))
    .withColumn("product_name", F.trim(q_any("product_name", "product")))
    .withColumn("product_sku", F.trim(q("sku")))
    .withColumn("shipping_name", F.trim(q_any("shipping_name", "customer_name", "name")))
    .withColumn("shipping_address", F.trim(q_any("shipping_address", "address")))
    .withColumn("shipping_city", F.trim(q_any("shipping_city", "city")))
    .withColumn("shipping_state", F.trim(q_any("shipping_state", "state")))
    .withColumn("shipping_country", F.upper(F.trim(q_any("country_2letter", "country"))))
    .withColumn("shipping_zip", F.trim(q_any("shipping_zip", "zip")))
    .withColumn("customer_email", F.lower(F.trim(q_any("customer_emailaddress", "email"))))
    .withColumn("customer_phone", F.regexp_replace(F.coalesce(q_any("customer_phone", "phone"), F.lit("")), r"[^0-9]", ""))
    .withColumn("subid", F.trim(q("subid")))
    .withColumn("subid2", F.trim(q("subid2")))
    .withColumn("subid3", F.trim(q("subid3")))
    .withColumn("subid4", F.trim(q("subid4")))
    .withColumn("subid5", F.trim(q("subid5")))
    .withColumn("sessid2", F.trim(q("sessid2")))
    .withColumn("payment_method", F.lower(F.trim(q("payment_method"))))
    .withColumn("braintree_agreement", F.trim(q("braintree_agreement")))
    .withColumn("paypal_native_agreement", F.trim(q("paypal_native_agreement")))
    .withColumn("klarna_agreement", F.trim(q("klarna_agreement")))
    .withColumn("dt_proc", F.to_date(F.coalesce(F.col("dt_proc"), F.current_date().cast("string"))))
    .filter(F.col("transaction_id").isNotNull() & (F.col("transaction_id") != ""))
    .filter(F.coalesce(q("is_test"), F.lit("0")) != "1")  # AJUSTE – descarta compras teste (is_test=1)
)

dedup_columns = [column for column in ["source_file", "transaction_id", "action_type", "event_received_raw"] if column in events.columns]
events = events.dropDuplicates(dedup_columns)

sale_events = events.filter(F.col("action_type") == "sale")
refund_events = events.filter(F.col("action_type") == "refund")
chargeback_events = events.filter(F.col("action_type") == "chargeback")

w_sale = Window.partitionBy("transaction_id").orderBy(F.col("event_ts").asc_nulls_last())
sale_snapshot = (
    sale_events
    .withColumn("rn", F.row_number().over(w_sale))
    .filter(F.col("rn") == 1)
    .select(
        "transaction_id",
        "rr_createdate_ts",
        "rr_createdate_ts_gmt3",
        "total_clean",
        "product_subtotal",
        "total_amount_charged",  # AJUSTE - captura do neworder para imutabilidade
        F.col("taxes_bg").alias("taxes_bg_sale"),  # AJUSTE 3 - isolamento: taxes so do neworder
        "merchant_commission",
        "aff_commission",
        "account_id",
        "affiliate_id",
        "affiliate_name",
        "product_codename",
        "product_id",
        "product_name",
        "product_sku",
        "shipping_name",
        "shipping_address",
        "shipping_city",
        "shipping_state",
        "shipping_country",
        "shipping_zip",
        "customer_email",
        "customer_phone",
        "subid",
        "subid2",
        "subid3",
        "subid4",
        "subid5",
        "sessid2",
        "payment_method",
        "braintree_agreement",
        "paypal_native_agreement",
        "klarna_agreement",
        "dt_proc",
    )
)

agg_events = (
    events
    .groupBy("transaction_id")
    .agg(
        F.max(F.when(F.col("action_type") == "sale", F.lit(1)).otherwise(F.lit(0))).alias("has_sale"),
        F.max(F.when(F.col("action_type") == "refund", F.lit(1)).otherwise(F.lit(0))).alias("has_refund"),
        F.max(F.when(F.col("action_type") == "chargeback", F.lit(1)).otherwise(F.lit(0))).alias("has_chargeback"),
        F.sum(F.when(F.col("action_type") == "refund", F.coalesce(F.col("refund_amount"), F.lit(0.0))).otherwise(F.lit(0.0))).alias("total_refund_usd_raw"),
        F.max(F.when(F.col("action_type") == "chargeback", F.coalesce(F.col("chargeback_fee_usd"), F.lit(0.0))).otherwise(F.lit(0.0))).alias("chargeback_fee_usd_raw"),
        F.min(F.when(F.col("action_type") == "refund", F.col("refund_effective_ts"))).alias("first_refund_platform_ts"),
        F.max(F.when(F.col("action_type") == "chargeback", F.col("chargeback_effective_ts"))).alias("last_chargeback_platform_ts"),
        F.max("event_ts").alias("last_event_ts"),
    )
)

w_last = Window.partitionBy("transaction_id").orderBy(F.col("event_ts").desc_nulls_last())
last_event = (
    events
    .withColumn("rn", F.row_number().over(w_last))
    .filter(F.col("rn") == 1)
    .select("transaction_id", "action_type")
)

tx = (
    agg_events
    .join(sale_snapshot, on="transaction_id", how="left")
    .join(last_event, on="transaction_id", how="left")
)


products_raw = try_read_table(SOURCE_DB, PRODUCTS_TABLE)
if products_raw.rdd.isEmpty():
    products = spark.createDataFrame([], "product_key string, account_key string, offer_name string")
else:
    products_raw = products_raw.toDF(*[c.lower() for c in products_raw.columns])
    products = (
        products_raw
        .withColumn("product_key", F.lower(F.trim(F.coalesce(
            F.col("product_codename") if "product_codename" in products_raw.columns else F.lit(None),
            F.col("product_id") if "product_id" in products_raw.columns else F.lit(None),
            F.col("base_sku") if "base_sku" in products_raw.columns else F.lit(None),
        ))))
        .withColumn("account_key", F.lower(F.trim(F.coalesce(
            F.col("account_id") if "account_id" in products_raw.columns else F.lit(None),
            F.col("account_name") if "account_name" in products_raw.columns else F.lit(None),
        ))))
        .withColumn("offer_name", F.trim(F.coalesce(
            F.col("offer_name") if "offer_name" in products_raw.columns else F.lit(None),
            F.col("product_name") if "product_name" in products_raw.columns else F.lit(None),
        )))
        .select("product_key", "account_key", "offer_name")
        .dropDuplicates(["product_key", "account_key"])
    )


internal_raw = try_read_table(SOURCE_DB, INTERNAL_AFFILIATES_TABLE)
if internal_raw.rdd.isEmpty():
    internal_aff = spark.createDataFrame([], "affiliate_id string, traffic_source string")
else:
    internal_raw = internal_raw.toDF(*[c.lower() for c in internal_raw.columns])
    internal_aff = (
        internal_raw
        .withColumn("affiliate_id", F.trim(F.coalesce(
            F.col("id") if "id" in internal_raw.columns else F.lit(None),
            F.col("affiliate_id") if "affiliate_id" in internal_raw.columns else F.lit(None),
        )))
        .withColumn("traffic_source", F.trim(F.coalesce(
            F.col("traffic_source") if "traffic_source" in internal_raw.columns else F.lit(None),
            F.col("source") if "source" in internal_raw.columns else F.lit(None),
        )))
        .withColumn("traffic_manager", F.trim(F.coalesce(
            F.col("traffic_manager") if "traffic_manager" in internal_raw.columns else F.lit(None),
            F.col("manager") if "manager" in internal_raw.columns else F.lit(None),
        )))
        .withColumn("affiliate_name", F.lower(F.trim(F.coalesce(
            F.col("affiliate_name") if "affiliate_name" in internal_raw.columns else F.lit(None),
            F.lit(None),
        ))))  # AJUSTE 2 — lowercase para join por affiliate_name
        .withColumn("is_internal_flag", F.lit(1))
        .select("affiliate_name", "traffic_source", "traffic_manager", "is_internal_flag")  # CORREÇÃO — removido affiliate_id que causava ambiguidade após mudança do join para affiliate_name
        .dropDuplicates(["affiliate_name"])
    )


rates_raw = try_read_table(SOURCE_DB, EXCHANGE_RATES_TABLE)
if rates_raw.rdd.isEmpty():
    rates = spark.createDataFrame([], "rate_date date, exchange_rate decimal(10,4)")
else:
    rates_raw = rates_raw.toDF(*[c.lower() for c in rates_raw.columns])
    rates = (
        rates_raw
        .withColumn("rate_date", F.to_date(F.coalesce(
            F.col("date") if "date" in rates_raw.columns else F.lit(None),
            F.col("dt") if "dt" in rates_raw.columns else F.lit(None),
            F.col("transactiondate") if "transactiondate" in rates_raw.columns else F.lit(None),
        )))
        .withColumn("exchange_rate", F.coalesce(
            F.col("exchange_rate") if "exchange_rate" in rates_raw.columns else F.lit(None),
            F.col("rate") if "rate" in rates_raw.columns else F.lit(None),
        ).cast("decimal(10,4)"))
        .select("rate_date", "exchange_rate")
        .where(F.col("rate_date").isNotNull() & F.col("exchange_rate").isNotNull())
        .dropDuplicates(["rate_date"])
    )


costs_raw = try_read_table(SOURCE_DB, PRODUCT_COSTS_TABLE)
if costs_raw.rdd.isEmpty():
    costs = spark.createDataFrame([], "cost_product_key string, valid_from date, valid_until date, unit_cost_usd decimal(10,2)")
else:
    costs_raw = costs_raw.toDF(*[c.lower() for c in costs_raw.columns])
    costs = (
        costs_raw
        .withColumn("cost_product_key", F.lower(F.trim(F.coalesce(
            F.col("product_sku") if "product_sku" in costs_raw.columns else F.lit(None),
            F.col("sku") if "sku" in costs_raw.columns else F.lit(None),
            F.col("product_codename") if "product_codename" in costs_raw.columns else F.lit(None),
            F.col("product_id") if "product_id" in costs_raw.columns else F.lit(None),
        ))))
        .withColumn("valid_from", F.to_date(F.coalesce(
            F.col("valid_from") if "valid_from" in costs_raw.columns else F.lit(None),
            F.col("start_date") if "start_date" in costs_raw.columns else F.lit(None),
        )))
        .withColumn("valid_until", F.to_date(F.coalesce(
            F.col("valid_until") if "valid_until" in costs_raw.columns else F.lit(None),
            F.col("end_date") if "end_date" in costs_raw.columns else F.lit(None),
        )))
        .withColumn("unit_cost_usd", F.coalesce(
            F.col("unit_cost_usd") if "unit_cost_usd" in costs_raw.columns else F.lit(None),
            F.col("unit_cost") if "unit_cost" in costs_raw.columns else F.lit(None),
            F.col("cost_usd") if "cost_usd" in costs_raw.columns else F.lit(None),
        ).cast("decimal(10,2)"))
        .select("cost_product_key", "valid_from", "valid_until", "unit_cost_usd")
        .where(F.col("cost_product_key").isNotNull() & F.col("unit_cost_usd").isNotNull())
    )


enriched = (
    tx
    .withColumn("account_key", F.lower(F.trim(F.col("account_id"))))
    .withColumn("product_key", F.lower(F.trim(F.col("product_codename"))))
    .join(products, on=["product_key", "account_key"], how="left")
    .join(internal_aff, on=["affiliate_name"], how="left")  # AJUSTE 2 — join por affiliate_name
    .join(rates, F.to_date(F.col("rr_createdate_ts_gmt3")) == F.col("rate_date"), "left")
    .withColumn("exchange_rate", F.coalesce(F.col("exchange_rate"), F.lit(5.10)).cast("decimal(10,4)"))
)

quantity_expr = F.when(
    F.regexp_extract(F.coalesce(F.col("product_sku"), F.lit("")), r"(12|[1-9])UNITS", 1) != "",
    F.regexp_extract(F.col("product_sku"), r"(12|[1-9])UNITS", 1).cast("int"),
).otherwise(F.lit(1))

enriched = enriched.withColumn("quantity", quantity_expr)

# CORREÇÃO — custo fixo para todos os produtos BuyGoods
# general_product_costs não tem chave de produto; unit_cost_usd é global
unit_cost_value = 5.00
if not costs.rdd.isEmpty():
    first_cost = costs.orderBy(F.col("valid_from").desc_nulls_last()).first()
    if first_cost and first_cost["unit_cost_usd"] is not None:
        unit_cost_value = float(first_cost["unit_cost_usd"])

print(f"[INFO] unit_cost_usd fixo aplicado: {unit_cost_value}")
enriched = enriched.withColumn("unit_cost_usd", F.lit(unit_cost_value).cast("decimal(10,2)"))

refund_fee_usd_expr = F.when(F.col("has_refund") == 1, F.lit(1.0)).otherwise(F.lit(0.0))

# AJUSTE 1 - total_refund_usd correto para chargeback (refund_amount vem zerado)
total_refund_usd_corrected_expr = (
    F.when(
        F.col("has_chargeback") == 1,
        F.coalesce(F.col("total_clean"), F.lit(0.0))
    )
    .otherwise(F.col("total_refund_usd_raw"))
)

payment_status_expr = (
    F.when(F.col("has_chargeback") == 1, F.lit("chargeback"))
     .when(
        (F.col("has_refund") == 1)
        & (F.col("total_clean").isNotNull())
        & (F.col("total_refund_usd_raw") >= F.col("total_clean")),
        F.lit("refunded"),
    )
    .when(F.col("has_refund") == 1, F.lit("refunded_partial"))
    .otherwise(F.lit("approved"))
)

commission_usd_expr = (
    F.when(
        payment_status_expr == "chargeback",
        F.coalesce(F.col("total_amount_charged"), F.lit(0.0)) - F.lit(0.0) - F.coalesce(F.col("aff_commission"), F.lit(0.0)) - F.coalesce(F.col("chargeback_fee_usd_raw"), F.lit(0.0)),  # AJUSTE
    )
    .when(
        payment_status_expr.isin("refunded", "refunded_partial"),
        F.coalesce(F.col("total_amount_charged"), F.lit(0.0)) - F.lit(0.0) - F.coalesce(F.col("aff_commission"), F.lit(0.0)) - refund_fee_usd_expr,  # AJUSTE
    )
    .otherwise(
        F.coalesce(F.col("total_amount_charged"), F.lit(0.0)) - F.coalesce(F.col("merchant_commission"), F.lit(0.0)) - F.coalesce(F.col("aff_commission"), F.lit(0.0))  # AJUSTE
    )
)

commission_usd_final_expr = F.when(F.col("has_sale") == 1, commission_usd_expr)

chargeback_refund_date_expr = F.when(
    F.col("last_chargeback_platform_ts").isNotNull(),
    F.to_date(to_gmt3_from_gmt4(F.col("last_chargeback_platform_ts")))
).otherwise(
    F.to_date(F.from_utc_timestamp(F.col("last_event_ts"), "America/Sao_Paulo"))
)

refund_date_expr = F.when(
    F.col("first_refund_platform_ts").isNotNull(),
    F.to_date(to_gmt3_from_gmt4(F.col("first_refund_platform_ts")))
).otherwise(
    F.to_date(F.from_utc_timestamp(F.col("last_event_ts"), "America/Sao_Paulo"))
)

chargeback_platform_expr = F.when(
    F.col("last_chargeback_platform_ts").isNotNull(),
    F.date_format(
        F.col("last_chargeback_platform_ts") - F.expr("INTERVAL 4 HOURS"),
        "yyyy-MM-dd HH:mm:ss"
    )
).otherwise(
    F.date_format(
        F.col("last_event_ts") - F.expr("INTERVAL 4 HOURS"),
        "yyyy-MM-dd HH:mm:ss"
    )
)

refund_platform_expr = F.when(  # CORRECAO 2 - datetime_refunded_platform: subtrair 4h para refletir horario da BuyGoods
    F.col("first_refund_platform_ts").isNotNull(),
    F.date_format(
        F.col("first_refund_platform_ts") - F.expr("INTERVAL 4 HOURS"),
        "yyyy-MM-dd HH:mm:ss"
    )
).otherwise(
    F.date_format(
        F.col("last_event_ts") - F.expr("INTERVAL 4 HOURS"),
        "yyyy-MM-dd HH:mm:ss"
    )
)

sales_type_expr = (
    F.when(F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).rlike("upsell|downsell"), F.lit("Venda de Funil"))
     .when(F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).contains("order bump"), F.lit("Order Bump"))
     .when(F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).contains("produto principal"), F.lit("Produto Principal"))
     .otherwise(F.lit("Produto Principal"))
)

transaction_type_expr = F.lit("Sale")
if TRANSACTION_TYPE_MODE in {"event", "lifecycle", "last_event"}:
    transaction_type_expr = F.initcap(F.coalesce(F.col("action_type"), F.lit("sale")))

print(f"[INFO] TRANSACTION_TYPE_MODE={TRANSACTION_TYPE_MODE}")
print("[INFO] taxes_usd remains immutable from sale snapshot; refund/chargeback use taxes=0 only in commission formula.")

result = (
    enriched
    .withColumn("transaction_type", transaction_type_expr)
    .withColumn("payment_status", payment_status_expr)
    .withColumn("platform", F.lit("buygoods"))
    .withColumn("client_name", F.initcap(F.trim(F.col("shipping_name"))))
    .withColumn("client_email", F.lower(F.trim(F.col("customer_email"))))
    .withColumn("client_phone", F.col("customer_phone"))
    .withColumn("client_zip", F.col("shipping_zip"))
    .withColumn("client_country", F.col("shipping_country"))
    .withColumn("client_state", F.col("shipping_state"))
    .withColumn("client_city", F.col("shipping_city"))
    .withColumn("client_street", F.col("shipping_address"))
    .withColumn("offer_name", F.col("offer_name"))  # AJUSTE 1 — NULL quando não encontrado na tabela products
    .withColumn("sales_type", sales_type_expr)
    .withColumn("vendor_name", F.lit(None).cast("string"))
    .withColumn("product_cost_usd", dec2(F.col("quantity") * F.coalesce(F.col("unit_cost_usd"), F.lit(0.0))))
    .withColumn("product_cost", dec4(F.col("quantity") * F.coalesce(F.col("unit_cost_usd"), F.lit(0.0)) * F.col("exchange_rate")))
    .withColumn("total_collected_usd", dec2(F.col("total_clean")))
    .withColumn("total_price_usd", dec2(F.col("total_amount_charged")))  # AJUSTE
    .withColumn("iva_usd", dec2(F.col("taxes_bg_sale")))  # AJUSTE 3
    .withColumn("taxes_usd", dec2(F.col("merchant_commission")))
    .withColumn("affiliate_amount_usd", dec2(F.col("aff_commission")))
    .withColumn("total_price", dec4(F.col("total_amount_charged") * F.col("exchange_rate")))  # AJUSTE
    .withColumn("taxes", dec4(F.col("merchant_commission") * F.col("exchange_rate")))
    .withColumn("iva", dec4(F.col("taxes_bg_sale") * F.col("exchange_rate")))  # AJUSTE 3
    .withColumn("affiliate_amount", dec4(F.col("aff_commission") * F.col("exchange_rate")))
    .withColumn("commission_usd", dec2(commission_usd_final_expr))
    .withColumn("commission", dec4(commission_usd_final_expr * F.col("exchange_rate")))
    .withColumn("total_refund_usd", dec2(total_refund_usd_corrected_expr))  # AJUSTE 1
    .withColumn("total_refund", dec4(total_refund_usd_corrected_expr * F.col("exchange_rate")))  # AJUSTE 1
    .withColumn("refund_fee_usd", dec2(refund_fee_usd_expr))
    .withColumn("refund_fee", dec4(refund_fee_usd_expr * F.col("exchange_rate")))
    .withColumn("chargeback_fee_usd", dec2(F.col("chargeback_fee_usd_raw")))
    .withColumn("chargeback_fee", dec4(F.col("chargeback_fee_usd_raw") * F.col("exchange_rate")))
    .withColumn(
        "date_refunded",
        F.when(
            F.col("has_chargeback") == 1,
            chargeback_refund_date_expr,
        ).when(
            F.col("has_refund") == 1,
            refund_date_expr,
        )
    )
    .withColumn(
        "datetime_refunded_platform",
        F.when(F.col("has_chargeback") == 1, chargeback_platform_expr)
         .when(F.col("has_refund") == 1, refund_platform_expr)
    )
    .withColumn("is_house_traffic", F.when(F.col("is_internal_flag").isNotNull(), F.lit(True)).otherwise(F.lit(False)))
    .withColumn("upsell_parent_receipt", F.col("sessid2"))
    .withColumn("created_at_date", F.to_date(F.col("rr_createdate_ts_gmt3")))
    .withColumn("created_at_hour", F.date_format(F.col("rr_createdate_ts_gmt3"), "HH:mm:ss"))
    .withColumn("datetime_platform", F.date_format(F.col("rr_createdate_ts"), "yyyy-MM-dd HH:mm:ss"))
    .withColumn("created_at", F.current_timestamp())
    .withColumn("updated_at", F.current_timestamp())
    .withColumn("pipeline_updated_at", F.date_format(
        F.current_timestamp(),
        "yyyy-MM-dd HH:mm:ss"
    ))  # CORRECAO - session tz ja e America/Sao_Paulo; from_utc_timestamp causava double-conversion
    # dt_proc preservado da Bronze (partição original do path de origem)
    .withColumn("dt_proc", F.coalesce(F.col("dt_proc"), F.current_date()))
)

result = result.select(
    "transaction_id",
    "transaction_type",
    "payment_status",
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
    "subid",
    "subid2",
    "subid3",
    "subid4",
    "subid5",
    "upsell_parent_receipt",
    "created_at_date",
    "created_at_hour",
    "datetime_platform",
    "created_at",
    "updated_at",
    "pipeline_updated_at",  # AJUSTE 2
    "dt_proc",
)


current_silver = None
try:
    current_silver = spark.read.parquet(OUTPUT_PATH).cache()
    print("[INFO] Silver existente lida com sucesso")
except Exception as e:
    print(f"[INFO] Primeira execução ou Silver vazia — criando nova: {str(e)}")

if current_silver is not None and len(current_silver.take(1)) > 0:
    current_silver = current_silver.toDF(*[c.lower() for c in current_silver.columns])
    # Cast de segurança para transição de schema (string -> date)
    if "date_refunded" in current_silver.columns:
        current_silver = current_silver.withColumn("date_refunded", F.to_date(F.col("date_refunded")))

    batch_tids = result.select("transaction_id").distinct().cache()

    current_immutables = (
        current_silver
        .select(
            F.col("transaction_id"),
            F.col("client_name").alias("client_name_prev"),
            F.col("client_email").alias("client_email_prev"),
            F.col("client_phone").alias("client_phone_prev"),
            F.col("client_zip").alias("client_zip_prev"),
            F.col("client_country").alias("client_country_prev"),
            F.col("client_state").alias("client_state_prev"),
            F.col("client_city").alias("client_city_prev"),
            F.col("client_street").alias("client_street_prev"),
            F.col("product_name").alias("product_name_prev"),
            F.col("product_sku").alias("product_sku_prev"),
            F.col("product_codename").alias("product_codename_prev"),
            F.col("product_id").alias("product_id_prev"),
            F.col("offer_name").alias("offer_name_prev"),
            F.col("quantity").alias("quantity_prev"),
            F.col("sales_type").alias("sales_type_prev"),
            F.col("vendor_name").alias("vendor_name_prev"),
            F.col("total_collected_usd").alias("total_collected_usd_prev"),
            F.col("total_price_usd").alias("total_price_usd_prev"),
            F.col("iva_usd").alias("iva_usd_prev"),
            F.col("taxes_usd").alias("taxes_usd_prev"),
            F.col("affiliate_amount_usd").alias("affiliate_amount_usd_prev"),
            F.col("exchange_rate").alias("exchange_rate_prev"),
            F.col("total_price").alias("total_price_prev"),
            F.col("taxes").alias("taxes_prev"),
            F.col("iva").alias("iva_prev"),
            F.col("affiliate_amount").alias("affiliate_amount_prev"),
            F.col("affiliate_id").alias("affiliate_id_prev"),
            F.col("affiliate_name").alias("affiliate_name_prev"),
            F.col("subid").alias("subid_prev"),
            F.col("subid2").alias("subid2_prev"),
            F.col("subid3").alias("subid3_prev"),
            F.col("subid4").alias("subid4_prev"),
            F.col("subid5").alias("subid5_prev"),
            F.col("upsell_parent_receipt").alias("upsell_parent_receipt_prev"),
            F.col("account_id").alias("account_id_prev"),
            F.col("created_at_date").alias("created_at_date_prev"),
            F.col("created_at_hour").alias("created_at_hour_prev"),
            F.col("datetime_platform").alias("datetime_platform_prev"),
            F.col("created_at").alias("created_at_prev"),
        )
        .join(F.broadcast(batch_tids), on="transaction_id", how="inner")
        .dropDuplicates(["transaction_id"])
        .cache()
    )

    result_with_immutables = (
        result
        .join(current_immutables, on="transaction_id", how="left")
        .withColumn("client_name", F.coalesce(F.col("client_name"), F.col("client_name_prev")))
        .withColumn("client_email", F.coalesce(F.col("client_email"), F.col("client_email_prev")))
        .withColumn("client_phone", F.coalesce(F.col("client_phone"), F.col("client_phone_prev")))
        .withColumn("client_zip", F.coalesce(F.col("client_zip"), F.col("client_zip_prev")))
        .withColumn("client_country", F.coalesce(F.col("client_country"), F.col("client_country_prev")))
        .withColumn("client_state", F.coalesce(F.col("client_state"), F.col("client_state_prev")))
        .withColumn("client_city", F.coalesce(F.col("client_city"), F.col("client_city_prev")))
        .withColumn("client_street", F.coalesce(F.col("client_street"), F.col("client_street_prev")))
        .withColumn("product_name", F.coalesce(F.col("product_name"), F.col("product_name_prev")))
        .withColumn("product_sku", F.coalesce(F.col("product_sku"), F.col("product_sku_prev")))
        .withColumn("product_codename", F.coalesce(F.col("product_codename"), F.col("product_codename_prev")))
        .withColumn("product_id", F.coalesce(F.col("product_id"), F.col("product_id_prev")))
        .withColumn("offer_name", F.coalesce(F.col("offer_name"), F.col("offer_name_prev")))
        .withColumn("quantity", F.coalesce(F.col("quantity"), F.col("quantity_prev")))
        .withColumn("sales_type", F.coalesce(F.col("sales_type"), F.col("sales_type_prev")))
        .withColumn("vendor_name", F.coalesce(F.col("vendor_name"), F.col("vendor_name_prev")))
        .withColumn("total_collected_usd", F.coalesce(F.col("total_collected_usd"), F.col("total_collected_usd_prev")))
        .withColumn("total_price_usd", F.coalesce(F.col("total_price_usd"), F.col("total_price_usd_prev")))
        .withColumn("iva_usd", F.coalesce(F.col("iva_usd"), F.col("iva_usd_prev")))
        .withColumn("taxes_usd", F.coalesce(F.col("taxes_usd"), F.col("taxes_usd_prev")))
        .withColumn("affiliate_amount_usd", F.coalesce(F.col("affiliate_amount_usd"), F.col("affiliate_amount_usd_prev")))
        .withColumn("exchange_rate", F.coalesce(F.col("exchange_rate"), F.col("exchange_rate_prev")))
        .withColumn("total_price", F.coalesce(F.col("total_price"), F.col("total_price_prev")))
        .withColumn("taxes", F.coalesce(F.col("taxes"), F.col("taxes_prev")))
        .withColumn("iva", F.coalesce(F.col("iva"), F.col("iva_prev")))
        .withColumn("affiliate_amount", F.coalesce(F.col("affiliate_amount"), F.col("affiliate_amount_prev")))
        .withColumn("affiliate_id", F.coalesce(F.col("affiliate_id"), F.col("affiliate_id_prev")))
        .withColumn("affiliate_name", F.coalesce(F.col("affiliate_name"), F.col("affiliate_name_prev")))
        .withColumn("subid", F.coalesce(F.col("subid"), F.col("subid_prev")))
        .withColumn("subid2", F.coalesce(F.col("subid2"), F.col("subid2_prev")))
        .withColumn("subid3", F.coalesce(F.col("subid3"), F.col("subid3_prev")))
        .withColumn("subid4", F.coalesce(F.col("subid4"), F.col("subid4_prev")))
        .withColumn("subid5", F.coalesce(F.col("subid5"), F.col("subid5_prev")))
        .withColumn("upsell_parent_receipt", F.coalesce(F.col("upsell_parent_receipt"), F.col("upsell_parent_receipt_prev")))
        .withColumn("account_id", F.coalesce(F.col("account_id"), F.col("account_id_prev")))
        .withColumn("created_at_date", F.coalesce(F.col("created_at_date"), F.col("created_at_date_prev")))
        .withColumn("created_at_hour", F.coalesce(F.col("created_at_hour"), F.col("created_at_hour_prev")))
        .withColumn("datetime_platform", F.coalesce(F.col("datetime_platform"), F.col("datetime_platform_prev")))
        .withColumn("created_at", F.coalesce(F.col("created_at_prev"), F.col("created_at")))
        .drop(
            "client_name_prev",
            "client_email_prev",
            "client_phone_prev",
            "client_zip_prev",
            "client_country_prev",
            "client_state_prev",
            "client_city_prev",
            "client_street_prev",
            "product_name_prev",
            "product_sku_prev",
            "product_codename_prev",
            "product_id_prev",
            "offer_name_prev",
            "quantity_prev",
            "sales_type_prev",
            "vendor_name_prev",
            "total_collected_usd_prev",
            "total_price_usd_prev",
            "iva_usd_prev",
            "taxes_usd_prev",
            "affiliate_amount_usd_prev",
            "exchange_rate_prev",
            "total_price_prev",
            "taxes_prev",
            "iva_prev",
            "affiliate_amount_prev",
            "affiliate_id_prev",
            "affiliate_name_prev",
            "subid_prev",
            "subid2_prev",
            "subid3_prev",
            "subid4_prev",
            "subid5_prev",
            "upsell_parent_receipt_prev",
            "account_id_prev",
            "created_at_date_prev",
            "created_at_hour_prev",
            "datetime_platform_prev",
            "created_at_prev",
        )
    )

    untouched_silver = (
        current_silver
        .join(F.broadcast(batch_tids), on="transaction_id", how="left_anti")
    )

    upserted = result_with_immutables.unionByName(untouched_silver, allowMissingColumns=True)

    batch_tids.unpersist()
    current_immutables.unpersist()
    current_silver.unpersist()
else:
    upserted = result


print(f"[INFO] Writing {upserted.count()} rows to {OUTPUT_PATH}")
upserted.write.mode("overwrite").partitionBy("dt_proc").parquet(OUTPUT_PATH)

job.commit()
````

## Relacionados
[[00-Data-Lake]]
