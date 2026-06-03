---
tipo: tabela-datalake
database: gex_db_prod_bronze
ambiente: prod
camada: bronze
formato: parquet
colunas: 6
tags: [datalake, bronze, prod]
---

# tb_bronze_exchange_rates

> `gex_db_prod_bronze` · camada **bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_bronze |
| Camada | bronze |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-prod/mysql_data/exchange_rates/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 6 |
| Atualizada em | 2026-06-02 22:04:20-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | rate | decimal(10,4) |
| 2 | source_currency | string |
| 3 | target_currency | string |
| 4 | date | date |
| 5 | time | timestamp |
| 6 | timezone | string |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
