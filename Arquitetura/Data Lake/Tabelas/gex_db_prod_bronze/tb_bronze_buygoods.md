---
tipo: tabela-datalake
database: gex_db_prod_bronze
ambiente: prod
camada: bronze
formato: parquet
colunas: 7
tags: [datalake, bronze, prod]
---

# tb_bronze_buygoods

> `gex_db_prod_bronze` · camada **bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_bronze |
| Camada | bronze |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-prod/buygoods/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 7 |
| Atualizada em | 2026-06-12 09:36:27-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | source_modification_time | timestamp |
| 2 | source_file_size | bigint |
| 3 | raw_payload | string |
| 4 | source_file | string |
| 5 | _ingested_at | timestamp |
| 6 | _landing_zone | string |
| 7 | _schema_version | string |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
