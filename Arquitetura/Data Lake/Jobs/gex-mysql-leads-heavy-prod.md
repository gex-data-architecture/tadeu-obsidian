---
tipo: job-glue
ambiente: prod
fluxo: 
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-03 13:38
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-mysql-leads-heavy-prod

> Glue ETL · fluxo **—** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x5 |
| Timeout (min) | 15 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/mysql_to_bronze_leads_heavy.py` |
| Criado | 2026-03-25 11:28:57.632000-03:00 |
| Modificado | 2026-04-01 17:19:15.192000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--DATABASE_NAME` | gex_db_prod_bronze |
| `--connection_name` | gex-mysql-connection-prod |
| `--db_table` | unified_lead_events_new |
| `--target_bucket` | gex-datalake-bronze-prod |
| `--temp_s3_dir` | s3://gex-datalake-bronze-prod/temp/ |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-03 13:38 | SUCCEEDED | 1m12s | — |
| 2026-06-03 12:38 | SUCCEEDED | 1m12s | — |
| 2026-06-03 11:38 | SUCCEEDED | 1m5s | — |
| 2026-06-03 10:38 | SUCCEEDED | 1m11s | — |
| 2026-06-03 09:38 | SUCCEEDED | 1m13s | — |
| 2026-06-03 08:38 | SUCCEEDED | 1m10s | — |
| 2026-06-03 07:38 | SUCCEEDED | 1m11s | — |
| 2026-06-03 06:38 | SUCCEEDED | 1m11s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/mysql_to_bronze_leads_heavy.py` — baixado do S3 (read-only).

````python
import sys
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from awsglue.utils import getResolvedOptions
from pyspark.sql import functions as F
from datetime import datetime

# Captura de argumentos
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'connection_name', 'target_bucket', 'db_table'])

glueContext = GlueContext(SparkContext())
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

table = args['db_table']
connection = args['connection_name']

# 1. Configuração de Particionamento JDBC (Alta Performance)
# Usamos 'unique_key' para distribuir a leitura entre os workers
# 'hashfield' divide os registros para que os 5 workers leiam fatias diferentes simultaneamente
connection_options = {
    "useConnectionProperties": "true",
    "dbtable": table,
    "connectionName": connection,
    "hashfield": "unique_key",
    "hashpartitions": "10",
    "enablePartitioningForSampleQuery": True
}

print(f"DEBUG: Iniciando extração otimizada da tabela: {table}")

# 2. Leitura com Predicate Pushdown (Filtro direto na origem)
# Filtramos por 'order_date' que possui índice no seu MySQL
datasource = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options=connection_options,
    transformation_ctx="datasource"
)

# Converter para DataFrame para facilitar manipulação
df = datasource.toDF()

# Se o bookmark estiver vazio, o filtro garante que não leremos o passado desnecessário
df_filtered = df.filter(F.col("order_date") >= F.current_date())

# 3. Escrita em Parquet Particionado por data de processamento
output_path = f"s3://{args['target_bucket']}/mysql_data/{table}/"
partition_col = datetime.now().strftime('%Y-%m-%d')

print(f"DEBUG: Gravando dados no S3: {output_path}")

df_filtered.write \
    .mode("append") \
    .partitionBy("order_date") \
    .parquet(output_path)

job.commit()
````

## Relacionados
[[00-Data-Lake]]
