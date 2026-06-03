---
tipo: tabela-datalake
database: gex_db_prod_bronze
ambiente: prod
camada: bronze
formato: parquet
colunas: 7
tags: [datalake, bronze, prod]
---

# tb_bronze_clickbank_fee_rates

> `gex_db_prod_bronze` · camada **bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_bronze |
| Camada | bronze |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-prod/mysql_data/clickbank_fee_rates/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 7 |
| Atualizada em | 2026-04-06 22:05:57-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | id | int |
| 2 | rate_percent | decimal(5,2) |
| 3 | fixed_fee | decimal(5,2) |
| 4 | refund_fee | decimal(5,2) |
| 5 | chargeback_fee | decimal(5,2) |
| 6 | valid_from | date |
| 7 | valid_until | date |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
