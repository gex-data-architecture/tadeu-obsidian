---
tipo: job-glue
ambiente: prod
fluxo: to-mysql
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-01 13:28
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-buygoods-orders-silver-to-mysql-prod

> Glue ETL · fluxo **to-mysql** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x10 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/buygoods_orders_silver_to_mysql.py` |
| Criado | 2026-06-01 13:14:32.298000-03:00 |
| Modificado | 2026-06-01 13:14:32.298000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--DB_TABLE` | buygoods_silver_orders_v2 |
| `--GLUE_CONNECTION_NAME` | gex-mysql-connection-prod |
| `--MIN_ROWS_THRESHOLD` | 100 |
| `--SOURCE_DATABASE` | gex_db_prod_silver |
| `--SOURCE_LOCATION` | s3://gex-datalake-silver-prod/buygoods_orders/ |
| `--SOURCE_TABLE` | buygoods_orders |
| `--TARGET_DATABASE` | instituto_experience |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-01 13:28 | SUCCEEDED | 2m44s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/buygoods_orders_silver_to_mysql.py` — baixado do S3 (read-only).

````python
"""
Glue Job: buygoods_silver_to_mysql  (DEV)
=========================================
Publica a silver dev (gex_db_develop_silver.buygoods_orders) no MySQL
instituto_experience.buygoods_silver_orders usando SWAP ATOMICO de tabela
(mesmo processo do job de producao silver-buygoods-physical-to-mysql-prod).

=== CREDENCIAIS ===
  Lidas da Glue Connection via glue_context.extract_jdbc_conf() (sem Secrets Manager).

=== FLUXO ===
  [1] Le a tabela fonte do Glue Catalog (fallback: le o LOCATION direto)
  [2] Carrega credenciais da Glue Connection
  [3] Sanity check - tabela final e staging precisam existir no MySQL
  [3.5] Valida tamanho do snapshot vs tabela atual (>=90%) p/ nao publicar silver pela metade
  [4] Escreve no staging com overwrite (truncate)
  [5] Valida contagem do staging
  [6] RENAME TABLE atomico (final<->backup, staging->final)
  [7] Recicla backup como proximo staging

Parametros (--CHAVE valor):
  --SOURCE_DATABASE      (req)   ex: gex_db_develop_silver
  --SOURCE_TABLE         (opt)   default: buygoods_orders
  --DB_TABLE             (opt)   default: buygoods_silver_orders   (tabela final no MySQL)
  --TARGET_DATABASE      (opt)   default: instituto_experience
  --MIN_ROWS_THRESHOLD   (req)   ex: 100
  --GLUE_CONNECTION_NAME (req)   ex: gex-mysql-connection-prod
  --STABILITY_RETRIES    (opt)   default: 4
  --STABILITY_WAIT_SECONDS (opt) default: 45
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


def get_optional_arg(name: str, default: str) -> str:
    token = f"--{name}"
    if token in sys.argv:
        idx = sys.argv.index(token)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return default


# --- nomes parametrizaveis (lidos direto de sys.argv) ---
SOURCE_TABLE = get_optional_arg("SOURCE_TABLE", "buygoods_orders")
MYSQL_TABLE = get_optional_arg("DB_TABLE", "buygoods_silver_orders")
STAGING_TABLE = f"{MYSQL_TABLE}_old"
DEFAULT_DATABASE = get_optional_arg("TARGET_DATABASE", "instituto_experience")
# Caminho S3 da silver lido DIRETO (sem boto3 glue.get_table, que e control-plane
# e TRAVA dentro da VPC do Glue connection). Listar/ler parquet por S3 e data-plane
# (gateway endpoint) e funciona na VPC. Override via --SOURCE_LOCATION se necessario.
SOURCE_LOCATION = get_optional_arg(
    "SOURCE_LOCATION", "s3://gex-datalake-silver-develop/buygoods_orders/"
)


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
    """Executa DDL/DML no MySQL via JDBC (Py4J)."""

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
stability_retries = int(get_optional_arg("STABILITY_RETRIES", "4"))
stability_wait_seconds = int(get_optional_arg("STABILITY_WAIT_SECONDS", "45"))

backup_table = f"{MYSQL_TABLE}_backup"


def read_source_snapshot():
    # IMPORTANTE: ler direto do LOCATION no S3 (lista TODOS os arquivos/particoes),
    # e NAO via create_dynamic_frame.from_catalog. O from_catalog so enxerga as
    # particoes dt_proc REGISTRADAS no Glue, e a tabela silver usa partition
    # projection (recurso so do Athena) sem registrar particoes no catalogo ->
    # o from_catalog perdia as particoes de dias novos (ex.: dt_proc do dia atual),
    # publicando a silver pela metade no MySQL. Ler por LOCATION e imune a isso.
    print(f"[STEP 1] Reading {source_database}.{SOURCE_TABLE} from LOCATION {SOURCE_LOCATION} ...")
    source_df = (
        spark.read.option("ignoreMissingFiles", "true").parquet(SOURCE_LOCATION)
    )

    source_df = source_df.withColumn("id", F.monotonically_increasing_id().cast("bigint"))
    cols = ["id"] + [c for c in source_df.columns if c != "id"]
    source_df = source_df.select(*cols)
    count = source_df.count()
    return source_df, count


df, source_count = read_source_snapshot()
print(f"[STEP 1] OK {source_count} rows read from source")

if source_count < min_rows_threshold:
    raise RuntimeError(
        f"Source row count below threshold. source_count={source_count} threshold={min_rows_threshold}"
    )

print(f"[STEP 2] Extracting JDBC config from Glue Connection ({glue_connection_name})...")
jdbc_conf = glue_context.extract_jdbc_conf(glue_connection_name)
raw_url = jdbc_conf.get("url") or jdbc_conf.get("fullUrl", "")
user = jdbc_conf.get("user") or jdbc_conf.get("username", "")
password = jdbc_conf.get("password", "")

host, port, database = parse_jdbc_url(raw_url)
jdbc_url = build_jdbc_url(host, port, database)
print(f"[STEP 2] OK credentials loaded - host={host} port={port} db={database}")

executor = JdbcExecutor(spark, jdbc_url, user, password)

try:
    print("[STEP 3] Checking that MySQL tables exist...")
    if not executor.table_exists(database, MYSQL_TABLE):
        raise RuntimeError(
            f"Final table {database}.{MYSQL_TABLE} does not exist. Run DDL manually first."
        )
    if not executor.table_exists(database, STAGING_TABLE):
        raise RuntimeError(
            f"Staging table {database}.{STAGING_TABLE} does not exist. Run DDL manually first."
        )
    print("[STEP 3] OK both tables exist")

    print("[STEP 3.5] Validating source snapshot size against current MySQL table...")
    current_count = executor.fetch_scalar_int(f"SELECT COUNT(*) FROM {quote_ident(MYSQL_TABLE)}")
    min_ratio_vs_current = 0.90
    if current_count >= min_rows_threshold:
        min_allowed = int(current_count * min_ratio_vs_current)
        attempt = 0
        while source_count < min_allowed and attempt < stability_retries:
            attempt += 1
            print(
                "[STEP 3.5] WARN source snapshot appears incomplete; "
                f"attempt={attempt}/{stability_retries} waiting={stability_wait_seconds}s "
                f"source_count={source_count} min_allowed={min_allowed}"
            )
            time.sleep(stability_wait_seconds)
            df, source_count = read_source_snapshot()
        if source_count < min_allowed:
            raise RuntimeError(
                "Source snapshot looks incomplete vs current MySQL table. "
                f"source_count={source_count} current_count={current_count} min_allowed={min_allowed}. "
                "Likely upstream Silver is still being rewritten; retry later."
            )
    print(f"[STEP 3.5] OK source_count={source_count} current_count={current_count}")

    print(f"[STEP 4] Writing {source_count} rows to MySQL staging with overwrite...")
    (
        df.write.mode("overwrite")
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", STAGING_TABLE)
        .option("user", user)
        .option("password", password)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .option("truncate", "true")
        .option("batchsize", "10000")
        .save()
    )
    print("[STEP 4] OK JDBC overwrite completed")

    print("[STEP 5] Validating staging row count...")
    staging_count = executor.fetch_scalar_int(f"SELECT COUNT(*) FROM {quote_ident(STAGING_TABLE)}")
    if staging_count < min_rows_threshold:
        raise RuntimeError(
            f"Staging row count below threshold. staging_count={staging_count} threshold={min_rows_threshold}"
        )
    print(f"[STEP 5] OK staging_count={staging_count}")

    print("[STEP 6] Executing atomic swap...")
    executor.execute(f"DROP TABLE IF EXISTS {quote_ident(backup_table)}")
    executor.execute(
        "RENAME TABLE "
        f"{quote_ident(MYSQL_TABLE)} TO {quote_ident(backup_table)}, "
        f"{quote_ident(STAGING_TABLE)} TO {quote_ident(MYSQL_TABLE)}"
    )
    print("[STEP 6] OK atomic swap completed")

    print("[STEP 7] Recycling backup as next staging...")
    executor.execute(f"RENAME TABLE {quote_ident(backup_table)} TO {quote_ident(STAGING_TABLE)}")
    executor.execute(f"TRUNCATE TABLE {quote_ident(STAGING_TABLE)}")
    print("[STEP 7] OK staging ready for next run")

finally:
    executor.close()

elapsed = int(time.time() - start)
print(f"[FINAL] OK job completed in {elapsed}s")
job.commit()
````

## Relacionados
[[00-Data-Lake]]
