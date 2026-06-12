---
tipo: job-glue
ambiente: prod
fluxo: 
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-12 03:00
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-cartpanda-bronze-prod

> Glue ETL · fluxo **—** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x4 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/mysql_to_bronze_cartpanda_physical.py` |
| Criado | 2026-06-10 09:14:17.272000-03:00 |
| Modificado | 2026-06-10 09:14:17.272000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--DATE_FLOOR` | 2026-01-01 |
| `--GLUE_CONNECTION_NAME` | gex-mysql-connection-prod |
| `--S3_PREFIX` | cartpanda/cartpanda_physical |
| `--SOURCE_DATABASE` | instituto_experience |
| `--SOURCE_TABLE` | cartpanda_physical |
| `--target_bucket` | gex-datalake-bronze-prod |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-12 03:00 | SUCCEEDED | 2m14s | — |
| 2026-06-11 03:00 | SUCCEEDED | 2m25s | — |
| 2026-06-10 09:49 | SUCCEEDED | 1m52s | — |
| 2026-06-10 09:27 | FAILED | 43s | An error occurred while calling o105.getDynamicFrame. SELECT command denied to user 'leonardo_pinhati'@'172.31.9.115' fo… |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/mysql_to_bronze_cartpanda_physical.py` — baixado do S3 (read-only).

````python
"""
Glue Job: mysql_to_bronze_cartpanda_physical
============================================
Ingestao BRONZE da tabela MySQL instituto_experience.cartpanda_physical para o
data lake (parquet), camada bronze = dado CRU (sem regra de negocio/limpeza).

=== MUTACAO DE REGISTROS ===
  cartpanda_physical MUTA ao longo do tempo (payment_status passa a refunded /
  refunded_partial / chargeback dias depois). Por isso usamos FULL SNAPSHOT com
  OVERWRITE idempotente: re-le TODA a janela (created_at_date >= DATE_FLOOR) e
  sobrescreve o destino. Rodar 2x nao duplica nem perde atualizacoes de status.
  (append por dia perderia as mudancas em registros antigos.)

=== PARTICIONAMENTO ===
  Particionado por created_at_date (consistente com o restante do lake).

=== CREDENCIAIS ===
  Glue Connection (connectionName / useConnectionProperties) — sem Secrets Manager.

Parametros (--CHAVE valor):
  --JOB_NAME             (req, injetado pelo Glue)
  --GLUE_CONNECTION_NAME (req)   ex: gex-mysql-connection-prod
  --target_bucket        (req)   bucket bronze
  --SOURCE_DATABASE      (opt)   default: instituto_experience
  --SOURCE_TABLE         (opt)   default: cartpanda_physical
  --S3_PREFIX            (opt)   default: cartpanda/cartpanda_physical
  --DATE_FLOOR           (opt)   default: 2026-01-01
"""

import sys
import time

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F


def get_optional_arg(name: str, default: str) -> str:
    token = f"--{name}"
    if token in sys.argv:
        idx = sys.argv.index(token)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return default


args = getResolvedOptions(sys.argv, ["JOB_NAME", "GLUE_CONNECTION_NAME", "target_bucket"])

start = time.time()
glue_context = GlueContext(SparkContext())
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

connection = args["GLUE_CONNECTION_NAME"]
target_bucket = args["target_bucket"]
SOURCE_DATABASE = get_optional_arg("SOURCE_DATABASE", "instituto_experience")
SOURCE_TABLE = get_optional_arg("SOURCE_TABLE", "cartpanda_physical")
S3_PREFIX = get_optional_arg("S3_PREFIX", "cartpanda/cartpanda_physical").strip("/")
DATE_FLOOR = get_optional_arg("DATE_FLOOR", "2026-01-01")

output_path = f"s3://{target_bucket}/{S3_PREFIX}/"

# IMPORTANTE: o conector MySQL do Glue (from_options) NAO aceita subquery em
# "dbtable" (trata a string como nome de tabela e gera query invalida). Por isso
# passamos o NOME SIMPLES da tabela e filtramos a janela no Spark. Full snapshot
# (re-le tudo desde DATE_FLOOR) -> captura mutacao de payment_status.
print(f"[STEP 1] Lendo {SOURCE_DATABASE}.{SOURCE_TABLE} via {connection} ...")
dyf = glue_context.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "connectionName": connection,
        "dbtable": f"{SOURCE_DATABASE}.{SOURCE_TABLE}",
    },
)
df = dyf.toDF()
if "created_at_date" in df.columns:
    df = df.where(F.col("created_at_date") >= F.lit(DATE_FLOOR))
row_count = df.count()
print(f"[STEP 1] OK {row_count} linhas (created_at_date >= {DATE_FLOOR})")

if row_count == 0:
    raise RuntimeError(
        f"Nenhuma linha lida de {SOURCE_DATABASE}.{SOURCE_TABLE} (>= {DATE_FLOOR}). Abortando p/ nao sobrescrever a bronze com vazio."
    )

if "created_at_date" not in df.columns:
    raise RuntimeError("Coluna created_at_date ausente em cartpanda_physical (necessaria p/ particionamento).")

print(f"[STEP 2] Escrevendo parquet (overwrite, particionado por created_at_date) em {output_path} ...")
(
    df.repartition("created_at_date")
    .write.mode("overwrite")
    .partitionBy("created_at_date")
    .parquet(output_path)
)

elapsed = int(time.time() - start)
print(f"[FINAL] OK bronze cartpanda_physical gravada em {elapsed}s | rows={row_count}")
job.commit()
````

## Relacionados
[[00-Data-Lake]]
