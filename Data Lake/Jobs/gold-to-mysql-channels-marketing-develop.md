---
tipo: job-glue
ambiente: develop
fluxo: to-mysql
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: —
ultimo_estado: —
tags: [datalake, glue-job]
---

# gold-to-mysql-channels-marketing-develop

> Glue ETL · fluxo **to-mysql** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x2 |
| Timeout (min) | 20 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-develop` |
| Script | `s3://gex-datalake-bronze-develop/scripts/glue_job_channels_marketing_to_mysql.py` |
| Criado | 2026-04-24 14:32:34.310000-03:00 |
| Modificado | 2026-04-24 17:35:14.926000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--BRONZE_BUCKET` | gex-datalake-bronze-develop |
| `--CONNECTION_NAME` | gex-mysql-connection-develop |
| `--GLUE_CONNECTION_NAME` | gex-mysql-connection-develop |
| `--MIN_ROWS_THRESHOLD` | 100 |
| `--MYSQL_TABLE` | dashboard_channels_marketing_aws |
| `--SOURCE_DATABASE` | gex_db_develop_gold |
| `--SOURCE_TABLE` | tb_gex_dashboard_channels_marketing |
| `--db_table` | dashboard_channels_marketing_aws |

## Últimas execuções

> Sem histórico de execuções (job nunca rodou ou sem acesso ao histórico).

## Script

> Fonte: `s3://gex-datalake-bronze-develop/scripts/glue_job_channels_marketing_to_mysql.py` — baixado do S3 (read-only).

````python
"""
Glue Job: gex-gold-to-mysql-channels-marketing

Replicates tb_gex_dashboard_channels_marketing from Glue Catalog/Athena
into MySQL using atomic table swap.

=== CREDENTIALS ===
  Credentials are read from the Glue Connection (gex-mysql-connection-prod)
  via glue_context.extract_jdbc_conf() — no Secrets Manager call needed.
  The Glue Connection must be attached to this job (already configured in Terraform).

=== PREREQUISITES ===
  MySQL must have these tables already created (run 01_ddl_mysql.sql once):
    - dashboard_channels_marketing_aws       (final table, read by Looker)
    - dashboard_channels_marketing_aws_new   (staging table)

=== JOB FLOW ===
  [STEP 1] Read source table from Glue Catalog
  [STEP 2] Load credentials from Glue Connection (VPC-internal, no Secrets Manager)
  [STEP 3] Sanity check — both MySQL tables must exist
  [STEP 4] TRUNCATE staging table (_new)
  [STEP 5] INSERT rows via Spark JDBC
  [STEP 6] Validate staging row count
  [STEP 7] Atomic RENAME TABLE swap
  [STEP 8] Recycle _old back into _new (ready for next run)

=== REQUIRED JOB PARAMETERS ===
  --JOB_NAME                 gex-gold-to-mysql-channels-marketing-prod
  --SOURCE_DATABASE          gex_db_prod_gold
  --SOURCE_TABLE             tb_gex_dashboard_channels_marketing
  --MYSQL_TABLE              dashboard_channels_marketing_aws
  --MIN_ROWS_THRESHOLD       100
  --GLUE_CONNECTION_NAME     gex-mysql-connection-prod

=== DEPENDENCIES ===
  * No pip dependencies — all DDL/DML via JVM (com.mysql.cj.jdbc.Driver loaded
    automatically by the attached Glue Connection)
  * Glue 4.0 / Spark 3.3 / Python 3.10
"""

import re
import sys
import time

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext


# ============================================================
# HELPERS
# ============================================================

DEFAULT_DATABASE = "instituto_experience"


def quote_ident(name: str) -> str:
    """Quote a MySQL identifier safely with backticks."""
    return f"`{name.replace('`', '``')}`"


def parse_jdbc_url(url: str):
    """
    Parse host, port, database from a JDBC MySQL URL.
    Accepts both formats returned by Glue Connection:
      - jdbc:mysql://host:port              → database = DEFAULT_DATABASE
      - jdbc:mysql://host:port/database     → database extracted
      - jdbc:mysql://host:port/database?p   → database extracted, params ignored
    """
    # With database (and optional query string)
    match = re.match(r"jdbc:mysql://([^:/]+):(\d+)/([^?]+)", url or "")
    if match:
        return match.group(1), int(match.group(2)), match.group(3)

    # Without database (short form returned by some Glue Connections)
    match = re.match(r"jdbc:mysql://([^:/]+):(\d+)$", url or "")
    if match:
        return match.group(1), int(match.group(2)), DEFAULT_DATABASE

    raise ValueError(f"Cannot parse JDBC URL: {url!r}")


def build_jdbc_url(host: str, port: int, database: str) -> str:
    return (
        f"jdbc:mysql://{host}:{port}/{database}"
        "?useSSL=true"
        "&serverTimezone=America/Sao_Paulo"
        "&rewriteBatchedStatements=true"
    )


class JdbcExecutor:
    """
    Executes DDL/DML on MySQL using the JVM JDBC driver loaded by the
    attached Glue Connection (com.mysql.cj.jdbc.Driver). Uses Py4J to reach
    JDBC directly — zero pip dependencies.
    """

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
        count = self.fetch_scalar_int(
            "SELECT COUNT(*) FROM information_schema.tables "
            f"WHERE table_schema = '{database}' AND table_name = '{table}'"
        )
        return count > 0

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass


# ============================================================
# MAIN
# ============================================================

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "SOURCE_DATABASE",
        "SOURCE_TABLE",
        "MYSQL_TABLE",
        "MIN_ROWS_THRESHOLD",
        "GLUE_CONNECTION_NAME",
    ],
)

start = time.time()

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
spark.conf.set("spark.sql.session.timeZone", "America/Sao_Paulo")
spark.conf.set("spark.sql.files.ignoreMissingFiles", "true")

job = Job(glue_context)
job.init(args["JOB_NAME"], args)

source_database = args["SOURCE_DATABASE"]
source_table = args["SOURCE_TABLE"]
mysql_table = args["MYSQL_TABLE"]
min_rows_threshold = int(args["MIN_ROWS_THRESHOLD"])
glue_connection_name = args["GLUE_CONNECTION_NAME"]

staging_table = f"{mysql_table}_new"
backup_table = f"{mysql_table}_old"

# --------------------------------------------------------------
# STEP 1 — Read source from Glue Catalog
# --------------------------------------------------------------
print(f"[STEP 1] Reading {source_database}.{source_table} from Glue Catalog...")
df = glue_context.create_dynamic_frame.from_catalog(
    database=source_database,
    table_name=source_table,
).toDF()

source_count = df.count()
print(f"[STEP 1] OK {source_count} rows read from source")

if source_count < min_rows_threshold:
    raise RuntimeError(
        f"Source row count below threshold. "
        f"source_count={source_count} threshold={min_rows_threshold}"
    )

# --------------------------------------------------------------
# STEP 2 — Load credentials from Glue Connection (VPC-internal)
# --------------------------------------------------------------
print(f"[STEP 2] Extracting JDBC config from Glue Connection ({glue_connection_name})...")
jdbc_conf = glue_context.extract_jdbc_conf(glue_connection_name)
print(f"[STEP 2] OK — raw url: {jdbc_conf.get('url', 'N/A')}")

raw_url = jdbc_conf.get("url") or jdbc_conf.get("fullUrl", "")
user = jdbc_conf.get("user") or jdbc_conf.get("username", "")
password = jdbc_conf.get("password", "")

host, port, database = parse_jdbc_url(raw_url)
jdbc_url = build_jdbc_url(host, port, database)

print(f"[STEP 2] OK credentials loaded — host={host} port={port} db={database}")

# --------------------------------------------------------------
# Open JVM JDBC connection for DDL
# --------------------------------------------------------------
executor = JdbcExecutor(spark, jdbc_url, user, password)

try:
    # ----------------------------------------------------------
    # STEP 3 — Sanity check: tables must already exist
    # ----------------------------------------------------------
    print("[STEP 3] Checking that MySQL tables exist...")
    if not executor.table_exists(database, mysql_table):
        raise RuntimeError(
            f"Final table {database}.{mysql_table} does not exist. "
            "Run 01_ddl_mysql.sql manually before running this job."
        )
    if not executor.table_exists(database, staging_table):
        raise RuntimeError(
            f"Staging table {database}.{staging_table} does not exist. "
            "Run 01_ddl_mysql.sql manually before running this job."
        )
    print("[STEP 3] OK both tables exist")

    # ----------------------------------------------------------
    # STEP 4 — Truncate staging
    # ----------------------------------------------------------
    print(f"[STEP 4] Truncating staging table {staging_table}...")
    executor.execute(f"TRUNCATE TABLE {quote_ident(staging_table)}")
    print("[STEP 4] OK staging truncated")

    # ----------------------------------------------------------
    # STEP 5 — Write via Spark JDBC (append to empty staging)
    # ----------------------------------------------------------
    print(f"[STEP 5] Writing {source_count} rows to MySQL staging via JDBC...")
    (
        df.write
        .mode("append")
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", staging_table)
        .option("user", user)
        .option("password", password)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .option("batchsize", "10000")
        .save()
    )
    print("[STEP 5] OK JDBC write completed")

    # ----------------------------------------------------------
    # STEP 6 — Validate staging row count
    # ----------------------------------------------------------
    print("[STEP 6] Validating staging row count...")
    staging_count = executor.fetch_scalar_int(
        f"SELECT COUNT(*) FROM {quote_ident(staging_table)}"
    )

    if staging_count < min_rows_threshold:
        raise RuntimeError(
            f"Staging row count below threshold. "
            f"staging_count={staging_count} threshold={min_rows_threshold}"
        )

    print(f"[STEP 6] OK staging_count={staging_count} (threshold={min_rows_threshold})")

    # ----------------------------------------------------------
    # STEP 7 — Atomic swap
    #   RENAME TABLE with two targets = single atomic MySQL operation.
    #   Looker Studio never sees a missing/empty table.
    # ----------------------------------------------------------
    print("[STEP 7] Executing atomic swap...")

    executor.execute(f"DROP TABLE IF EXISTS {quote_ident(backup_table)}")
    executor.execute(
        "RENAME TABLE "
        f"{quote_ident(mysql_table)} TO {quote_ident(backup_table)}, "
        f"{quote_ident(staging_table)} TO {quote_ident(mysql_table)}"
    )
    print("[STEP 7] OK atomic swap completed")

    # ----------------------------------------------------------
    # STEP 8 — Recycle _old back into _new (ready for next run)
    # ----------------------------------------------------------
    print("[STEP 8] Recycling backup as next staging...")
    executor.execute(
        f"RENAME TABLE {quote_ident(backup_table)} TO {quote_ident(staging_table)}"
    )
    executor.execute(f"TRUNCATE TABLE {quote_ident(staging_table)}")
    print("[STEP 8] OK staging ready for next run")

finally:
    executor.close()

elapsed = int(time.time() - start)
print(f"[FINAL] OK job completed in {elapsed}s")
job.commit()
````

## Relacionados
[[00-Data-Lake]]
