---
tipo: job-glue
ambiente: develop
fluxo: landing-to-bronze
tipo_job: glueetl
glue_version: 3.0
ultima_execucao: 2026-05-28 17:41
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-landing-to-bronze-buygoods-polling-develop

> Glue ETL · fluxo **landing-to-bronze** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 3.0 |
| Worker | G.1X x2 |
| Timeout (min) | 2880 |
| Max retries | 1 |
| Role | `arn:aws:iam::406933028738:role/gex-role-lambda-ingestion-develop` |
| Script | `s3://gex-datalake-landing-develop/scripts/landing_to_bronze_buygoods_polling.py` |
| Criado | 2026-05-28 16:42:42.513000-03:00 |
| Modificado | 2026-05-28 20:11:00.701000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--BRONZE_DATABASE` | gex_db_develop_bronze |
| `--BRONZE_TABLE` | tb_bronze_buygoods_vendas_polling |
| `--SOURCE_BUCKET` | gex-datalake-landing-develop |
| `--TARGET_BUCKET` | gex-datalake-bronze-develop |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-05-28 17:41 | SUCCEEDED | 1m7s | — |
| 2026-05-28 17:18 | SUCCEEDED | 1m4s | — |
| 2026-05-28 17:13 | FAILED | 24s | SystemExit: 0 |
| 2026-05-28 17:12 | FAILED | 44s | SystemExit: 0 |
| 2026-05-28 16:59 | SUCCEEDED | 31s | — |
| 2026-05-28 16:58 | FAILED | 14s | LAUNCH ERROR / Error downloading from S3 for bucket: gex-datalake-landing-develop, key: scripts/landing_to_bronze_buygoo… |
| 2026-05-28 16:57 | FAILED | 21s | LAUNCH ERROR / Error downloading from S3 for bucket: gex-datalake-landing-develop, key: scripts/landing_to_bronze_buygoo… |
| 2026-05-28 16:50 | FAILED | — | AccountId:406933028738 and JobName:gex-landing-to-bronze-buygoods-polling-develop and JobRunId:jr_a7852f475a4b7fcdcbd269… |

## Script

> Fonte: `s3://gex-datalake-landing-develop/scripts/landing_to_bronze_buygoods_polling.py` — baixado do S3 (read-only).

````python
# landing_to_bronze_buygoods_polling.py
# Glue Job: Landing → Bronze para o pipeline BuyGoods API Polling

import sys
import boto3
import gzip
import json
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import Row
from datetime import datetime

args = getResolvedOptions(sys.argv, [
    'SOURCE_BUCKET',
    'TARGET_BUCKET',
    'BRONZE_DATABASE',
    'BRONZE_TABLE',
])

SOURCE_BUCKET = args['SOURCE_BUCKET']
TARGET_BUCKET = args['TARGET_BUCKET']
BRONZE_DATABASE = args['BRONZE_DATABASE']
BRONZE_TABLE = args['BRONZE_TABLE']
dt_proc = datetime.utcnow().strftime("%Y-%m-%d")

print(f"[INFO] dt_proc calculado automaticamente: {dt_proc}")

PREFIX = "buygoods_api/orders/"

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
s3 = boto3.client('s3')

def list_landing_files(bucket, prefix, dt_proc):
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if f"dt_proc={dt_proc}" in key and key.endswith('.json.gz'):
                yield key

def read_records(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    with gzip.GzipFile(fileobj=obj['Body']) as gz:
        envelope = json.loads(gz.read().decode('utf-8'))
    records = envelope.get('records', [])
    for r in records:
        r['_account_id']   = envelope.get('account_id')
        r['_account_name'] = envelope.get('account_name')
        r['_date_from']    = envelope.get('date_from')
        r['_date_to']      = envelope.get('date_to')
        r['_extracted_at'] = envelope.get('extracted_at')
        r['_run_id']       = envelope.get('run_id')
        # dt_proc NÃO vai dentro do record — vai como partição no path S3
    return records

all_records = []
keys_processed = 0

for key in list_landing_files(SOURCE_BUCKET, PREFIX, dt_proc):
    try:
        records = read_records(SOURCE_BUCKET, key)
        all_records.extend(records)
        keys_processed += 1
        print(f"[INFO] Lido {len(records)} records | {key}")
    except Exception as e:
        print(f"[ERROR] Falha ao ler {key} | {e}")

if not all_records:
    print(f"[WARN] Nenhum registro encontrado para dt_proc={dt_proc}. Encerrando.")
    sys.exit(0)

print(f"[INFO] Total: {len(all_records)} records de {keys_processed} arquivos")

df = spark.createDataFrame([
    Row(**{str(k): str(v) if v is not None else None for k, v in r.items()})
    for r in all_records
])

# dt_proc como partição no path — não como coluna dentro do DataFrame
output_path = f"s3://{TARGET_BUCKET}/buygoods_api/orders/dt_proc={dt_proc}/"
df.write.mode("overwrite").parquet(output_path)

print(f"[INFO] Escrita concluída | {output_path} | {df.count()} registros")
````

## Relacionados
[[00-Data-Lake]]
