---
tipo: tabela-datalake
database: gex_db_prod_bronze
ambiente: prod
camada: bronze
formato: parquet
colunas: 8
tags: [datalake, bronze, prod]
---

# tb_bronze_sms_costs

> `gex_db_prod_bronze` · camada **bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_bronze |
| Camada | bronze |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-prod/mysql_data/sms_costs/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 8 |
| Atualizada em | 2026-06-10 02:42:53-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | data | date |
| 2 | sms_recup_cost | decimal(18,6) |
| 3 | updated_at | timestamp |
| 4 | sms_monet_cost | decimal(18,6) |
| 5 | email_recup_cost | decimal(18,6) |
| 6 | email_monet_cost | decimal(18,6) |
| 7 | whatsapp_recup_cost | decimal(18,6) |
| 8 | whatsapp_monet_cost | decimal(18,6) |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
