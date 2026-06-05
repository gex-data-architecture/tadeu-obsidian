---
tipo: job-glue
ambiente: prod
fluxo: silver-to-gold
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-03 13:39
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-silver-to-gold-prod

> Glue ETL · fluxo **silver-to-gold** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x10 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/silver_to_gold_clickbank.py` |
| Criado | 2026-04-16 11:33:24.636000-03:00 |
| Modificado | 2026-04-16 11:33:24.636000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--SOURCE_DATABASE` | gex_db_prod_silver |
| `--TARGET_DATABASE` | gex_db_prod_gold |
| `--target_bucket` | gex-datalake-gold-prod |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-03 13:39 | SUCCEEDED | 2m44s | — |
| 2026-06-03 11:43 | SUCCEEDED | 2m28s | — |
| 2026-06-03 11:38 | SUCCEEDED | 2m44s | — |
| 2026-06-03 09:42 | SUCCEEDED | 2m24s | — |
| 2026-06-03 09:38 | SUCCEEDED | 2m36s | — |
| 2026-06-03 07:41 | SUCCEEDED | 2m26s | — |
| 2026-06-03 07:36 | SUCCEEDED | 2m42s | — |
| 2026-06-03 05:41 | SUCCEEDED | 2m19s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/silver_to_gold_clickbank.py` — baixado do S3 (read-only).

````python
"""

Glue Job: gex-silver-to-gold-clickbank-{env}
Materializa a Gold ClickBank a partir da Silver atual, reproduzindo
as transformacoes do legado dashboard_gold_clickbank em PySpark.

Observacao:
  - Este primeiro corte preserva a regra legada de agrupamento por
    client_email + vendor_name + janela temporal de 4 horas.
  - A migracao para um agrupamento deterministico via upsell_parent_receipt
    pode ser feita depois, quando a Silver estiver validada.
"""

import sys
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType
from pyspark.sql.window import Window


args = getResolvedOptions(sys.argv, [
    "JOB_NAME", "SOURCE_DATABASE", "TARGET_DATABASE", "target_bucket"
])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
spark.conf.set("spark.sql.session.timeZone", "America/Sao_Paulo")

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

SOURCE_DB = args["SOURCE_DATABASE"]
TARGET_DB = args["TARGET_DATABASE"]
OUTPUT_PATH = f"s3://{args['target_bucket']}/gex_gold_clickbank/"

SOURCE_TABLE = "tb_gex_clickbank_physical_new"


COUNTRY_MAP = {
    "AD": "Andorra",
    "AE": "United Arab Emirates",
    "AF": "Afghanistan",
    "AG": "Antigua and Barbuda",
    "AL": "Albania",
    "AM": "Armenia",
    "AO": "Angola",
    "AR": "Argentina",
    "AT": "Austria",
    "AU": "Australia",
    "AZ": "Azerbaijan",
    "BA": "Bosnia and Herzegovina",
    "BB": "Barbados",
    "BD": "Bangladesh",
    "BE": "Belgium",
    "BF": "Burkina Faso",
    "BG": "Bulgaria",
    "BH": "Bahrain",
    "BI": "Burundi",
    "BJ": "Benin",
    "BN": "Brunei",
    "BO": "Bolivia",
    "BR": "Brazil",
    "BS": "Bahamas",
    "BT": "Bhutan",
    "BW": "Botswana",
    "BY": "Belarus",
    "BZ": "Belize",
    "CA": "Canada",
    "CD": "Democratic Republic of the Congo",
    "CF": "Central African Republic",
    "CG": "Republic of the Congo",
    "CH": "Switzerland",
    "CI": "Ivory Coast",
    "CL": "Chile",
    "CM": "Cameroon",
    "CN": "China",
    "CO": "Colombia",
    "CR": "Costa Rica",
    "CU": "Cuba",
    "CV": "Cape Verde",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DJ": "Djibouti",
    "DK": "Denmark",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "DZ": "Algeria",
    "EC": "Ecuador",
    "EE": "Estonia",
    "EG": "Egypt",
    "ER": "Eritrea",
    "ES": "Spain",
    "ET": "Ethiopia",
    "FI": "Finland",
    "FJ": "Fiji",
    "FR": "France",
    "GA": "Gabon",
    "GB": "United Kingdom",
    "GD": "Grenada",
    "GE": "Georgia",
    "GH": "Ghana",
    "GM": "Gambia",
    "GN": "Guinea",
    "GQ": "Equatorial Guinea",
    "GR": "Greece",
    "GT": "Guatemala",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HN": "Honduras",
    "HR": "Croatia",
    "HT": "Haiti",
    "HU": "Hungary",
    "ID": "Indonesia",
    "IE": "Ireland",
    "IL": "Israel",
    "IN": "India",
    "IQ": "Iraq",
    "IR": "Iran",
    "IS": "Iceland",
    "IT": "Italy",
    "JM": "Jamaica",
    "JO": "Jordan",
    "JP": "Japan",
    "KE": "Kenya",
    "KG": "Kyrgyzstan",
    "KH": "Cambodia",
    "KI": "Kiribati",
    "KM": "Comoros",
    "KN": "Saint Kitts and Nevis",
    "KP": "North Korea",
    "KR": "South Korea",
    "KW": "Kuwait",
    "KZ": "Kazakhstan",
    "LA": "Laos",
    "LB": "Lebanon",
    "LC": "Saint Lucia",
    "LI": "Liechtenstein",
    "LK": "Sri Lanka",
    "LR": "Liberia",
    "LS": "Lesotho",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "LY": "Libya",
    "MA": "Morocco",
    "MC": "Monaco",
    "MD": "Moldova",
    "ME": "Montenegro",
    "MG": "Madagascar",
    "MH": "Marshall Islands",
    "MK": "North Macedonia",
    "ML": "Mali",
    "MM": "Myanmar",
    "MN": "Mongolia",
    "MR": "Mauritania",
    "MT": "Malta",
    "MU": "Mauritius",
    "MV": "Maldives",
    "MW": "Malawi",
    "MX": "Mexico",
    "MY": "Malaysia",
    "MZ": "Mozambique",
    "NA": "Namibia",
    "NE": "Niger",
    "NG": "Nigeria",
    "NI": "Nicaragua",
    "NL": "Netherlands",
    "NO": "Norway",
    "NP": "Nepal",
    "NR": "Nauru",
    "NZ": "New Zealand",
    "OM": "Oman",
    "PA": "Panama",
    "PE": "Peru",
    "PG": "Papua New Guinea",
    "PH": "Philippines",
    "PK": "Pakistan",
    "PL": "Poland",
    "PT": "Portugal",
    "PW": "Palau",
    "PY": "Paraguay",
    "QA": "Qatar",
    "RO": "Romania",
    "RS": "Serbia",
    "RU": "Russia",
    "RW": "Rwanda",
    "SA": "Saudi Arabia",
    "SB": "Solomon Islands",
    "SC": "Seychelles",
    "SD": "Sudan",
    "SE": "Sweden",
    "SG": "Singapore",
    "SI": "Slovenia",
    "SK": "Slovakia",
    "SL": "Sierra Leone",
    "SM": "San Marino",
    "SN": "Senegal",
    "SO": "Somalia",
    "SR": "Suriname",
    "SS": "South Sudan",
    "ST": "Sao Tome and Principe",
    "SV": "El Salvador",
    "SY": "Syria",
    "SZ": "Eswatini",
    "TD": "Chad",
    "TG": "Togo",
    "TH": "Thailand",
    "TJ": "Tajikistan",
    "TL": "Timor-Leste",
    "TM": "Turkmenistan",
    "TN": "Tunisia",
    "TO": "Tonga",
    "TR": "Turkey",
    "TT": "Trinidad and Tobago",
    "TV": "Tuvalu",
    "TZ": "Tanzania",
    "UA": "Ukraine",
    "UG": "Uganda",
    "US": "United States",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VA": "Vatican City",
    "VC": "Saint Vincent and the Grenadines",
    "VE": "Venezuela",
    "VN": "Vietnam",
    "VU": "Vanuatu",
    "WS": "Samoa",
    "YE": "Yemen",
    "ZA": "South Africa",
    "ZM": "Zambia",
    "ZW": "Zimbabwe",
}


def read_silver(table_name: str) -> DataFrame:
    return glueContext.create_dynamic_frame.from_catalog(
        database=SOURCE_DB,
        table_name=table_name,
    ).toDF()


country_map_expr = F.create_map(*[value for item in COUNTRY_MAP.items() for value in (F.lit(item[0]), F.lit(item[1]))])

silver = read_silver(SOURCE_TABLE)

base = (
    silver
    .filter((F.col("created_at_date") >= F.lit("2026-01-01")) | F.col("created_at_date").isNull())
    .withColumn(
        "created_at_ts",
        F.to_timestamp(
            F.concat_ws(" ", F.col("created_at_date"), F.col("created_at_hour")),
            "yyyy-MM-dd HH:mm:ss",
        ),
    )
)

# Agrupamento determinístico: receipt + vendor_name
# CASE: se UPSELL, usar upsell_parent_receipt; senão, usar receipt base derivado do transaction_id
base = base.withColumn(
    "group_key",
    F.concat(
        F.coalesce(F.col("upsell_parent_receipt"), F.regexp_extract(F.col("transaction_id"), r"^([^-]+)", 1)),
        F.lit("_"),
        F.col("vendor_name")
    )
)

classified = base.withColumn(
    "funnel_type",
    F.when(F.upper(F.col("product_sku")) == F.lit("PRIORITYSHIPPING"), F.lit("order_bump"))
     .when(F.trim(F.lower(F.col("sales_type"))).like("produto principal%"), F.lit("main"))
     .when(F.lower(F.col("sales_type")) == F.lit("order bump"), F.lit("order_bump"))
     .when((F.lower(F.col("sales_type")) == F.lit("venda de funil")) & F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).like("%upsell 1%"), F.lit("upsell1"))
     .when((F.lower(F.col("sales_type")) == F.lit("venda de funil")) & F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).like("%upsell 2%"), F.lit("upsell2"))
     .when((F.lower(F.col("sales_type")) == F.lit("venda de funil")) & F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).like("%upsell 3%"), F.lit("upsell3"))
     .when((F.lower(F.col("sales_type")) == F.lit("venda de funil")) & F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).like("%downsell 1%"), F.lit("downsell1"))
     .when((F.lower(F.col("sales_type")) == F.lit("venda de funil")) & F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).like("%downsell 2%"), F.lit("downsell2"))
     .when((F.lower(F.col("sales_type")) == F.lit("venda de funil")) & F.lower(F.coalesce(F.col("offer_name"), F.lit(""))).like("%downsell 3%"), F.lit("downsell3"))
     .when((F.lower(F.col("sales_type")) == F.lit("venda de funil")) & (F.col("offer_name").isNull() | (F.trim(F.col("offer_name")) == F.lit(""))), F.lit("funil_sem_offer"))
     .when(F.lower(F.col("sales_type")) == F.lit("venda de funil"), F.lit("funil_sem_offer"))
     .otherwise(F.lit("other"))
)

main_by_group = (
    classified
    .groupBy("group_key")
    .agg(
        F.max(F.when(F.col("funnel_type") == "main", F.col("product_name"))).alias("main_product_name"),
        F.max(F.when(F.col("funnel_type") == "main", F.col("offer_name"))).alias("main_offer_name"),
        F.max(F.when(F.col("funnel_type") == "main", F.col("product_sku"))).alias("main_product_sku"),
    )
)

gold = (
    classified.alias("c")
    .groupBy("group_key")
    .agg(
        F.max(F.when(F.upper(F.col("product_sku")) == "PRIORITYSHIPPING", F.lit(1)).otherwise(F.lit(0))).alias("has_priorityshipping"),
        F.min(F.when(F.upper(F.col("product_sku")) == "PRIORITYSHIPPING", F.col("transaction_id"))).alias("priority_transaction_id"),
        F.min(F.when(F.col("funnel_type") == "main", F.col("transaction_id"))).alias("main_transaction_id"),
        F.min("transaction_id").alias("min_transaction_id"),
        F.countDistinct("payment_status").alias("payment_status_distinct_count"),
        F.max("payment_status").alias("payment_status_max"),
        F.max(F.when(F.col("payment_status") == "chargeback", F.lit(1)).otherwise(F.lit(0))).alias("has_chargeback_status"),
        F.max(F.when(F.col("payment_status") == "refunded", F.lit(1)).otherwise(F.lit(0))).alias("has_refunded_status"),
        F.max(F.when(F.col("payment_status") == "refunded_partial", F.lit(1)).otherwise(F.lit(0))).alias("has_refunded_partial_status"),
        F.max(F.when(F.col("payment_status") == "approved", F.lit(1)).otherwise(F.lit(0))).alias("has_approved_status"),
        F.max(F.when((F.col("funnel_type") == "main") & (F.col("payment_status") == "refunded"), F.lit(1)).otherwise(F.lit(0))).alias("has_main_refunded_status"),
        F.max("client_name").alias("client_name"),
        F.max("client_phone").alias("client_phone"),
        F.max("client_zip").alias("client_zip"),
        F.max("client_country").alias("client_country_raw"),
        F.max("client_state").alias("client_state"),
        F.max("client_city").alias("client_city"),
        F.max("client_street").alias("client_street"),
        F.max(F.when(F.col("funnel_type") == "main", F.col("product_name"))).alias("group_main_product_name"),
        F.max(F.when(F.col("funnel_type") == "main", F.col("offer_name"))).alias("group_main_offer_name"),
        F.max(F.when(F.col("funnel_type") == "main", F.col("product_sku"))).alias("group_main_product_sku"),
        F.round(F.sum("product_cost"), 4).alias("product_cost"),
        F.round(F.sum("product_cost_usd"), 2).alias("product_cost_usd"),
        F.sum("quantity").alias("quantity"),
        F.max(F.when(F.col("funnel_type") == "main", F.col("quantity"))).alias("quantity_principal"),
        F.round(F.sum("total_price"), 4).alias("total_price"),
        F.round(F.sum("total_price_usd"), 2).alias("total_price_usd"),
        F.round(F.sum("taxes"), 4).alias("taxes"),
        F.round(F.sum("taxes_usd"), 2).alias("taxes_usd"),
        F.round(F.sum("total_refund"), 4).alias("total_refund"),
        F.round(F.sum("total_refund_usd"), 2).alias("total_refund_usd"),
        F.round(F.sum(F.when(F.col("is_house_traffic") == 1, F.coalesce(F.col("commission"), F.lit(0)) + F.coalesce(F.col("affiliate_amount"), F.lit(0))).otherwise(F.col("commission"))), 4).alias("commission"),
        F.round(F.sum(F.when(F.col("is_house_traffic") == 1, F.coalesce(F.col("commission_usd"), F.lit(0)) + F.coalesce(F.col("affiliate_amount_usd"), F.lit(0))).otherwise(F.col("commission_usd"))), 2).alias("commission_usd"),
        F.round(F.sum(F.when(F.col("is_house_traffic") == 1, F.lit(0)).otherwise(F.col("affiliate_amount"))), 4).alias("affiliate_amount"),
        F.round(F.sum(F.when(F.col("is_house_traffic") == 1, F.lit(0)).otherwise(F.col("affiliate_amount_usd"))), 2).alias("affiliate_amount_usd"),
        F.round(F.sum(F.when(F.col("is_house_traffic") == 1, F.coalesce(F.col("affiliate_amount"), F.lit(0))).otherwise(F.lit(0))), 4).alias("revenue_afiliado"),
        F.round(F.sum(F.when(F.col("is_house_traffic") == 1, F.coalesce(F.col("affiliate_amount_usd"), F.lit(0))).otherwise(F.lit(0))), 2).alias("revenue_afiliado_usd"),
        F.sum(F.when(F.col("funnel_type") == "upsell1", 1).otherwise(0)).alias("has_upsell"),
        F.sum(F.when(F.col("funnel_type") == "upsell2", 1).otherwise(0)).alias("has_upsell2"),
        F.sum(F.when(F.col("funnel_type") == "upsell3", 1).otherwise(0)).alias("has_upsell3"),
        F.sum(F.when(F.col("funnel_type") == "downsell1", 1).otherwise(0)).alias("has_downsell"),
        F.sum(F.when(F.col("funnel_type") == "downsell2", 1).otherwise(0)).alias("has_downsell2"),
        F.sum(F.when(F.col("funnel_type") == "downsell3", 1).otherwise(0)).alias("has_downsell3"),
        F.sum(F.when(F.col("funnel_type") == "order_bump", 1).otherwise(0)).alias("has_order_bump"),
        F.round(F.sum(F.when(F.col("funnel_type") == "upsell1", F.col("total_price")).otherwise(F.lit(0))), 2).alias("total_price_upsell"),
        F.round(F.sum(F.when(F.col("funnel_type") == "upsell1", F.col("total_price_usd")).otherwise(F.lit(0))), 2).alias("total_price_upsell_usd"),
        F.round(F.sum(F.when(F.col("funnel_type") == "upsell2", F.col("total_price")).otherwise(F.lit(0))), 2).alias("total_price_upsell2"),
        F.round(F.sum(F.when(F.col("funnel_type") == "upsell2", F.col("total_price_usd")).otherwise(F.lit(0))), 2).alias("total_price_upsell2_usd"),
        F.round(F.sum(F.when(F.col("funnel_type") == "upsell3", F.col("total_price")).otherwise(F.lit(0))), 2).alias("total_price_upsell3"),
        F.round(F.sum(F.when(F.col("funnel_type") == "upsell3", F.col("total_price_usd")).otherwise(F.lit(0))), 2).alias("total_price_upsell3_usd"),
        F.round(F.sum(F.when(F.col("funnel_type") == "downsell1", F.col("total_price")).otherwise(F.lit(0))), 2).alias("total_price_downsell"),
        F.round(F.sum(F.when(F.col("funnel_type") == "downsell1", F.col("total_price_usd")).otherwise(F.lit(0))), 2).alias("total_price_downsell_usd"),
        F.round(F.sum(F.when(F.col("funnel_type") == "downsell2", F.col("total_price")).otherwise(F.lit(0))), 2).alias("total_price_downsell2"),
        F.round(F.sum(F.when(F.col("funnel_type") == "downsell2", F.col("total_price_usd")).otherwise(F.lit(0))), 2).alias("total_price_downsell2_usd"),
        F.round(F.sum(F.when(F.col("funnel_type") == "downsell3", F.col("total_price")).otherwise(F.lit(0))), 2).alias("total_price_downsell3"),
        F.round(F.sum(F.when(F.col("funnel_type") == "downsell3", F.col("total_price_usd")).otherwise(F.lit(0))), 2).alias("total_price_downsell3_usd"),
        F.round(F.sum(F.when(F.col("funnel_type") == "order_bump", F.col("total_price")).otherwise(F.lit(0))), 2).alias("total_price_order_bump"),
        F.round(F.sum(F.when(F.col("funnel_type") == "order_bump", F.col("total_price_usd")).otherwise(F.lit(0))), 2).alias("total_price_order_bump_usd"),
        F.min("created_at_ts").alias("min_created_at_ts"),
        F.max("date_refunded").alias("date_refunded"),
        F.max("utm_source").alias("utm_source"),
        F.max("utm_medium").alias("utm_medium"),
        F.max("utm_content").alias("utm_content"),
        F.max("utm_term").alias("utm_term"),
        F.max("utm_campaign").alias("utm_campaign"),
        F.max("src").alias("src"),
        F.max("platform").alias("platform"),
        F.max("affiliate_name").alias("affiliate_name"),
        F.max("is_house_traffic").alias("is_house_traffic"),
        F.max("vendor_name").alias("vendor_name"),
        F.max("client_email").alias("client_email"),
    )
    .join(
        main_by_group.select(
            "group_key",
            "main_product_name",
            "main_offer_name",
            "main_product_sku",
        ),
        on=["group_key"],
        how="left",
    )
    .withColumn(
        "transaction_id",
        F.coalesce(
            F.col("main_transaction_id"),
            F.when(
                F.col("has_priorityshipping") == 1,
                F.regexp_extract(F.col("priority_transaction_id"), r"^([^-]+)", 1),
            ),
            F.col("min_transaction_id")
        )
    )
    .withColumn(
        "payment_status",
           F.when(F.col("has_chargeback_status") == 1, F.lit("chargeback"))
            .when((F.col("has_main_refunded_status") == 1) & (F.col("has_approved_status") == 1), F.lit("refunded_partial"))
            .when(F.col("has_refunded_status") == 1, F.lit("refunded"))
            .when(F.col("has_refunded_partial_status") == 1, F.lit("refunded_partial"))
            .when(F.col("payment_status_distinct_count") == 1, F.col("payment_status_max"))
            .otherwise(F.lit("approved"))
    )
    .withColumn("client_country", F.coalesce(country_map_expr[F.col("client_country_raw")], F.col("client_country_raw")))
    .withColumn("product_name", F.coalesce(F.col("group_main_product_name"), F.col("main_product_name")))
    .withColumn("offer_name", F.coalesce(F.col("group_main_offer_name"), F.col("main_offer_name")))
    .withColumn("product_sku", F.coalesce(F.col("group_main_product_sku"), F.col("main_product_sku")))
    .withColumn("coupon_code", F.lit(None).cast("string"))
    .withColumn("created_at_date", F.to_date(F.col("min_created_at_ts")))
    .withColumn("created_at_hour", F.date_format(F.col("min_created_at_ts"), "HH:mm:ss"))
)

gold = gold.select(
    F.col("transaction_id").cast("string"),
    F.col("payment_status").cast("string"),
    F.col("client_name").cast("string"),
    F.col("client_email").cast("string"),
    F.col("client_phone").cast("string"),
    F.col("client_zip").cast("string"),
    F.col("client_country").cast("string"),
    F.col("client_state").cast("string"),
    F.col("client_city").cast("string"),
    F.col("client_street").cast("string"),
    F.col("product_name").cast("string"),
    F.col("offer_name").cast("string"),
    F.col("product_sku").cast("string"),
    F.col("product_cost").cast(DecimalType(12, 4)),
    F.col("product_cost_usd").cast(DecimalType(10, 2)),
    F.col("quantity").cast("int"),
    F.col("quantity_principal").cast("int"),
    F.col("total_price").cast(DecimalType(12, 4)),
    F.col("total_price_usd").cast(DecimalType(10, 2)),
    F.col("taxes").cast(DecimalType(12, 4)),
    F.col("taxes_usd").cast(DecimalType(10, 2)),
    F.col("total_refund").cast(DecimalType(12, 4)),
    F.col("total_refund_usd").cast(DecimalType(10, 2)),
    F.col("commission").cast(DecimalType(12, 4)),
    F.col("commission_usd").cast(DecimalType(10, 2)),
    F.col("affiliate_amount").cast(DecimalType(12, 4)),
    F.col("affiliate_amount_usd").cast(DecimalType(10, 2)),
    F.col("revenue_afiliado").cast(DecimalType(12, 4)),
    F.col("revenue_afiliado_usd").cast(DecimalType(10, 2)),
    F.col("has_upsell").cast("int"),
    F.col("has_upsell2").cast("int"),
    F.col("has_upsell3").cast("int"),
    F.col("has_downsell").cast("int"),
    F.col("has_downsell2").cast("int"),
    F.col("has_downsell3").cast("int"),
    F.col("has_order_bump").cast("int"),
    F.col("total_price_upsell").cast(DecimalType(10, 2)),
    F.col("total_price_upsell_usd").cast(DecimalType(10, 2)),
    F.col("total_price_upsell2").cast(DecimalType(10, 2)),
    F.col("total_price_upsell2_usd").cast(DecimalType(10, 2)),
    F.col("total_price_upsell3").cast(DecimalType(10, 2)),
    F.col("total_price_upsell3_usd").cast(DecimalType(10, 2)),
    F.col("total_price_downsell").cast(DecimalType(10, 2)),
    F.col("total_price_downsell_usd").cast(DecimalType(10, 2)),
    F.col("total_price_downsell2").cast(DecimalType(10, 2)),
    F.col("total_price_downsell2_usd").cast(DecimalType(10, 2)),
    F.col("total_price_downsell3").cast(DecimalType(10, 2)),
    F.col("total_price_downsell3_usd").cast(DecimalType(10, 2)),
    F.col("total_price_order_bump").cast(DecimalType(10, 2)),
    F.col("total_price_order_bump_usd").cast(DecimalType(10, 2)),
    F.col("coupon_code").cast("string"),
    F.col("created_at_date").cast("date"),
    F.col("created_at_hour").cast("string"),
    F.col("date_refunded").cast("string"),
    F.col("utm_source").cast("string"),
    F.col("utm_medium").cast("string"),
    F.col("utm_content").cast("string"),
    F.col("utm_term").cast("string"),
    F.col("utm_campaign").cast("string"),
    F.col("src").cast("string"),
    F.col("platform").cast("string"),
    F.col("affiliate_name").cast("string"),
    F.col("vendor_name").cast("string"),
    F.col("is_house_traffic").cast("int"),
)

# A Gold alimenta dashboard e tem volume administravel; gravar particionado por data
# melhora pruning no Athena/BI e limitar a 1 particao upstream evita small files por dia.
gold.repartition(1, "created_at_date").write.mode("overwrite").partitionBy("created_at_date").parquet(OUTPUT_PATH)

print(f"Gold ClickBank escrita em {OUTPUT_PATH}")
print(f"[DEBUG] SOURCE_DATABASE={SOURCE_DB} TARGET_DATABASE={TARGET_DB} TABLE={SOURCE_TABLE}")
print(f"[DEBUG] GOLD COUNT FINAL: {gold.count()} linhas gravadas")

job.commit()
````

## Relacionados
[[00-Data-Lake]]
