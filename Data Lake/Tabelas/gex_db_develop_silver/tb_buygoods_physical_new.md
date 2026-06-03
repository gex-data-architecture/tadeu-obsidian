---
tipo: tabela-datalake
database: gex_db_develop_silver
ambiente: develop
camada: silver
formato: parquet
colunas: 62
tags: [datalake, silver, develop]
---

# tb_buygoods_physical_new

> `gex_db_develop_silver` · camada **silver** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_develop_silver |
| Camada | silver |
| Ambiente | develop |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-silver-develop/buygoods_physical_new/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 62 |
| Atualizada em | 2026-05-14 14:56:13-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | transaction_id | string |
| 2 | transaction_type | string |
| 3 | payment_status | string |
| 4 | platform | string |
| 5 | client_name | string |
| 6 | client_email | string |
| 7 | client_phone | string |
| 8 | client_zip | string |
| 9 | client_country | string |
| 10 | client_state | string |
| 11 | client_city | string |
| 12 | client_street | string |
| 13 | product_name | string |
| 14 | product_sku | string |
| 15 | product_codename | string |
| 16 | product_id | int |
| 17 | offer_name | string |
| 18 | quantity | int |
| 19 | sales_type | string |
| 20 | vendor_name | string |
| 21 | product_cost | decimal(12,4) |
| 22 | product_cost_usd | decimal(10,2) |
| 23 | total_collected_usd | decimal(10,2) |
| 24 | total_price_usd | decimal(10,2) |
| 25 | iva_usd | decimal(10,2) |
| 26 | taxes_usd | decimal(10,2) |
| 27 | affiliate_amount_usd | decimal(10,2) |
| 28 | exchange_rate | decimal(10,4) |
| 29 | total_price | decimal(12,4) |
| 30 | taxes | decimal(12,4) |
| 31 | iva | decimal(12,4) |
| 32 | affiliate_amount | decimal(12,4) |
| 33 | commission_usd | decimal(10,2) |
| 34 | commission | decimal(12,4) |
| 35 | total_refund_usd | decimal(10,2) |
| 36 | total_refund | decimal(12,4) |
| 37 | refund_fee_usd | decimal(10,2) |
| 38 | refund_fee | decimal(12,4) |
| 39 | chargeback_fee_usd | decimal(10,2) |
| 40 | chargeback_fee | decimal(12,4) |
| 41 | date_refunded | string |
| 42 | datetime_refunded_platform | string |
| 43 | affiliate_id | string |
| 44 | affiliate_name | string |
| 45 | is_house_traffic | boolean |
| 46 | subid | string |
| 47 | subid2 | string |
| 48 | subid3 | string |
| 49 | subid4 | string |
| 50 | subid5 | string |
| 51 | upsell_parent_receipt | string |
| 52 | created_at_date | date |
| 53 | created_at_hour | string |
| 54 | datetime_platform | string |
| 55 | created_at | timestamp |
| 56 | updated_at | timestamp |
| 57 | payment_provider | string |
| 58 | fulfillment_box_id | string |
| 59 | tracking_id | string |
| 60 | was_fulfilled | int |
| 61 | ip_address | string |
| 62 | browser_user_agent | string |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
