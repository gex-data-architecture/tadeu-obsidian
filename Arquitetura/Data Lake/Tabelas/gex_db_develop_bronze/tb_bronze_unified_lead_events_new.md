---
tipo: tabela-datalake
database: gex_db_develop_bronze
ambiente: develop
camada: bronze
formato: parquet
colunas: 48
tags: [datalake, bronze, develop]
---

# tb_bronze_unified_lead_events_new

> `gex_db_develop_bronze` · camada **bronze** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_develop_bronze |
| Camada | bronze |
| Ambiente | develop |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-develop/mysql_data/unified_lead_events_new/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 48 |
| Atualizada em | 2026-04-02 11:21:22-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | unique_key | string |
| 2 | order_id | string |
| 3 | event_type | string |
| 4 | platform | string |
| 5 | shop_id | string |
| 6 | client_email | string |
| 7 | client_phone | string |
| 8 | client_first_name | string |
| 9 | client_last_name | string |
| 10 | product_name | string |
| 11 | order_amount | decimal(10,2) |
| 12 | currency | string |
| 13 | tracking_link | string |
| 14 | fulfillment_updated_at | date |
| 15 | address_line_1 | string |
| 16 | address_line_2 | string |
| 17 | address_city | string |
| 18 | address_state | string |
| 19 | address_zip | string |
| 20 | address_country | string |
| 21 | order_date | date |
| 22 | order_time | timestamp |
| 23 | created_at | timestamp |
| 24 | status_sms | string |
| 25 | status_sms_geral | string |
| 26 | log_sms | string |
| 27 | status_active_campaign | string |
| 28 | log_active_campaign | string |
| 29 | status_call_center | string |
| 30 | call_center_target | string |
| 31 | log_call_center | string |
| 32 | raw_payload | string |
| 33 | updated_at | timestamp |
| 34 | source | string |
| 35 | lambda_name | string |
| 36 | data_insercao_slicktext | timestamp |
| 37 | data_insercao_activecampaign | timestamp |
| 38 | data_insercao_logicall | timestamp |
| 39 | data_insercao_salesbound | timestamp |
| 40 | data_insercao_reportana | timestamp |
| 41 | log_reportana | string |
| 42 | data_insercao_scalepath | timestamp |
| 43 | status_whatsapp_reportana | string |
| 44 | data_insercao_active_validated | timestamp |
| 45 | contact_id_active_campaign | string |
| 46 | watchdog_retries_sms | int |
| 47 | watchdog_retries_email | int |
| 48 | watchdog_retries_callcenter | int |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
