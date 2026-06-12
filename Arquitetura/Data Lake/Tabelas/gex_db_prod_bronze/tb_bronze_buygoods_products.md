---
tipo: tabela-datalake
database: gex_db_prod_bronze
ambiente: prod
camada: bronze
formato: parquet
colunas: 8
tags: [datalake, bronze, prod]
---

# tb_bronze_buygoods_products

> `gex_db_prod_bronze` · camada **bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_bronze |
| Camada | bronze |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-prod/mysql_data/buygoods_products/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 8 |
| Atualizada em | 2026-06-11 22:04:10-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | id | int |
| 2 | product_id | string |
| 3 | account_name | string |
| 4 | product_codename | string |
| 5 | product_name | string |
| 6 | offer_name | string |
| 7 | offer_name_locked | boolean |
| 8 | data_insercao_offer | timestamp |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
