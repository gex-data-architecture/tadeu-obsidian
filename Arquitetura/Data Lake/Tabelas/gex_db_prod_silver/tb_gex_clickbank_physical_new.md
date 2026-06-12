---
tipo: tabela-datalake
database: gex_db_prod_silver
ambiente: prod
camada: silver
formato: parquet
colunas: 58
tags: [datalake, silver, prod]
---

# tb_gex_clickbank_physical_new

> `gex_db_prod_silver` · camada **silver** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_silver |
| Camada | silver |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-silver-prod/gex_clickbank_physical_new/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 58 |
| Atualizada em | 2026-06-12 09:50:29-03:00 |

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
| 19 | upsell_parent_receipt | string |
| 20 | total_price | decimal(12,4) |
| 21 | total_price_usd | decimal(10,2) |
| 22 | total_collected_usd | decimal(10,2) |
| 23 | taxes | decimal(12,4) |
| 24 | taxes_usd | decimal(10,2) |
| 25 | iva_usd | decimal(10,2) |
| 26 | exchange_rate | decimal(10,4) |
| 27 | commission | decimal(12,4) |
| 28 | commission_usd | decimal(10,2) |
| 29 | account_amount_event_usd | decimal(10,2) |
| 30 | affiliate_amount | decimal(12,4) |
| 31 | affiliate_amount_usd | decimal(10,2) |
| 32 | total_refund | decimal(12,4) |
| 33 | total_refund_usd | decimal(10,2) |
| 34 | refund_fee | decimal(12,4) |
| 35 | refund_fee_usd | decimal(10,2) |
| 36 | chargeback_fee | decimal(12,4) |
| 37 | chargeback_fee_usd | decimal(10,2) |
| 38 | affiliate_name | string |
| 39 | is_house_traffic | int |
| 40 | vendor_name | string |
| 41 | created_at_date | string |
| 42 | created_at_hour | string |
| 43 | datetime_platform | string |
| 44 | date_refunded | string |
| 45 | datetime_refunded_platform | string |
| 46 | utm_content | string |
| 47 | utm_source | string |
| 48 | utm_medium | string |
| 49 | utm_term | string |
| 50 | utm_campaign | string |
| 51 | src | string |
| 52 | platform | string |
| 53 | created_at | timestamp |
| 54 | updated_at | timestamp |
| 55 | transaction_type | string |
| 56 | account_amount_usd | decimal(10,2) |
| 57 | account_amount | decimal(12,4) |
| 58 | pipeline_updated_at | timestamp |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
