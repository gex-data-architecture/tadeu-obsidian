---
tipo: job-glue
ambiente: develop
fluxo: mysql-to-bronze
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-03-26 15:53
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# mysql-to-bronze-gross_recovery_target-develop

> Glue ETL · fluxo **mysql-to-bronze** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x2 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-develop` |
| Script | `s3://gex-datalake-bronze-develop/scripts/mysql_to_bronze_gross_recovery_target.py` |
| Criado | 2026-03-26 14:10:23.538000-03:00 |
| Modificado | 2026-03-30 19:27:42.041000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--BRONZE_BUCKET` | gex-datalake-bronze-develop |
| `--CONNECTION_NAME` | gex-mysql-connection-develop |
| `--DATABASE_NAME` | gex_db_develop_bronze |
| `--db_table` | gross_recovery_target |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-03-26 15:53 | SUCCEEDED | 59s | — |
| 2026-03-26 15:26 | SUCCEEDED | 1m24s | — |
| 2026-03-26 14:48 | SUCCEEDED | 1m25s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-develop/scripts/mysql_to_bronze_gross_recovery_target.py` — baixado do S3 (read-only).

````python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
# IMPORTANTE: Importar a função nativa do Spark
from pyspark.sql.functions import current_date

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BRONZE_BUCKET', 'CONNECTION_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Configurações
DATABASE = "instituto_experience"
TABLE = "gross_recovery_target"
BUCKET_BRONZE = args['BRONZE_BUCKET']
TARGET_PATH = f"s3://{BUCKET_BRONZE}/mysql_data/{TABLE}/"

CONNECTION_NAME = args['CONNECTION_NAME']
# 1. Leitura usando a Connection do Glue
datasource = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": f"{DATABASE}.{TABLE}",
        "connectionName": CONNECTION_NAME,
    }
)

# 2. Conversão para Spark DataFrame
df = datasource.toDF()

# 3. Adicionar dt_proc de forma performática e correta
df = df.withColumn("dt_proc", current_date())

# 4. Escrita na Bronze (Overwrite + Coalesce)
df.coalesce(1).write.mode("overwrite").partitionBy("dt_proc").parquet(TARGET_PATH)

job.commit()
````

## Relacionados
[[00-Data-Lake]]
