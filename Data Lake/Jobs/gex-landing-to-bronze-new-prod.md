---
tipo: job-glue
ambiente: prod
fluxo: landing-to-bronze
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-03 14:10
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-landing-to-bronze-new-prod

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
| Script | `s3://gex-datalake-bronze-prod/scripts/landing_to_bronze_new.py` |
| Criado | 2026-04-01 17:19:14.888000-03:00 |
| Modificado | 2026-04-01 17:19:14.888000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--DATABASE_NAME` | gex_db_prod_bronze |
| `--source_bucket` | gex-datalake-landing-prod |
| `--target_bucket` | gex-datalake-bronze-prod |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-03 14:10 | SUCCEEDED | 1m17s | — |
| 2026-06-03 13:55 | SUCCEEDED | 1m9s | — |
| 2026-06-03 13:40 | SUCCEEDED | 58s | — |
| 2026-06-03 13:25 | SUCCEEDED | 1m15s | — |
| 2026-06-03 13:10 | SUCCEEDED | 1m11s | — |
| 2026-06-03 12:55 | SUCCEEDED | 1m1s | — |
| 2026-06-03 12:40 | SUCCEEDED | 1m15s | — |
| 2026-06-03 12:25 | SUCCEEDED | 1m21s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/landing_to_bronze_new.py` — baixado do S3 (read-only).

````python
"""
landing_to_bronze_new.py

Glue Job: Landing (clickbank_new/) → Bronze (clickbank/clickbank_vendas_new/)

Fonte: Nova API /v0/analytics/transactions
Estrutura: Flat (sem arrays aninhados problemáticos)
Chave de deduplicação: receiptNumber + transactionType
  (um mesmo receipt pode ter Sale, Refund, Chargeback e Fee — todos são linhas distintas)
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

path_landing = f"s3://{args['source_bucket']}/clickbank_new/"
path_bronze  = f"s3://{args['target_bucket']}/clickbank/clickbank_vendas_new/"

try:
    # ── 1. LEITURA ──────────────────────────────────────────────────────────
    df = (
        spark.read
        .option("recursiveFileLookup", "true")
        .json(path_landing)
        .withColumn("account_owner", F.element_at(F.split(F.input_file_name(), "/"), -2))
    )
    
    df.cache() # Joga em memória para evitar re-leitura do S3
    total_registros = df.count() # Ação única aqui

    if total_registros == 0:
        print("Nenhum dado novo em clickbank_new/. Finalizando.")
        job.commit()
        sys.exit(0)
    
    # ── 2. PARTIÇÃO DE PROCESSAMENTO (GMT-3) ────────────────────────────────
    df = df.withColumn(
        "dt_proc",
        F.to_date(F.col("transactionDate"), "yyyy-MM-dd").cast("string")
    )

    # ── 4. ESCRITA NA BRONZE ─────────────────────────────────────────────────
    (
        df.repartition(1)
        .write
        .mode("append")
        .partitionBy("dt_proc")
        .parquet(path_bronze)
    )

    # Aqui usamos a variável que já guardou o valor lá em cima
    print(f"Bronze nova API atualizada: {total_registros} registros escritos em {path_bronze}")

    # ── 5. LIMPEZA DA LANDING ────────────────────────────────────────────────
    s3     = boto3.resource("s3")
    bucket = s3.Bucket(args["source_bucket"])
    bucket.objects.filter(Prefix="clickbank_new/").delete()
    print("Landing clickbank_new/ limpa.")

    job.commit()

except Exception as e:
    print(f"ERRO CRÍTICO: {str(e)}")
    raise e
````

## Relacionados
[[00-Data-Lake]]
