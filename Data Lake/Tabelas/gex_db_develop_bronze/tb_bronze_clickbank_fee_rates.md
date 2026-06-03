---
tipo: tabela-datalake
database: gex_db_develop_bronze
ambiente: develop
camada: bronze
formato: parquet
colunas: 7
tags: [datalake, bronze, develop]
---

# tb_bronze_clickbank_fee_rates

> `gex_db_develop_bronze` · camada **bronze** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_develop_bronze |
| Camada | bronze |
| Ambiente | develop |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-develop/mysql_data/clickbank_fee_rates/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 7 |
| Atualizada em | 2026-03-30 19:44:24-03:00 |

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
