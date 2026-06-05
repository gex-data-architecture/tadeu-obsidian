---
tipo: tabela-datalake
database: gex_db_prod_bronze
ambiente: prod
camada: bronze
formato: parquet
colunas: 6
tags: [datalake, bronze, prod]
---

# tb_bronze_general_product_costs

> `gex_db_prod_bronze` · camada **bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_bronze |
| Camada | bronze |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-prod/mysql_data/general_product_costs/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 6 |
| Atualizada em | 2026-04-06 22:06:01-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | id | int |
| 2 | unit_cost_usd | decimal(10,2) |
| 3 | valid_from | date |
| 4 | valid_until | date |
| 5 | created_at | timestamp |
| 6 | updated_at | timestamp |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
