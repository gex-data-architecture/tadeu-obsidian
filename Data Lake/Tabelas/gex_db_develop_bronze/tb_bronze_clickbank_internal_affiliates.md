---
tipo: tabela-datalake
database: gex_db_develop_bronze
ambiente: develop
camada: bronze
formato: parquet
colunas: 6
tags: [datalake, bronze, develop]
---

# tb_bronze_clickbank_internal_affiliates

> `gex_db_develop_bronze` · camada **bronze** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_develop_bronze |
| Camada | bronze |
| Ambiente | develop |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-develop/mysql_data/clickbank_internal_affiliates/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 6 |
| Atualizada em | 2026-04-09 10:44:40-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | id | int |
| 2 | affiliate_name | string |
| 3 | traffic_manager | string |
| 4 | traffic_source | string |
| 5 | created_at | timestamp |
| 6 | updated_at | timestamp |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
