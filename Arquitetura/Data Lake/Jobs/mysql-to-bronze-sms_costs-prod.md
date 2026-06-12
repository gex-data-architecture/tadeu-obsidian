---
tipo: job-glue
ambiente: prod
fluxo: mysql-to-bronze
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-12 02:15
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# mysql-to-bronze-sms_costs-prod

> Glue ETL · fluxo **mysql-to-bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x2 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/mysql_to_bronze_sms_costs.py` |
| Criado | 2026-03-26 18:49:40.789000-03:00 |
| Modificado | 2026-04-01 17:19:15.328000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--BRONZE_BUCKET` | gex-datalake-bronze-prod |
| `--CONNECTION_NAME` | gex-mysql-connection-prod |
| `--DATABASE_NAME` | gex_db_prod_bronze |
| `--db_table` | sms_costs |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-12 02:15 | SUCCEEDED | 1m11s | — |
| 2026-06-11 02:15 | SUCCEEDED | 1m13s | — |
| 2026-06-10 02:15 | SUCCEEDED | 1m17s | — |
| 2026-06-09 02:15 | SUCCEEDED | 1m13s | — |
| 2026-06-08 02:15 | SUCCEEDED | 1m15s | — |
| 2026-06-07 02:15 | SUCCEEDED | 1m13s | — |
| 2026-06-06 02:15 | SUCCEEDED | 1m35s | — |
| 2026-06-05 02:15 | SUCCEEDED | 1m25s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/mysql_to_bronze_sms_costs.py` — baixado do S3 (read-only).

````python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
# ADICIONADO: Import das funções do Spark SQL
from pyspark.sql.functions import current_date 

# 1. Inicialização do Job Glue
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BRONZE_BUCKET', 'CONNECTION_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# ======================================================
# PARÂMETROS ESPECÍFICOS: sms_costs
# ======================================================
DATABASE = "instituto_experience"
TABLE = "sms_costs"
BUCKET_BRONZE = args['BRONZE_BUCKET']
TARGET_PATH = f"s3://{BUCKET_BRONZE}/mysql_data/sms_costs/"

# ======================================================
# EXECUÇÃO DO ETL
# ======================================================
CONNECTION_NAME = args['CONNECTION_NAME']
# 2. Leitura do MySQL
datasource = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": f"{DATABASE}.{TABLE}",
        "connectionName": CONNECTION_NAME,
    }
)

# 3. Conversão para DataFrame Spark
df = datasource.toDF()

# Agora o current_date() vai funcionar porque foi importado acima
df = df.withColumn("dt_proc", current_date())

# 4. Escrita Otimizada na Bronze
df.coalesce(1).write.mode("overwrite").partitionBy("dt_proc").parquet(TARGET_PATH)

job.commit()
````

## Relacionados
[[00-Data-Lake]]
