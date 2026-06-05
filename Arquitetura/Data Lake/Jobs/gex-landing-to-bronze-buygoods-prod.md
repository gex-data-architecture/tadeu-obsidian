---
tipo: job-glue
ambiente: prod
fluxo: landing-to-bronze
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-03 13:30
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-landing-to-bronze-buygoods-prod

> Glue ETL · fluxo **landing-to-bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x10 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/landing_to_bronze_buygoods.py` |
| Criado | 2026-05-14 17:30:55.162000-03:00 |
| Modificado | 2026-05-19 15:26:06.002000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--DATABASE_NAME` | gex_db_prod_bronze |
| `--read_mode` | incremental |
| `--source_bucket` | gex-datalake-landing-prod |
| `--target_bucket` | gex-datalake-bronze-prod |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-03 13:30 | SUCCEEDED | 4m1s | — |
| 2026-06-03 13:10 | SUCCEEDED | 3m25s | — |
| 2026-06-03 11:30 | SUCCEEDED | 3m19s | — |
| 2026-06-03 09:30 | SUCCEEDED | 3m43s | — |
| 2026-06-03 07:30 | SUCCEEDED | 3m2s | — |
| 2026-06-03 05:30 | SUCCEEDED | 3m41s | — |
| 2026-06-03 03:30 | SUCCEEDED | 3m1s | — |
| 2026-06-03 01:30 | SUCCEEDED | 3m29s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/landing_to_bronze_buygoods.py` — baixado do S3 (read-only).

````python
"""
landing_to_bronze_buygoods.py

Glue Job: Landing (buygoods/) -> Bronze (buygoods/)

Objetivo:
- Ler payloads JSON brutos recebidos via webhook BuyGoods na Landing
- Materializar uma camada Bronze em Parquet para analise de schema e integridade

Regras desta fase:
- Escrita em overwrite
- Sem purge da Landing
- Preserva payload bruto e adiciona metadados operacionais
"""

import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Tuple
from urllib.parse import urlparse

import boto3
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


LANDING_PREFIX = "buygoods/"
BRONZE_PREFIX = "buygoods/"
DT_PROC_PATTERN = r"dt_proc=(\d{4}-\d{2}-\d{2})"


def log_info(message: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] [INFO] {message}")


def log_error(message: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] [ERROR] {message}")


def configure_spark(spark_session: SparkSession) -> None:
    # AQE + tamanho alvo de particao para reduzir custo de shuffle/scan no Glue 4.0.
    spark_session.conf.set("spark.sql.adaptive.enabled", "true")
    spark_session.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
    spark_session.conf.set("spark.sql.files.maxPartitionBytes", str(128 * 1024 * 1024))


def build_paths(source_bucket: str, target_bucket: str) -> Tuple[str, str]:
    return (
        f"s3://{source_bucket}/{LANDING_PREFIX}",
        f"s3://{target_bucket}/{BRONZE_PREFIX}",
    )


def build_landing_paths(source_bucket: str, read_mode: str) -> list[str]:
    # incremental restringe a listagem do S3 no path, sem filtrar depois do load().
    base = f"s3://{source_bucket}/{LANDING_PREFIX}"

    if read_mode == "full":
        return [base]

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    return [
        f"{base}dt_proc={yesterday}/",
        f"{base}dt_proc={today}/",
    ]


def filter_existing_paths(paths: list[str]) -> list[str]:
    # Em incremental, evita falha quando d-1 ou d-0 ainda nao existem no S3.
    s3 = boto3.client("s3")
    existing = []
    for path in paths:
        parsed = urlparse(path)
        response = s3.list_objects_v2(
            Bucket=parsed.netloc,
            Prefix=parsed.path.lstrip("/"),
            MaxKeys=1,
        )
        if response.get("KeyCount", 0) > 0:
            existing.append(path)
    return existing


def extract_dt_proc_from_path() -> F.Column:
    return F.regexp_extract(F.col("path"), DT_PROC_PATTERN, 1)


def load_landing_json(spark_session: SparkSession, *landing_paths: str) -> DataFrame:
    paths = [p for p in landing_paths if p]
    if not paths:
        raise ValueError("Nenhum path de landing informado para leitura")

    # Spark aceita multiplos paths quando enviados como lista unica.
    # Enviar via *args faz o segundo path ser interpretado como formato.
    return (
        spark_session.read.format("binaryFile")
        .option("recursiveFileLookup", "true")
        .load(paths)
        .withColumn("raw_payload", F.decode(F.col("content"), "UTF-8"))
        .withColumn("source_file", F.col("path"))
        .withColumn("dt_proc", extract_dt_proc_from_path())
        .withColumnRenamed("modificationTime", "source_modification_time")
        .withColumnRenamed("length", "source_file_size")
        .drop("path", "content")
    )


def normalize_for_bronze(df: DataFrame) -> DataFrame:
    normalized = df.withColumn(
        "dt_proc",
        F.when(F.col("dt_proc") != "", F.col("dt_proc")).otherwise(
            F.to_date(F.current_timestamp()).cast("string")
        ),
    )

    return (
        normalized.withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_landing_zone", F.lit("buygoods"))
        .withColumn("_schema_version", F.lit("raw_v1"))
    )


def is_input_empty(df: DataFrame) -> bool:
    # isEmpty evita o full scan de count() antes da escrita.
    return df.isEmpty()


def delete_bronze_partitions(spark_session: SparkSession, bronze_path: str, dt_proc_values: list[str]) -> None:
    # Remove apenas as particoes que serao regravadas em incremental (d-1/d0).
    hconf = spark_session._jsc.hadoopConfiguration()
    jvm = spark_session._jvm

    base = bronze_path.rstrip("/")
    for dt_proc in dt_proc_values:
        partition_path = jvm.org.apache.hadoop.fs.Path(f"{base}/dt_proc={dt_proc}")
        fs = partition_path.getFileSystem(hconf)
        if fs.exists(partition_path):
            fs.delete(partition_path, True)


def write_bronze(df: DataFrame, bronze_path: str, read_mode: str, spark_session: SparkSession) -> None:
    writer = df.repartition("dt_proc").write.partitionBy("dt_proc")

    if read_mode == "full":
        writer.mode("overwrite").parquet(bronze_path)
        return

    dt_proc_values = [row["dt_proc"] for row in df.select("dt_proc").distinct().collect() if row["dt_proc"]]
    if dt_proc_values:
        delete_bronze_partitions(spark_session, bronze_path, dt_proc_values)

    writer.mode("append").parquet(bronze_path)


def main() -> None:
    args = getResolvedOptions(sys.argv, ["JOB_NAME", "source_bucket", "target_bucket"])
    read_mode = "full"
    if "--read_mode" in sys.argv:
        args_extra = getResolvedOptions(sys.argv, ["read_mode"])
        read_mode = args_extra["read_mode"].lower().strip()

    if read_mode not in ("full", "incremental"):
        raise ValueError(
            f"read_mode invalido: '{read_mode}'. Use 'full' ou 'incremental'."
        )

    glue_context = GlueContext(SparkContext())
    spark = glue_context.spark_session
    configure_spark(spark)

    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    landing_path, bronze_path = build_paths(args["source_bucket"], args["target_bucket"])
    landing_paths = build_landing_paths(args["source_bucket"], read_mode)
    if read_mode == "incremental":
        landing_paths = filter_existing_paths(landing_paths)
        if not landing_paths:
            log_info("Nenhuma particao encontrada para d-1/d-0. Finalizando sem escrita.")
            job.commit()
            sys.exit(0)

    log_info(f"Job iniciado: {args['JOB_NAME']}")
    log_info(f"Landing path: {landing_path}")
    log_info(f"read_mode: {read_mode}")
    log_info(f"Paths de leitura: {landing_paths}")
    log_info(f"Bronze path: {bronze_path}")
    log_info("Modo de escrita: full=overwrite total | incremental=replace particoes d-1/d0.")

    df_bronze: DataFrame | None = None

    try:
        log_info("Etapa 1/3 - Leitura da Landing (binaryFile)")
        df_raw = load_landing_json(spark, *landing_paths)

        log_info("Etapa 2/3 - Validacao de entrada")
        if is_input_empty(df_raw):
            log_info("Nenhum dado encontrado em buygoods/. Finalizando sem escrita.")
            job.commit()
            sys.exit(0)

        log_info("Etapa 3/3 - Normalizacao e escrita na Bronze")
        df_bronze = normalize_for_bronze(df_raw)
        df_bronze = df_bronze.cache()

        write_bronze(df_bronze, bronze_path, read_mode, spark)
        total_rows = df_bronze.count()

        log_info(
            f"Bronze BuyGoods atualizada com {total_rows} registros em {bronze_path} "
            f"(modo {read_mode}, landing preservada)."
        )
        job.commit()
        log_info("Job finalizado com sucesso")

    except Exception as exc:
        log_error(f"ERRO CRITICO BuyGoods Landing -> Bronze: {exc}")
        raise
    finally:
        if df_bronze is not None:
            df_bronze.unpersist()


if __name__ == "__main__":
    main()
````

## Relacionados
[[00-Data-Lake]]
