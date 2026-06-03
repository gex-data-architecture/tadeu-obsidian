---
tipo: tabela-datalake
database: gex_db_develop_bronze
ambiente: develop
camada: bronze
formato: parquet
colunas: 8
tags: [datalake, bronze, develop]
---

# tb_bronze_sms_costs

> `gex_db_develop_bronze` · camada **bronze** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_develop_bronze |
| Camada | bronze |
| Ambiente | develop |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-develop/mysql_data/sms_costs/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 8 |
| Atualizada em | 2026-03-30 13:58:17-03:00 |

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
