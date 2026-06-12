---
tipo: job-glue
ambiente: prod
fluxo: 
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-12 10:00
ultimo_estado: FAILED
tags: [datalake, glue-job]
---

# gex-gold-clickbank-buygoods-prod

> Glue ETL · fluxo **—** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x4 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/gold_clickbank_buygoods_build.py` |
| Criado | 2026-06-10 10:55:11.011000-03:00 |
| Modificado | 2026-06-10 11:45:30.665000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--BUYGOODS_TABLE` | tb_gex_gold_buygoods |
| `--CLICKBANK_TABLE` | gold_clickbank_aws |
| `--DB_TABLE` | tb_gex_gold_clickbank_buygoods |
| `--GLUE_CONNECTION_NAME` | gex-mysql-connection-prod |
| `--GOLD_S3_PREFIX` | gex_gold_clickbank_buygoods |
| `--MIN_ROWS_THRESHOLD` | 100 |
| `--TARGET_DATABASE` | instituto_experience |
| `--target_bucket` | gex-datalake-gold-prod |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-12 10:00 | FAILED | 54s | An error occurred while calling o116.execute. Data truncation: Data too long for column 'client_street' at row 48906 |
| 2026-06-12 07:59 | FAILED | 1m3s | An error occurred while calling o116.execute. Data truncation: Data too long for column 'client_street' at row 48648 |
| 2026-06-12 06:03 | FAILED | 1m24s | An error occurred while calling o116.execute. Data truncation: Data too long for column 'client_street' at row 48522 |
| 2026-06-12 04:01 | FAILED | 1m15s | An error occurred while calling o116.execute. Data truncation: Data too long for column 'client_street' at row 48406 |
| 2026-06-12 01:59 | FAILED | 59s | An error occurred while calling o116.execute. Data truncation: Data too long for column 'client_street' at row 48225 |
| 2026-06-11 23:58 | FAILED | 54s | An error occurred while calling o116.execute. Data truncation: Data too long for column 'client_street' at row 47951 |
| 2026-06-11 21:59 | FAILED | 1m3s | An error occurred while calling o116.execute. Data truncation: Data too long for column 'client_street' at row 47468 |
| 2026-06-11 20:00 | FAILED | 1m3s | An error occurred while calling o116.execute. Data truncation: Data too long for column 'client_street' at row 47190 |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/gold_clickbank_buygoods_build.py` — baixado do S3 (read-only).

````python
"""
Glue Job: gold_clickbank_buygoods_build
=======================================
Constroi a gold COMBINADA instituto_experience.dashboard_gold_clickbank_buygoods
= UNIAO de:
  - ClickBank: gold_clickbank_aws            (todas as 64 colunas)
  - BuyGoods : tb_gex_gold_buygoods           (mesmas 64 colunas; vendor_name = CAST(account_id AS CHAR))
alinhada ao schema da gold ClickBank (64 colunas). Reproduz a procedure
refresh_dashboard_gold_clickbank_buygoods VERBATIM, no padrao server-side MySQL
(stage + INSERT + swap atomico) + espelho parquet no S3 (catalogo/Athena).

Obs: a procedure le 'dashboard_gold_buygoods' e 'dashboard_gold_clickbank' (nomes
legados). No nosso pipeline as tabelas atuais sao 'tb_gex_gold_buygoods' (renomeada)
e 'gold_clickbank_aws'. Parametrizado por --CLICKBANK_TABLE / --BUYGOODS_TABLE.

=== CREDENCIAIS === Glue Connection via extract_jdbc_conf (sem Secrets Manager).

Parametros (--CHAVE valor):
  --JOB_NAME             (req)
  --GLUE_CONNECTION_NAME (req)   ex: gex-mysql-connection-prod
  --target_bucket        (req)   bucket gold
  --CLICKBANK_TABLE      (opt)   default: gold_clickbank_aws
  --BUYGOODS_TABLE       (opt)   default: tb_gex_gold_buygoods
  --DB_TABLE             (opt)   default: dashboard_gold_clickbank_buygoods
  --TARGET_DATABASE      (opt)   default: instituto_experience
  --MIN_ROWS_THRESHOLD   (opt)   default: 100
  --GOLD_S3_PREFIX       (opt)   default: gex_gold_clickbank_buygoods
"""

import re
import sys
import time

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext


def get_optional_arg(name: str, default: str) -> str:
    token = f"--{name}"
    if token in sys.argv:
        idx = sys.argv.index(token)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return default


# 64 colunas (schema da gold ClickBank) — ordem da procedure do Tadeu.
COLS_64 = [
    "transaction_id", "payment_status", "client_name", "client_email", "client_phone", "client_zip",
    "client_country", "client_state", "client_city", "client_street", "product_name", "offer_name",
    "product_sku", "product_cost", "product_cost_usd", "quantity", "quantity_principal", "total_price",
    "total_price_usd", "taxes", "taxes_usd", "total_refund", "total_refund_usd", "commission",
    "commission_usd", "affiliate_amount", "affiliate_amount_usd", "revenue_afiliado", "revenue_afiliado_usd", "has_upsell",
    "has_upsell2", "has_upsell3", "has_downsell", "has_downsell2", "has_downsell3", "has_order_bump",
    "total_price_upsell", "total_price_upsell_usd", "total_price_upsell2", "total_price_upsell2_usd", "total_price_upsell3", "total_price_upsell3_usd",
    "total_price_downsell", "total_price_downsell_usd", "total_price_downsell2", "total_price_downsell2_usd", "total_price_downsell3", "total_price_downsell3_usd",
    "total_price_order_bump", "total_price_order_bump_usd", "coupon_code", "created_at_date", "created_at_hour", "date_refunded",
    "utm_source", "utm_medium", "utm_content", "utm_term", "utm_campaign", "src",
    "platform", "affiliate_name", "vendor_name", "is_house_traffic",
]

CLICKBANK_TABLE = get_optional_arg("CLICKBANK_TABLE", "gold_clickbank_aws")
BUYGOODS_TABLE = get_optional_arg("BUYGOODS_TABLE", "tb_gex_gold_buygoods")
MYSQL_TABLE = get_optional_arg("DB_TABLE", "dashboard_gold_clickbank_buygoods")
STAGING_TABLE = f"{MYSQL_TABLE}_stage"
BACKUP_TABLE = f"{MYSQL_TABLE}_old"
DEFAULT_DATABASE = get_optional_arg("TARGET_DATABASE", "instituto_experience")
GOLD_S3_PREFIX = get_optional_arg("GOLD_S3_PREFIX", "gex_gold_clickbank_buygoods").strip("/")


def quote_ident(name: str) -> str:
    return f"`{name.replace('`', '``')}`"


def parse_jdbc_url(url: str):
    with_db = re.match(r"jdbc:mysql://([^:/]+):(\d+)/([^?]+)", url or "")
    if with_db:
        return with_db.group(1), int(with_db.group(2)), with_db.group(3)
    without_db = re.match(r"jdbc:mysql://([^:/]+):(\d+)$", url or "")
    if without_db:
        return without_db.group(1), int(without_db.group(2)), DEFAULT_DATABASE
    raise ValueError(f"Cannot parse JDBC URL: {url!r}")


def build_jdbc_url(host: str, port: int, database: str) -> str:
    return (
        f"jdbc:mysql://{host}:{port}/{database}"
        "?useSSL=true&serverTimezone=UTC&rewriteBatchedStatements=true"
    )


class JdbcExecutor:
    def __init__(self, spark, jdbc_url, user, password):
        self._jvm = spark._jvm
        props = self._jvm.java.util.Properties()
        props.setProperty("user", user)
        props.setProperty("password", password)
        self._jvm.java.lang.Class.forName("com.mysql.cj.jdbc.Driver")
        self._conn = self._jvm.java.sql.DriverManager.getConnection(jdbc_url, props)

    def execute(self, sql):
        stmt = self._conn.createStatement()
        try:
            stmt.execute(sql)
        finally:
            stmt.close()

    def fetch_scalar_int(self, sql):
        stmt = self._conn.createStatement()
        try:
            rs = stmt.executeQuery(sql)
            try:
                return int(rs.getLong(1)) if rs.next() else 0
            finally:
                rs.close()
        finally:
            stmt.close()

    def fetch_columns(self, database, table):
        stmt = self._conn.createStatement()
        try:
            rs = stmt.executeQuery(
                "SELECT column_name FROM information_schema.columns "
                f"WHERE table_schema = '{database}' AND table_name = '{table}'"
            )
            cols = set()
            try:
                while rs.next():
                    cols.add(rs.getString(1).lower())
            finally:
                rs.close()
            return cols
        finally:
            stmt.close()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


args = getResolvedOptions(sys.argv, ["JOB_NAME", "GLUE_CONNECTION_NAME", "target_bucket"])
start = time.time()
glue_context = GlueContext(SparkContext())
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

glue_connection_name = args["GLUE_CONNECTION_NAME"]
target_bucket = args["target_bucket"]
min_rows_threshold = int(get_optional_arg("MIN_ROWS_THRESHOLD", "100"))

print(f"[STEP 1] Credenciais via {glue_connection_name} ...")
jdbc_conf = glue_context.extract_jdbc_conf(glue_connection_name)
raw_url = jdbc_conf.get("url") or jdbc_conf.get("fullUrl", "")
user = jdbc_conf.get("user") or jdbc_conf.get("username", "")
password = jdbc_conf.get("password", "")
host, port, database = parse_jdbc_url(raw_url)
jdbc_url = build_jdbc_url(host, port, database)
print(f"[STEP 1] OK host={host} db={database}")

clickbank_fqtn = quote_ident(CLICKBANK_TABLE)
buygoods_fqtn = quote_ident(BUYGOODS_TABLE)
stage_fqtn = quote_ident(STAGING_TABLE)
final_fqtn = quote_ident(MYSQL_TABLE)
backup_fqtn = quote_ident(BACKUP_TABLE)

cols_list = ", ".join(quote_ident(c) for c in COLS_64)
clickbank_values = ", ".join(quote_ident(c) for c in COLS_64)
# BuyGoods: vendor_name e NULL no BG -> usa account_id como texto (igual a procedure)
buygoods_values = ", ".join(
    "CAST(account_id AS CHAR)" if c == "vendor_name" else quote_ident(c) for c in COLS_64
)

executor = JdbcExecutor(spark, jdbc_url, user, password)
try:
    # Parity de schema: as 64 colunas precisam existir nas duas fontes.
    print("[STEP 2] Validando parity de schema (64 colunas) nas fontes...")
    for tbl in (CLICKBANK_TABLE, BUYGOODS_TABLE):
        cols = executor.fetch_columns(database, tbl)
        if not cols:
            raise RuntimeError(f"Tabela fonte {database}.{tbl} nao encontrada/sem colunas.")
        needed = COLS_64 if tbl == CLICKBANK_TABLE else [c for c in COLS_64 if c != "vendor_name"] + ["account_id"]
        missing = [c for c in needed if c.lower() not in cols]
        if missing:
            raise RuntimeError(f"Colunas ausentes em {database}.{tbl}: {missing}")
    print("[STEP 2] OK parity de schema confirmada")

    print(f"[STEP 3] DROP + CREATE stage {STAGING_TABLE} LIKE {CLICKBANK_TABLE} ...")
    executor.execute(f"DROP TABLE IF EXISTS {stage_fqtn}")
    executor.execute(f"CREATE TABLE {stage_fqtn} LIKE {clickbank_fqtn}")

    # A coluna 'id' (copiada via CREATE LIKE) e NOT NULL e sem auto_increment na
    # gold_clickbank_aws -> geramos um id sequencial unico via contador de sessao,
    # contínuo entre os 2 INSERTs (mesma conexao JDBC).
    cols_with_id = "`id`, " + cols_list
    executor.execute("SET @gex_rn := 0")

    print(f"[STEP 4] INSERT ClickBank ({CLICKBANK_TABLE}) -> stage ...")
    executor.execute(
        f"INSERT INTO {stage_fqtn} ({cols_with_id}) "
        f"SELECT (@gex_rn := @gex_rn + 1), {clickbank_values} FROM {clickbank_fqtn}"
    )
    print(f"[STEP 4] INSERT BuyGoods ({BUYGOODS_TABLE}) -> stage (vendor_name=CAST(account_id AS CHAR)) ...")
    executor.execute(
        f"INSERT INTO {stage_fqtn} ({cols_with_id}) "
        f"SELECT (@gex_rn := @gex_rn + 1), {buygoods_values} FROM {buygoods_fqtn}"
    )

    stage_count = executor.fetch_scalar_int(f"SELECT COUNT(*) FROM {stage_fqtn}")
    print(f"[STEP 5] stage_count={stage_count}")
    if stage_count < min_rows_threshold:
        raise RuntimeError(f"Gold combinada abaixo do threshold. stage_count={stage_count} threshold={min_rows_threshold}")

    print(f"[STEP 6] CREATE TABLE IF NOT EXISTS {MYSQL_TABLE} LIKE {CLICKBANK_TABLE} (auto-bootstrap)...")
    executor.execute(f"CREATE TABLE IF NOT EXISTS {final_fqtn} LIKE {clickbank_fqtn}")

    print("[STEP 7] Swap atomico (RENAME)...")
    executor.execute(f"DROP TABLE IF EXISTS {backup_fqtn}")
    executor.execute(f"RENAME TABLE {final_fqtn} TO {backup_fqtn}, {stage_fqtn} TO {final_fqtn}")
    executor.execute(f"DROP TABLE IF EXISTS {backup_fqtn}")
    print("[STEP 7] OK swap concluido")
finally:
    executor.close()

# Espelho S3 (parquet) p/ catalogo/Athena
output_path = f"s3://{target_bucket}/{GOLD_S3_PREFIX}/"
print(f"[STEP 8] Lendo {database}.{MYSQL_TABLE} e gravando parquet em {output_path} ...")
gold_df = glue_context.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": f"{database}.{MYSQL_TABLE}",
        "connectionName": glue_connection_name,
    },
).toDF()
s3_count = gold_df.count()
(
    gold_df.repartition(1, "created_at_date")
    .write.mode("overwrite")
    .partitionBy("created_at_date")
    .parquet(output_path)
)

elapsed = int(time.time() - start)
print(f"[FINAL] OK gold combinada em {elapsed}s | rows={stage_count} s3_rows={s3_count}")
job.commit()
````

## Relacionados
[[00-Data-Lake]]
