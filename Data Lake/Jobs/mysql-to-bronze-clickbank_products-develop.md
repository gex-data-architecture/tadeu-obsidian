---
tipo: job-glue
ambiente: develop
fluxo: mysql-to-bronze
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-04-09 09:58
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# mysql-to-bronze-clickbank_products-develop

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
| Script | `s3://gex-datalake-bronze-develop/scripts/mysql_to_bronze_clickbank_products.py` |
| Criado | 2026-03-31 09:15:47.275000-03:00 |
| Modificado | 2026-03-31 09:15:47.275000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--BRONZE_BUCKET` | gex-datalake-bronze-develop |
| `--CONNECTION_NAME` | gex-mysql-connection-develop |
| `--DATABASE_NAME` | gex_db_develop_bronze |
| `--db_table` | clickbank_products |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-04-09 09:58 | SUCCEEDED | 1m47s | — |
| 2026-04-02 19:29 | SUCCEEDED | 1m21s | — |
| 2026-04-02 19:21 | FAILED | — | AccountId:406933028738 and JobName:mysql-to-bronze-clickbank_products-develop and JobRunId:jr_74424e4bffdc1d93ed5af46128… |
| 2026-03-31 09:16 | SUCCEEDED | 1m31s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-develop/scripts/mysql_to_bronze_clickbank_products.py` — baixado do S3 (read-only).

````python
import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.sql import functions as F

# ============================================================
# SETUP
# ============================================================
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'BRONZE_BUCKET',
    'CONNECTION_NAME',
    'db_table',
    'DATABASE_NAME'
])

glueContext = GlueContext(SparkContext())
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# ============================================================
# 1. LEITURA VIA JDBC (Glue Connection)
# ============================================================
df = (
    glueContext.create_dynamic_frame.from_options(
        connection_type="mysql",
        connection_options={
            "useConnectionProperties": "true",
            "connectionName": args['CONNECTION_NAME'],
            "dbtable": args['db_table'],
        }
    ).toDF()
)

# ============================================================
# 2. TRANSFORMAÇÕES
# Padronização de tipos e adição da partição de processamento
# ============================================================
df = (
    df
    .withColumn("product_id",           F.col("product_id").cast("string"))
    .withColumn("account_name",         F.col("account_name").cast("string"))
    .withColumn("product_name",         F.col("product_name").cast("string"))
    .withColumn("offer_name",           F.col("offer_name").cast("string"))
    .withColumn("offer_name_locked",    F.col("offer_name_locked").cast("boolean"))
    .withColumn("offer_name_resync",    F.col("offer_name_resync").cast("boolean"))
    .withColumn("price_usd",            F.col("price_usd").cast("decimal(10,2)"))
    .withColumn("commission_pct",       F.col("commission_pct").cast("decimal(5,2)"))
    .withColumn("product_status",       F.col("product_status").cast("string"))
    .withColumn("is_physical",          F.col("is_physical").cast("boolean"))
    .withColumn("created_at",           F.col("created_at").cast("timestamp"))
    .withColumn("updated_at",           F.col("updated_at").cast("timestamp"))
    # Partição de processamento — data de execução do job
    .withColumn("dt_proc",              F.to_date(F.current_timestamp()))
)

# ============================================================
# 3. ESCRITA NA BRONZE — overwrite total
# Tabela pequena de configuração: sem histórico, sempre substitui
# ============================================================
target = f"s3://{args['BRONZE_BUCKET']}/mysql_data/{args['db_table']}/"

(
    df.write
    .format("parquet")
    .mode("overwrite")
    .partitionBy("dt_proc")
    .save(target)
)

# ============================================================
# 4. REGISTRO NO GLUE CATALOG
# ============================================================
from awsglue.dynamicframe import DynamicFrame

dyf = DynamicFrame.fromDF(df, glueContext, "dyf")

sink = glueContext.getSink(
    path=target,
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=["dt_proc"],
    enableUpdateCatalog=True
)
sink.setCatalogInfo(
    catalogDatabase=args['DATABASE_NAME'],
    catalogTableName=f"tb_bronze_{args['db_table']}"
)
sink.setFormat("glueparquet")
sink.writeFrame(dyf)

print(f"Ingestão de {args['db_table']} finalizada com sucesso!")

job.commit()
````

## Relacionados
[[00-Data-Lake]]
