---
tipo: job-glue
ambiente: prod
fluxo: mysql-to-bronze
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-02 22:00
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# mysql-to-bronze-exchange_rates-prod

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
| Script | `s3://gex-datalake-bronze-prod/scripts/mysql_to_bronze_exchange_rates.py` |
| Criado | 2026-04-06 11:36:20.387000-03:00 |
| Modificado | 2026-04-06 11:36:20.387000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--BRONZE_BUCKET` | gex-datalake-bronze-prod |
| `--CONNECTION_NAME` | gex-mysql-connection-prod |
| `--DATABASE_NAME` | gex_db_prod_bronze |
| `--db_table` | exchange_rates |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-02 22:00 | SUCCEEDED | 1m1s | — |
| 2026-06-01 22:00 | SUCCEEDED | 1m5s | — |
| 2026-05-31 22:00 | SUCCEEDED | 1m4s | — |
| 2026-05-30 22:00 | SUCCEEDED | 1m0s | — |
| 2026-05-29 22:00 | SUCCEEDED | 1m11s | — |
| 2026-05-28 22:00 | SUCCEEDED | 1m10s | — |
| 2026-05-27 22:00 | SUCCEEDED | 1m5s | — |
| 2026-05-26 22:00 | SUCCEEDED | 1m1s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/mysql_to_bronze_exchange_rates.py` — baixado do S3 (read-only).

````python
import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import current_date

# ======================================================
# 1. Inicialização
# ======================================================
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BRONZE_BUCKET', 'CONNECTION_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# ======================================================
# PARÂMETROS: exchange_rates
# ======================================================
DATABASE    = "instituto_experience"
TABLE       = "exchange_rates"
TARGET_PATH = f"s3://{args['BRONZE_BUCKET']}/mysql_data/{TABLE}/"

# ======================================================
# 2. Leitura do MySQL
# Schema: rate, source_currency, target_currency, date, time, timezone
# ======================================================
datasource = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": f"{DATABASE}.{TABLE}",
        "connectionName": args['CONNECTION_NAME'],
    }
)

# ======================================================
# 3. Transformação mínima — adiciona dt_proc
# ======================================================
df = datasource.toDF()
df = df.withColumn("dt_proc", current_date())

# ======================================================
# 4. Escrita Bronze — overwrite total, particionado por dt_proc
# Tabela pequena de configuração: coalesce(1) evita arquivos
# minúsculos no S3
# ======================================================
(
    df.coalesce(1)
      .write
      .mode("overwrite")
      .partitionBy("dt_proc")
      .parquet(TARGET_PATH)
)

job.commit()
````

## Relacionados
[[00-Data-Lake]]
