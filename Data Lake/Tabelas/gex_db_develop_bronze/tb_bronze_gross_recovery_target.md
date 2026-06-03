---
tipo: tabela-datalake
database: gex_db_develop_bronze
ambiente: develop
camada: bronze
formato: parquet
colunas: 11
tags: [datalake, bronze, develop]
---

# tb_bronze_gross_recovery_target

> `gex_db_develop_bronze` · camada **bronze** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_develop_bronze |
| Camada | bronze |
| Ambiente | develop |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-develop/mysql_data/gross_recovery_target/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 11 |
| Atualizada em | 2026-03-30 13:58:16-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | yearmonth | date |
| 2 | sms_recuperacao | decimal(10,4) |
| 3 | sms_monetizacao | decimal(10,4) |
| 4 | sms_geral | decimal(10,4) |
| 5 | updated_at | timestamp |
| 6 | email_recuperacao | decimal(10,4) |
| 7 | email_monetizacao | decimal(10,4) |
| 8 | email_geral | decimal(10,4) |
| 9 | whatsapp_recuperacao | decimal(10,4) |
| 10 | whatsapp_monetizacao | decimal(10,4) |
| 11 | whatsapp_geral | decimal(10,4) |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
