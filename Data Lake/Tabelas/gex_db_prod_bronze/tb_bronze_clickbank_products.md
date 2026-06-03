---
tipo: tabela-datalake
database: gex_db_prod_bronze
ambiente: prod
camada: bronze
formato: parquet
colunas: 12
tags: [datalake, bronze, prod]
---

# tb_bronze_clickbank_products

> `gex_db_prod_bronze` · camada **bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_bronze |
| Camada | bronze |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-prod/mysql_data/clickbank_products/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 12 |
| Atualizada em | 2026-06-02 22:01:29-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | product_id | string |
| 2 | account_name | string |
| 3 | product_name | string |
| 4 | offer_name | string |
| 5 | offer_name_locked | boolean |
| 6 | offer_name_resync | boolean |
| 7 | price_usd | decimal(10,2) |
| 8 | commission_pct | decimal(5,2) |
| 9 | product_status | string |
| 10 | is_physical | boolean |
| 11 | created_at | timestamp |
| 12 | updated_at | timestamp |

## Chaves de partição

- `dt_proc` (date)

## Relacionados
[[00-Data-Lake]]
