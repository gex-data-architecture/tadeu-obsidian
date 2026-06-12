---
tipo: tabela-datalake
database: gex_db_prod_gold
ambiente: prod
camada: gold
formato: parquet
colunas: 64
tags: [datalake, gold, prod]
---

# tb_gex_gold_clickbank_buygoods

> `gex_db_prod_gold` · camada **gold** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_gold |
| Camada | gold |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-gold-prod/gex_gold_clickbank_buygoods/` |
| Tipo | EXTERNAL_TABLE |
| Partições | created_at_date |
| Nº colunas | 64 |
| Atualizada em | 2026-06-11 15:20:01-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | id | bigint |
| 2 | transaction_id | string |
| 3 | payment_status | string |
| 4 | client_name | string |
| 5 | client_email | string |
| 6 | client_phone | string |
| 7 | client_zip | string |
| 8 | client_country | string |
| 9 | client_state | string |
| 10 | client_city | string |
| 11 | client_street | string |
| 12 | product_name | string |
| 13 | offer_name | string |
| 14 | product_sku | string |
| 15 | product_cost | decimal(12,4) |
| 16 | product_cost_usd | decimal(10,2) |
| 17 | quantity | int |
| 18 | quantity_principal | int |
| 19 | total_price | decimal(12,4) |
| 20 | total_price_usd | decimal(10,2) |
| 21 | taxes | decimal(12,4) |
| 22 | taxes_usd | decimal(10,2) |
| 23 | total_refund | decimal(12,4) |
| 24 | total_refund_usd | decimal(10,2) |
| 25 | commission | decimal(12,4) |
| 26 | commission_usd | decimal(10,2) |
| 27 | affiliate_amount | decimal(12,4) |
| 28 | affiliate_amount_usd | decimal(10,2) |
| 29 | revenue_afiliado | decimal(12,4) |
| 30 | revenue_afiliado_usd | decimal(10,2) |
| 31 | has_upsell | int |
| 32 | has_upsell2 | int |
| 33 | has_upsell3 | int |
| 34 | has_downsell | int |
| 35 | has_downsell2 | int |
| 36 | has_downsell3 | int |
| 37 | has_order_bump | int |
| 38 | total_price_upsell | decimal(10,2) |
| 39 | total_price_upsell_usd | decimal(10,2) |
| 40 | total_price_upsell2 | decimal(10,2) |
| 41 | total_price_upsell2_usd | decimal(10,2) |
| 42 | total_price_upsell3 | decimal(10,2) |
| 43 | total_price_upsell3_usd | decimal(10,2) |
| 44 | total_price_downsell | decimal(10,2) |
| 45 | total_price_downsell_usd | decimal(10,2) |
| 46 | total_price_downsell2 | decimal(10,2) |
| 47 | total_price_downsell2_usd | decimal(10,2) |
| 48 | total_price_downsell3 | decimal(10,2) |
| 49 | total_price_downsell3_usd | decimal(10,2) |
| 50 | total_price_order_bump | decimal(10,2) |
| 51 | total_price_order_bump_usd | decimal(10,2) |
| 52 | coupon_code | string |
| 53 | created_at_hour | string |
| 54 | date_refunded | string |
| 55 | utm_source | string |
| 56 | utm_medium | string |
| 57 | utm_content | string |
| 58 | utm_term | string |
| 59 | utm_campaign | string |
| 60 | src | string |
| 61 | platform | string |
| 62 | affiliate_name | string |
| 63 | vendor_name | string |
| 64 | is_house_traffic | int |

## Chaves de partição

- `created_at_date` (string)

## Relacionados
[[00-Data-Lake]]
