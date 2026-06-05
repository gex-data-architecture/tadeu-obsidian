---
tipo: tabela-datalake
database: gex_db_develop_silver
ambiente: develop
camada: silver
formato: parquet
colunas: 56
tags: [datalake, silver, develop]
---

# tb_silver_gex_datalake_silver_develop

> `gex_db_develop_silver` · camada **silver** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_develop_silver |
| Camada | silver |
| Ambiente | develop |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-silver-develop/` |
| Tipo | EXTERNAL_TABLE |
| Partições | partition_0, dt_proc |
| Nº colunas | 56 |
| Atualizada em | 2026-04-10 12:05:53-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | transaction_id | string |
| 2 | payment_status | string |
| 3 | client_name | string |
| 4 | client_email | string |
| 5 | client_phone | string |
| 6 | client_zip | string |
| 7 | client_country | string |
| 8 | client_state | string |
| 9 | client_city | string |
| 10 | client_street | string |
| 11 | product_name | string |
| 12 | product_sku | string |
| 13 | product_cost | decimal(12,4) |
| 14 | product_cost_usd | decimal(10,2) |
| 15 | quantity | int |
| 16 | offer_name | string |
| 17 | sales_type | string |
| 18 | coupon_code | string |
| 19 | total_price | decimal(12,4) |
| 20 | total_price_usd | decimal(10,2) |
| 21 | total_collected_usd | decimal(10,2) |
| 22 | taxes | decimal(12,4) |
| 23 | taxes_usd | decimal(10,2) |
| 24 | iva_usd | decimal(10,2) |
| 25 | exchange_rate | decimal(10,4) |
| 26 | commission | decimal(12,4) |
| 27 | commission_usd | decimal(10,2) |
| 28 | account_amount_event_usd | decimal(10,2) |
| 29 | affiliate_amount | decimal(12,4) |
| 30 | affiliate_amount_usd | decimal(10,2) |
| 31 | total_refund | decimal(12,4) |
| 32 | total_refund_usd | decimal(10,2) |
| 33 | refund_fee | decimal(12,4) |
| 34 | refund_fee_usd | decimal(10,2) |
| 35 | chargeback_fee | decimal(12,4) |
| 36 | chargeback_fee_usd | decimal(10,2) |
| 37 | affiliate_name | string |
| 38 | is_house_traffic | int |
| 39 | vendor_name | string |
| 40 | created_at_date | string |
| 41 | created_at_hour | string |
| 42 | datetime_platform | string |
| 43 | date_refunded | string |
| 44 | datetime_refunded_platform | string |
| 45 | utm_content | string |
| 46 | utm_source | string |
| 47 | utm_medium | string |
| 48 | utm_term | string |
| 49 | utm_campaign | string |
| 50 | src | string |
| 51 | platform | string |
| 52 | created_at | timestamp |
| 53 | updated_at | timestamp |
| 54 | transaction_type | string |
| 55 | account_amount_usd | decimal(10,2) |
| 56 | account_amount | decimal(12,4) |

## Chaves de partição

- `partition_0` (string)
- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
