---
tipo: tabela-datalake
database: gex_db_prod_bronze
ambiente: prod
camada: bronze
formato: parquet
colunas: 56
tags: [datalake, bronze, prod]
---

# tb_bronze_cartpanda_physical

> `gex_db_prod_bronze` · camada **bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_bronze |
| Camada | bronze |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-prod/cartpanda/cartpanda_physical/` |
| Tipo | EXTERNAL_TABLE |
| Partições | created_at_date |
| Nº colunas | 56 |
| Atualizada em | 2026-06-12 03:06:41-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | transaction_id | string |
| 2 | client_id | string |
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
| 13 | product_cost | decimal(10,2) |
| 14 | quantity | int |
| 15 | offer_name | string |
| 16 | payment_status | string |
| 17 | refund_reason | string |
| 18 | total_price | decimal(10,2) |
| 19 | total_price_usd | decimal(10,2) |
| 20 | taxes | decimal(10,2) |
| 21 | taxes_usd | decimal(10,2) |
| 22 | total_refund | decimal(10,2) |
| 23 | total_refund_usd | decimal(10,2) |
| 24 | affiliate_amount | decimal(10,2) |
| 25 | affiliate_amount_usd | decimal(10,2) |
| 26 | commission | decimal(10,2) |
| 27 | commission_usd | decimal(10,2) |
| 28 | affiliate_id | string |
| 29 | affiliate_name | string |
| 30 | has_upsell | int |
| 31 | has_upsell2 | int |
| 32 | has_upsell3 | int |
| 33 | has_downsell | int |
| 34 | has_downsell2 | int |
| 35 | has_downsell3 | int |
| 36 | has_order_bump | int |
| 37 | total_price_upsell | decimal(10,2) |
| 38 | total_price_upsell2 | decimal(10,2) |
| 39 | total_price_upsell3 | decimal(10,2) |
| 40 | total_price_downsell2 | decimal(10,2) |
| 41 | total_price_downsell | decimal(10,2) |
| 42 | total_price_downsell3 | decimal(10,2) |
| 43 | total_price_order_bump | decimal(10,2) |
| 44 | cartpanda_retry | int |
| 45 | coupon_code | string |
| 46 | created_at_hour | timestamp |
| 47 | date_refunded | date |
| 48 | utm_source | string |
| 49 | utm_medium | string |
| 50 | utm_content | string |
| 51 | utm_term | string |
| 52 | utm_campaign | string |
| 53 | src | string |
| 54 | referring_site | string |
| 55 | platform | string |
| 56 | company | string |

## Chaves de partição

- `created_at_date` (string)

## Relacionados
[[00-Data-Lake]]
