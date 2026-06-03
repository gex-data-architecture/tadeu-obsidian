---
tipo: job-glue
ambiente: develop
fluxo: landing-to-bronze
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-04-08 15:37
ultimo_estado: FAILED
tags: [datalake, glue-job]
---

# gex-landing-to-bronze-develop

> Glue ETL · fluxo **landing-to-bronze** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x10 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-develop` |
| Script | `s3://gex-datalake-bronze-develop/scripts/landing_to_bronze.py` |
| Criado | 2026-03-24 12:47:53.295000-03:00 |
| Modificado | 2026-03-30 13:51:19.268000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--DATABASE_NAME` | gex_db_develop_bronze |
| `--source_bucket` | gex-datalake-landing-develop |
| `--target_bucket` | gex-datalake-bronze-develop |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-04-08 15:37 | FAILED | 39s | AnalysisException: Path does not exist: s3://gex-datalake-landing-develop/clickbank_old |
| 2026-04-06 11:44 | FAILED | 41s | AnalysisException: Path does not exist: s3://gex-datalake-landing-develop/clickbank_old |
| 2026-04-06 11:24 | FAILED | 45s | AnalysisException: Path does not exist: s3://gex-datalake-landing-develop/clickbank_old |
| 2026-04-06 11:04 | FAILED | 59s | AnalysisException: Path does not exist: s3://gex-datalake-landing-develop/clickbank_old |
| 2026-04-06 10:44 | FAILED | 1m6s | AnalysisException: Path does not exist: s3://gex-datalake-landing-develop/clickbank_old |
| 2026-04-06 10:24 | FAILED | 37s | AnalysisException: Path does not exist: s3://gex-datalake-landing-develop/clickbank_old |
| 2026-04-02 15:23 | SUCCEEDED | 1m24s | — |
| 2026-04-02 15:16 | FAILED | 1m35s | NameError: name 'col' is not defined |

## Script

> Fonte: `s3://gex-datalake-bronze-develop/scripts/landing_to_bronze.py` — baixado do S3 (read-only).

````python
"""
landing_to_bronze.py  (ATUALIZADO)

Glue Job: Landing (clickbank_old/) → Bronze (clickbank/clickbank_vendas_old/)

Fonte: API antiga /rest/1.3/orders/list
Propósito: capturar APENAS o telefone do cliente (ausente na nova API)
Chave de deduplicação: receipt

ALTERAÇÕES vs versão anterior:
  - path_landing: clickbank/ → clickbank_old/
  - path_bronze:  clickbank/clickbank_vendas/ → clickbank/clickbank_vendas_old/
  - Limpeza da landing aponta para clickbank_old/
"""

import sys
import boto3
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv, ["JOB_NAME", "source_bucket", "target_bucket"])

glueContext = GlueContext(SparkContext())
spark       = glueContext.spark_session
job         = Job(glueContext)
job.init(args["JOB_NAME"], args)

# ATUALIZADO: lê de clickbank_old/ (API antiga, apenas telefone)
path_landing = f"s3://{args['source_bucket']}/clickbank_old/"
path_bronze  = f"s3://{args['target_bucket']}/clickbank/clickbank_vendas_old/"

try:
    # ── 1. LEITURA ──────────────────────────────────────────────────────────
    df = (
        spark.read
        .option("recursiveFileLookup", "true")
        .json(path_landing)
        .select("*", "_metadata.file_modification_time")
    )
    if "promo" in df.columns:
        df = df.withColumn("promo", F.col("promo").cast("string"))

    if df.count() == 0:
        print("Nenhum dado novo em clickbank_old/. Finalizando.")
        job.commit()
        sys.exit(0)

    # ── 2. PARTIÇÃO DE PROCESSAMENTO (GMT-3) ────────────────────────────────
    df = df.withColumn(
        "dt_proc",
        F.from_utc_timestamp(F.col("file_modification_time"), "GMT-3")
         .cast("date")
         .cast("string"),
    ).drop("file_modification_time")

    # ── 3. DEDUPLICAÇÃO ─────────────────────────────────────────────────────
    # customerContactInfo é array — preserva estrutura para parse na Silver
    if "receipt" in df.columns:
        df = df.dropDuplicates(["receipt"])

    # ── 4. ESCRITA NA BRONZE ─────────────────────────────────────────────────
    (
        df.repartition(1)
        .write
        .mode("append")
        .partitionBy("dt_proc")
        .parquet(path_bronze)
    )

    print(f"Bronze API antiga (telefone) atualizada: {df.count()} registros em {path_bronze}")

    # ── 5. LIMPEZA DA LANDING ────────────────────────────────────────────────
    s3     = boto3.resource("s3")
    bucket = s3.Bucket(args["source_bucket"])
    bucket.objects.filter(Prefix="clickbank_old/").delete()
    print("Landing clickbank_old/ limpa.")

    job.commit()

except Exception as e:
    print(f"ERRO CRÍTICO: {str(e)}")
    raise e
````

## Relacionados
[[00-Data-Lake]]
