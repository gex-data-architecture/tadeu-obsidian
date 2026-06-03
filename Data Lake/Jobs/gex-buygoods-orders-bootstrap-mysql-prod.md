---
tipo: job-glue
ambiente: prod
fluxo: 
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-01 13:19
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-buygoods-orders-bootstrap-mysql-prod

> Glue ETL · fluxo **—** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x2 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/buygoods_orders_bootstrap_mysql.py` |
| Criado | 2026-06-01 13:14:32.448000-03:00 |
| Modificado | 2026-06-01 13:14:32.448000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--DB_TABLE` | buygoods_silver_orders_v2 |
| `--GLUE_CONNECTION_NAME` | gex-mysql-connection-prod |
| `--TARGET_DATABASE` | instituto_experience |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-01 13:19 | SUCCEEDED | 37s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/buygoods_orders_bootstrap_mysql.py` — baixado do S3 (read-only).

````python
"""
Glue Job: buygoods_bootstrap_mysql_tables  (one-time / idempotent)
=================================================================
Cria as tabelas finais e de staging no MySQL instituto_experience que o job
buygoods_silver_to_mysql precisa que ja existam:
  - instituto_experience.buygoods_silver_orders        (final)
  - instituto_experience.buygoods_silver_orders_old    (staging)

Roda DENTRO da VPC (via Glue Connection) porque o RDS e privado.
Usa CREATE TABLE IF NOT EXISTS (idempotente, NAO dropa dados existentes).
Credenciais lidas da Glue Connection via extract_jdbc_conf (sem Secrets Manager).

Schema = id BIGINT PK + 61 colunas da silver + dt_proc (coluna de particao
incluida no DataFrame lido via from_catalog).

Parametros:
  --GLUE_CONNECTION_NAME (req)  ex: gex-mysql-connection-prod
  --DB_TABLE             (opt)  default: buygoods_silver_orders
"""

import re
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark import SparkConf
from pyspark.context import SparkContext


def get_optional_arg(name: str, default: str) -> str:
    token = f"--{name}"
    if token in sys.argv:
        idx = sys.argv.index(token)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return default


MYSQL_TABLE = get_optional_arg("DB_TABLE", "buygoods_silver_orders")
STAGING_TABLE = f"{MYSQL_TABLE}_old"
DEFAULT_DATABASE = get_optional_arg("TARGET_DATABASE", "instituto_experience")


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
        "?useSSL=true"
        "&serverTimezone=UTC"
        "&rewriteBatchedStatements=true"
    )


class JdbcExecutor:
    def __init__(self, spark, jdbc_url: str, user: str, password: str):
        self._jvm = spark._jvm
        props = self._jvm.java.util.Properties()
        props.setProperty("user", user)
        props.setProperty("password", password)
        self._jvm.java.lang.Class.forName("com.mysql.cj.jdbc.Driver")
        self._conn = self._jvm.java.sql.DriverManager.getConnection(jdbc_url, props)

    def execute(self, sql: str) -> None:
        stmt = self._conn.createStatement()
        try:
            stmt.execute(sql)
        finally:
            stmt.close()

    def fetch_scalar_int(self, sql: str) -> int:
        stmt = self._conn.createStatement()
        try:
            rs = stmt.executeQuery(sql)
            try:
                return int(rs.getLong(1)) if rs.next() else 0
            finally:
                rs.close()
        finally:
            stmt.close()

    def table_exists(self, database: str, table: str) -> bool:
        return self.fetch_scalar_int(
            "SELECT COUNT(*) FROM information_schema.tables "
            f"WHERE table_schema = '{database}' AND table_name = '{table}'"
        ) > 0

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass


# Schema espelhando gex_db_develop_silver.buygoods_orders (+ id + dt_proc).
COLUMNS_DDL = """
  id BIGINT NOT NULL,
  transaction_id VARCHAR(64),
  transaction_type VARCHAR(32),
  payment_status VARCHAR(32),
  cancel_reason VARCHAR(255),
  platform VARCHAR(64),
  client_name VARCHAR(255),
  client_email VARCHAR(255),
  client_phone VARCHAR(64),
  client_zip VARCHAR(32),
  client_country VARCHAR(64),
  client_state VARCHAR(128),
  client_city VARCHAR(128),
  client_street VARCHAR(512),
  product_name VARCHAR(512),
  product_sku VARCHAR(128),
  product_codename VARCHAR(128),
  product_id INT,
  offer_name VARCHAR(512),
  quantity INT,
  sales_type VARCHAR(64),
  vendor_name VARCHAR(128),
  product_cost DECIMAL(12,4),
  product_cost_usd DECIMAL(10,2),
  total_collected_usd DECIMAL(10,2),
  total_price_usd DECIMAL(10,2),
  iva_usd DECIMAL(10,2),
  taxes_usd DECIMAL(10,2),
  affiliate_amount_usd DECIMAL(10,2),
  exchange_rate DECIMAL(10,4),
  total_price DECIMAL(12,4),
  taxes DECIMAL(12,4),
  iva DECIMAL(12,4),
  affiliate_amount DECIMAL(12,4),
  commission_usd DECIMAL(10,2),
  commission DECIMAL(12,4),
  total_refund_usd DECIMAL(10,2),
  total_refund DECIMAL(12,4),
  refund_fee_usd DECIMAL(10,2),
  refund_fee DECIMAL(12,4),
  chargeback_fee_usd DECIMAL(10,2),
  chargeback_fee DECIMAL(12,4),
  date_refunded DATE,
  datetime_refunded_platform VARCHAR(64),
  affiliate_id VARCHAR(64),
  account_id VARCHAR(64),
  affiliate_name VARCHAR(255),
  is_house_traffic TINYINT(1),
  utm_source VARCHAR(1024),
  utm_content VARCHAR(1024),
  utm_campaign VARCHAR(1024),
  utm_term VARCHAR(1024),
  utm_medium VARCHAR(1024),
  upsell_parent_receipt VARCHAR(128),
  created_at_date DATE,
  created_at_hour VARCHAR(16),
  datetime_platform VARCHAR(64),
  created_at DATETIME,
  updated_at DATETIME,
  pipeline_updated_at VARCHAR(64),
  dt_proc VARCHAR(32),
  PRIMARY KEY (id)
"""


def create_table_sql(table: str) -> str:
    return (
        f"CREATE TABLE IF NOT EXISTS {quote_ident(table)} (\n"
        f"{COLUMNS_DDL}\n"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    )


args = getResolvedOptions(sys.argv, ["JOB_NAME", "GLUE_CONNECTION_NAME"])
glue_connection_name = args["GLUE_CONNECTION_NAME"]

_conf = SparkConf()
sc = SparkContext(conf=_conf)
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

print(f"[1] Extracting JDBC config from Glue Connection ({glue_connection_name})...")
jdbc_conf = glue_context.extract_jdbc_conf(glue_connection_name)
raw_url = jdbc_conf.get("url") or jdbc_conf.get("fullUrl", "")
user = jdbc_conf.get("user") or jdbc_conf.get("username", "")
password = jdbc_conf.get("password", "")
host, port, database = parse_jdbc_url(raw_url)
jdbc_url = build_jdbc_url(host, port, database)
print(f"[1] OK host={host} port={port} db={database}")

executor = JdbcExecutor(spark, jdbc_url, user, password)
try:
    for tbl in (MYSQL_TABLE, STAGING_TABLE):
        existed = executor.table_exists(database, tbl)
        print(f"[2] Table {database}.{tbl} exists_before={existed} -> CREATE IF NOT EXISTS")
        executor.execute(create_table_sql(tbl))
        rows = executor.fetch_scalar_int(f"SELECT COUNT(*) FROM {quote_ident(tbl)}")
        print(f"[2] OK {database}.{tbl} now exists; row_count={rows}")
finally:
    executor.close()

print("[FINAL] OK bootstrap complete")
job.commit()
````

## Relacionados
[[00-Data-Lake]]
