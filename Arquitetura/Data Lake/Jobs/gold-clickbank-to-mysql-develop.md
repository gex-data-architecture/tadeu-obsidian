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

# gold-clickbank-to-mysql-develop

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
| Script | `s3://gex-datalake-bronze-develop/scripts/glue_job_gold_clickbank_to_mysql.py` |
| Criado | 2026-04-27 14:53:11.563000-03:00 |
| Modificado | 2026-04-27 14:53:11.563000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--BRONZE_BUCKET` | gex-datalake-bronze-develop |
| `--CONNECTION_NAME` | gex-mysql-connection-develop |
| `--GLUE_CONNECTION_NAME` | gex-mysql-connection-develop |
| `--MIN_ROWS_THRESHOLD` | 100 |
| `--SOURCE_DATABASE` | gex_db_develop_gold |
| `--db_table` | gold_clickbank_aws |

## Últimas execuções

> Sem histórico de execuções (job nunca rodou ou sem acesso ao histórico).

## Script

> Fonte: `s3://gex-datalake-bronze-develop/scripts/glue_job_gold_clickbank_to_mysql.py` — baixado do S3 (read-only).

````python
"""
Glue Job: gex-gold-clickbank-to-mysql

Replicates tb_gex_gold_clickbank from Glue Catalog/Athena
into MySQL table gold_clickbank_aws using atomic table swap.

=== CREDENTIALS ===
  Credentials are read from the Glue Connection via
  glue_context.extract_jdbc_conf() (no Secrets Manager dependency).

=== TRANSFORMATIONS ===
    * Adds a sequential 'id' column = ROW_NUMBER() OVER (ORDER BY transaction_id)
        Values: 1, 2, 3, ..., N
        Stable across runs while transaction_ids don't change order.
        Uses Spark Window function (not MySQL AUTO_INCREMENT, which is
        incompatible with swap+truncate strategy).

=== JOB FLOW ===
  [STEP 1] Read source table from Glue Catalog
  [STEP 2] Load credentials from Glue Connection
  [STEP 3] Sanity check — both MySQL tables must exist
  [STEP 4] Write to staging table (_new) with overwrite mode
  [STEP 5] Validate staging row count
  [STEP 6] Atomic RENAME TABLE swap
  [STEP 7] Recycle _old back into _new
"""

import re
import sys
import time
import boto3

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.window import Window


SOURCE_TABLE = "tb_gex_gold_clickbank"
MYSQL_TABLE = "gold_clickbank_aws"
DEFAULT_DATABASE = "instituto_experience"


def quote_ident(name: str) -> str:
    """Quote a MySQL identifier safely with backticks."""
    return f"`{name.replace('`', '``')}`"


def parse_jdbc_url(url: str):
    """
    Parse host, port, database from a JDBC MySQL URL.
    Supports short and full forms returned by Glue Connection.
    """
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
        "&serverTimezone=America/Sao_Paulo"
        "&rewriteBatchedStatements=true"
    )


class JdbcExecutor:
    """Executes DDL/DML on MySQL via JVM JDBC driver (Py4J)."""

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


args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "SOURCE_DATABASE",
        "MIN_ROWS_THRESHOLD",
        "GLUE_CONNECTION_NAME",
    ],
)

start = time.time()

_conf = SparkConf()
_conf.set("spark.sql.files.ignoreMissingFiles", "true")
_conf.set("spark.sql.session.timeZone", "America/Sao_Paulo")
sc = SparkContext(conf=_conf)
glue_context = GlueContext(sc)
spark = glue_context.spark_session

job = Job(glue_context)
job.init(args["JOB_NAME"], args)

source_database = args["SOURCE_DATABASE"]
min_rows_threshold = int(args["MIN_ROWS_THRESHOLD"])
glue_connection_name = args["GLUE_CONNECTION_NAME"]

staging_table = f"{MYSQL_TABLE}_new"
backup_table = f"{MYSQL_TABLE}_old"

print(f"[STEP 1] Reading {source_database}.{SOURCE_TABLE} from Glue Catalog...")
try:
    df = glue_context.create_dynamic_frame.from_catalog(
        database=source_database,
        table_name=SOURCE_TABLE,
    ).toDF()
except Exception as exc:
    # Some stale partitions can reference deleted S3 files and make from_catalog fail.
    if "No such file or directory" not in str(exc):
        raise

    print(
        "[STEP 1] WARN stale catalog partition detected; "
        "falling back to table location read"
    )
    glue_client = boto3.client("glue")
    table_resp = glue_client.get_table(DatabaseName=source_database, Name=SOURCE_TABLE)
    table_location = table_resp["Table"]["StorageDescriptor"]["Location"]
    df = (
        spark.read
        .option("ignoreMissingFiles", "true")
        .parquet(table_location)
    )

if "id" in df.columns:
    df = df.drop("id")

source_count = df.count()
print(f"[STEP 1] OK {source_count} rows read from source")

# Add sequential 'id' column = ROW_NUMBER() OVER (ORDER BY transaction_id)
# Values: 1, 2, 3, ..., N
# Stable across runs while transaction_ids don't change order.
window_id = Window.orderBy(F.col("transaction_id"))
df = df.withColumn("id", F.row_number().over(window_id).cast("bigint"))
cols = ["id"] + [c for c in df.columns if c != "id"]
df = df.select(*cols)
print("[STEP 1] OK Added 'id' column (ROW_NUMBER over transaction_id)")

if source_count < min_rows_threshold:
    raise RuntimeError(
        f"Source row count below threshold. "
        f"source_count={source_count} threshold={min_rows_threshold}"
    )

print(f"[STEP 2] Extracting JDBC config from Glue Connection ({glue_connection_name})...")
jdbc_conf = glue_context.extract_jdbc_conf(glue_connection_name)
raw_url = jdbc_conf.get("url") or jdbc_conf.get("fullUrl", "")
user = jdbc_conf.get("user") or jdbc_conf.get("username", "")
password = jdbc_conf.get("password", "")

host, port, database = parse_jdbc_url(raw_url)
jdbc_url = build_jdbc_url(host, port, database)
print(f"[STEP 2] OK credentials loaded — host={host} port={port} db={database}")

executor = JdbcExecutor(spark, jdbc_url, user, password)

try:
    print("[STEP 3] Checking that MySQL tables exist...")
    if not executor.table_exists(database, MYSQL_TABLE):
        raise RuntimeError(
            f"Final table {database}.{MYSQL_TABLE} does not exist. "
            "Run DDL manually before running this job."
        )
    if not executor.table_exists(database, staging_table):
        raise RuntimeError(
            f"Staging table {database}.{staging_table} does not exist. "
            "Run DDL manually before running this job."
        )
    print("[STEP 3] OK both tables exist")

    print("[STEP 3.5] Validating source snapshot size against current MySQL table...")
    current_count = executor.fetch_scalar_int(
        f"SELECT COUNT(*) FROM {quote_ident(MYSQL_TABLE)}"
    )
    min_ratio_vs_current = 0.90
    if current_count >= min_rows_threshold:
        min_allowed = int(current_count * min_ratio_vs_current)
        if source_count < min_allowed:
            raise RuntimeError(
                "Source snapshot looks incomplete vs current MySQL table. "
                f"source_count={source_count} current_count={current_count} "
                f"min_allowed={min_allowed} ratio={min_ratio_vs_current}. "
                "Likely upstream Gold is still being rewritten; retry later."
            )
    print(
        f"[STEP 3.5] OK source_count={source_count} current_count={current_count} "
        f"ratio_floor={min_ratio_vs_current}"
    )

    print(f"[STEP 4] Writing {source_count} rows to MySQL staging with overwrite...")
    (
        df.write
        .mode("overwrite")
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", staging_table)
        .option("user", user)
        .option("password", password)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .option("truncate", "true")
        .option("batchsize", "10000")
        .save()
    )
    print("[STEP 4] OK JDBC overwrite completed")

    print("[STEP 5] Validating staging row count...")
    staging_count = executor.fetch_scalar_int(
        f"SELECT COUNT(*) FROM {quote_ident(staging_table)}"
    )

    if staging_count < min_rows_threshold:
        raise RuntimeError(
            f"Staging row count below threshold. "
            f"staging_count={staging_count} threshold={min_rows_threshold}"
        )

    print(f"[STEP 5] OK staging_count={staging_count} (threshold={min_rows_threshold})")

    print("[STEP 6] Executing atomic swap...")
    executor.execute(f"DROP TABLE IF EXISTS {quote_ident(backup_table)}")
    executor.execute(
        "RENAME TABLE "
        f"{quote_ident(MYSQL_TABLE)} TO {quote_ident(backup_table)}, "
        f"{quote_ident(staging_table)} TO {quote_ident(MYSQL_TABLE)}"
    )
    print("[STEP 6] OK atomic swap completed")

    print("[STEP 7] Recycling backup as next staging...")
    executor.execute(
        f"RENAME TABLE {quote_ident(backup_table)} TO {quote_ident(staging_table)}"
    )
    executor.execute(f"TRUNCATE TABLE {quote_ident(staging_table)}")
    print("[STEP 7] OK staging ready for next run")

finally:
    executor.close()

elapsed = int(time.time() - start)
print(f"[FINAL] OK job completed in {elapsed}s")
job.commit()
````

## Relacionados
[[00-Data-Lake]]
