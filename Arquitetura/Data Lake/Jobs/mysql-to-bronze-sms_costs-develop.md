---
tipo: job-glue
ambiente: develop
fluxo: mysql-to-bronze
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-03-26 15:51
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# mysql-to-bronze-sms_costs-develop

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
| Script | `s3://gex-datalake-bronze-develop/scripts/mysql_to_bronze_sms_costs.py` |
| Criado | 2026-03-26 14:10:23.537000-03:00 |
| Modificado | 2026-03-30 19:27:42.072000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--BRONZE_BUCKET` | gex-datalake-bronze-develop |
| `--CONNECTION_NAME` | gex-mysql-connection-develop |
| `--DATABASE_NAME` | gex_db_develop_bronze |
| `--db_table` | sms_costs |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-03-26 15:51 | SUCCEEDED | 1m12s | — |
| 2026-03-26 15:48 | FAILED | 46s | GlueArgumentError: the following arguments are required: --CONNECTION_NAME |
| 2026-03-26 15:30 | SUCCEEDED | 1m54s | — |
| 2026-03-26 14:42 | SUCCEEDED | 1m19s | — |
| 2026-03-26 14:34 | FAILED | 1m25s | TypeError: col should be Column |
| 2026-03-26 14:24 | FAILED | 38s | An error occurred while calling o99.getSource. Connection with name gex-mysql-connection-dev in account 406933028738 is … |
| 2026-03-26 14:17 | FAILED | 41s | An error occurred while calling o96.getSource. Connection with name gex-mysql-connection-dev in account 406933028738 is … |

## Script

> Fonte: `s3://gex-datalake-bronze-develop/scripts/mysql_to_bronze_sms_costs.py` — baixado do S3 (read-only).

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
