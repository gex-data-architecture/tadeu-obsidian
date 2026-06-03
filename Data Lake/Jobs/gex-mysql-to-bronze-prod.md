---
tipo: job-glue
ambiente: prod
fluxo: mysql-to-bronze
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-02 23:00
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-mysql-to-bronze-prod

> Glue ETL · fluxo **mysql-to-bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x10 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/mysql_to_bronze.py` |
| Criado | 2026-03-25 09:47:37.140000-03:00 |
| Modificado | 2026-04-01 17:19:15.213000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--DATABASE_NAME` | gex_db_prod_bronze |
| `--connection_name` | gex-mysql-connection-prod |
| `--db_table` | change_me |
| `--target_bucket` | gex-datalake-bronze-prod |
| `--temp_s3_dir` | s3://gex-datalake-bronze-prod/temp/ |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-02 23:00 | SUCCEEDED | 1m20s | — |
| 2026-06-01 23:00 | SUCCEEDED | 1m19s | — |
| 2026-05-31 23:00 | SUCCEEDED | 1m19s | — |
| 2026-05-30 23:00 | SUCCEEDED | 1m18s | — |
| 2026-05-29 23:00 | SUCCEEDED | 1m20s | — |
| 2026-05-28 23:00 | SUCCEEDED | 1m21s | — |
| 2026-05-27 23:00 | SUCCEEDED | 1m18s | — |
| 2026-05-26 23:00 | SUCCEEDED | 1m19s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/mysql_to_bronze.py` — baixado do S3 (read-only).

````python
import sys
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from awsglue.utils import getResolvedOptions
from pyspark.sql import functions as F
from datetime import datetime

# Captura de argumentos passados pelo Terraform/Step Functions
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'connection_name', 'target_bucket', 'db_table'])

glueContext = GlueContext(SparkContext())
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

table = args['db_table']
connection = args['connection_name']

# Query com Predicate Pushdown para filtrar direto na origem
sql_query = f"SELECT * FROM {table} WHERE created_at >= DATE(NOW())"

print(f"DEBUG: Iniciando extração da tabela: {table}")
print(f"DEBUG: Query utilizada: {sql_query}")

# --- CONFIGURAÇÃO DE CONEXÃO OTIMIZADA ---
dynamic_frame = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "connectionName": connection,
        "dbtable": table,  
        
        "pushdown_predicate": "created_at >= DATE(NOW())",
    }
)

df = dynamic_frame.toDF()

# Ação de contagem para validar se o Pushdown funcionou
row_count = df.count()
print(f"DEBUG: Total de registros lidos pelo Spark: {row_count}")

if row_count > 0:
    df.show(5)

    # Adicionando metadado de data de processamento para partição no S3
    dt_today = datetime.now().strftime("%Y-%m-%d")
    df = df.withColumn("dt_proc", F.lit(dt_today))

    # Caminho de destino no S3 (Camada Bronze)
    path_bronze = f"s3://{args['target_bucket']}/mysql_data/{table}"
    print(f"DEBUG: Gravando dados em: {path_bronze}")

    # Escrita otimizada em Parquet
    (
        df.repartition(1) # Agrupa em um único arquivo por partição (evita Small Files)
        .write
        .mode("overwrite")  
        .partitionBy("dt_proc")
        .parquet(path_bronze)
    )
    print("DEBUG: Escrita finalizada com sucesso.")
else:
    print(f"WARNING: Nenhum dado encontrado para a tabela {table} com o filtro aplicado.")

job.commit()
````

## Relacionados
[[00-Data-Lake]]
