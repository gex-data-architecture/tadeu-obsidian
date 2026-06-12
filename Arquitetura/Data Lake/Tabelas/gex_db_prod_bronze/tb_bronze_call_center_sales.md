---
tipo: tabela-datalake
database: gex_db_prod_bronze
ambiente: prod
camada: bronze
formato: parquet
colunas: 24
tags: [datalake, bronze, prod]
---

# tb_bronze_call_center_sales

> `gex_db_prod_bronze` · camada **bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_bronze |
| Camada | bronze |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-prod/mysql_data/call_center_sales/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 24 |
| Atualizada em | 2026-06-11 23:07:57-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | id | int |
| 2 | data | date |
| 3 | nome_produto | string |
| 4 | niche | string |
| 5 | cartpanda_brl | decimal(12,2) |
| 6 | cartpanda_usd | decimal(12,2) |
| 7 | buygoods_usd | decimal(12,2) |
| 8 | digistore_usd | decimal(12,2) |
| 9 | clickbank_usd | decimal(12,2) |
| 10 | frontend_sales | decimal(12,2) |
| 11 | logicall_usd | decimal(12,2) |
| 12 | sales_bound | decimal(12,2) |
| 13 | commited_coaches | decimal(12,2) |
| 14 | logicall_net | decimal(12,2) |
| 15 | sales_bound_net | decimal(12,2) |
| 16 | commited_coaches_net | decimal(12,2) |
| 17 | call_center_sales | decimal(12,2) |
| 18 | call_center_net | decimal(12,2) |
| 19 | logicall_check | boolean |
| 20 | sales_bound_check | boolean |
| 21 | commited_check | boolean |
| 22 | created_at | timestamp |
| 23 | updated_at | timestamp |
| 24 | product_key | string |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
