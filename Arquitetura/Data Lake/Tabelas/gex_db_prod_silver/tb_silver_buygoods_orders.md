---
tipo: tabela-datalake
database: gex_db_prod_silver
ambiente: prod
camada: silver
formato: parquet
colunas: 59
tags: [datalake, silver, prod]
---

# tb_silver_buygoods_orders

> `gex_db_prod_silver` · camada **silver** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_silver |
| Camada | silver |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-silver-prod/buygoods_orders/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 59 |
| Atualizada em | 2026-06-01 17:02:38-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | transaction_id | string |
| 2 | transaction_type | string |
| 3 | payment_status | string |
| 4 | cancel_reason | string |
| 5 | platform | string |
| 6 | client_name | string |
| 7 | client_email | string |
| 8 | client_phone | string |
| 9 | client_zip | string |
| 10 | client_country | string |
| 11 | client_state | string |
| 12 | client_city | string |
| 13 | client_street | string |
| 14 | product_name | string |
| 15 | product_sku | string |
| 16 | product_codename | string |
| 17 | product_id | int |
| 18 | offer_name | string |
| 19 | quantity | int |
| 20 | sales_type | string |
| 21 | vendor_name | string |
| 22 | product_cost | decimal(12,4) |
| 23 | product_cost_usd | decimal(10,2) |
| 24 | total_collected_usd | decimal(10,2) |
| 25 | total_price_usd | decimal(10,2) |
| 26 | iva_usd | decimal(10,2) |
| 27 | taxes_usd | decimal(10,2) |
| 28 | affiliate_amount_usd | decimal(10,2) |
| 29 | exchange_rate | decimal(10,4) |
| 30 | total_price | decimal(12,4) |
| 31 | taxes | decimal(12,4) |
| 32 | iva | decimal(12,4) |
| 33 | affiliate_amount | decimal(12,4) |
| 34 | commission_usd | decimal(10,2) |
| 35 | commission | decimal(12,4) |
| 36 | total_refund_usd | decimal(10,2) |
| 37 | total_refund | decimal(12,4) |
| 38 | refund_fee_usd | decimal(10,2) |
| 39 | refund_fee | decimal(12,4) |
| 40 | chargeback_fee_usd | decimal(10,2) |
| 41 | chargeback_fee | decimal(12,4) |
| 42 | date_refunded | date |
| 43 | datetime_refunded_platform | string |
| 44 | affiliate_id | string |
| 45 | account_id | string |
| 46 | affiliate_name | string |
| 47 | is_house_traffic | boolean |
| 48 | utm_source | string |
| 49 | utm_content | string |
| 50 | utm_campaign | string |
| 51 | utm_term | string |
| 52 | utm_medium | string |
| 53 | upsell_parent_receipt | string |
| 54 | created_at_date | date |
| 55 | created_at_hour | string |
| 56 | datetime_platform | string |
| 57 | created_at | timestamp |
| 58 | updated_at | timestamp |
| 59 | pipeline_updated_at | string |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
