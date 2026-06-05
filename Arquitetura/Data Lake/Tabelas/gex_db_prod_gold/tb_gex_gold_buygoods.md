---
tipo: tabela-datalake
database: gex_db_prod_gold
ambiente: prod
camada: gold
formato: parquet
colunas: 74
tags: [datalake, gold, prod]
---

# tb_gex_gold_buygoods

> `gex_db_prod_gold` · camada **gold** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_gold |
| Camada | gold |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-gold-prod/gex_gold_buygoods/` |
| Tipo | EXTERNAL_TABLE |
| Partições | created_at_date |
| Nº colunas | 74 |
| Atualizada em | 2026-06-03 14:04:55-03:00 |

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
| 12 | offer_name | string |
| 13 | product_sku | string |
| 14 | product_cost | decimal(34,4) |
| 15 | product_cost_usd | decimal(32,2) |
| 16 | quantity | decimal(32,0) |
| 17 | quantity_principal | bigint |
| 18 | total_price | decimal(34,4) |
| 19 | total_price_usd | decimal(32,2) |
| 20 | taxes | decimal(34,4) |
| 21 | taxes_usd | decimal(32,2) |
| 22 | total_refund | decimal(34,4) |
| 23 | total_refund_usd | decimal(32,2) |
| 24 | commission | decimal(35,4) |
| 25 | commission_usd | decimal(33,2) |
| 26 | affiliate_amount | decimal(34,4) |
| 27 | affiliate_amount_usd | decimal(32,2) |
| 28 | revenue_afiliado | decimal(34,4) |
| 29 | revenue_afiliado_usd | decimal(32,2) |
| 30 | has_upsell | decimal(23,0) |
| 31 | has_upsell2 | decimal(23,0) |
| 32 | has_upsell3 | decimal(23,0) |
| 33 | has_downsell | decimal(23,0) |
| 34 | has_downsell2 | decimal(23,0) |
| 35 | has_downsell3 | decimal(23,0) |
| 36 | has_order_bump | decimal(23,0) |
| 37 | total_price_upsell | decimal(33,2) |
| 38 | total_price_upsell_usd | decimal(32,2) |
| 39 | total_price_upsell2 | decimal(33,2) |
| 40 | total_price_upsell2_usd | decimal(32,2) |
| 41 | total_price_upsell3 | decimal(33,2) |
| 42 | total_price_upsell3_usd | decimal(32,2) |
| 43 | total_price_downsell | decimal(33,2) |
| 44 | total_price_downsell_usd | decimal(32,2) |
| 45 | total_price_downsell2 | decimal(33,2) |
| 46 | total_price_downsell2_usd | decimal(32,2) |
| 47 | total_price_downsell3 | decimal(33,2) |
| 48 | total_price_downsell3_usd | decimal(32,2) |
| 49 | total_price_order_bump | decimal(33,2) |
| 50 | total_price_order_bump_usd | decimal(32,2) |
| 51 | coupon_code | string |
| 52 | created_at_hour | string |
| 53 | date_refunded | date |
| 54 | utm_source | string |
| 55 | utm_medium | string |
| 56 | utm_content | string |
| 57 | utm_term | string |
| 58 | utm_campaign | string |
| 59 | src | string |
| 60 | platform | string |
| 61 | affiliate_name | string |
| 62 | vendor_name | string |
| 63 | is_house_traffic | bigint |
| 64 | purchase_group_id | string |
| 65 | account_id | string |
| 66 | datetime_platform | string |
| 67 | total_collected_usd | decimal(32,2) |
| 68 | iva | decimal(34,4) |
| 69 | iva_usd | decimal(32,2) |
| 70 | refund_fee | decimal(34,4) |
| 71 | refund_fee_usd | decimal(32,2) |
| 72 | chargeback_fee | decimal(34,4) |
| 73 | chargeback_fee_usd | decimal(32,2) |
| 74 | affiliate_id | string |

## Chaves de partição

- `created_at_date` (string)

## Relacionados
[[00-Data-Lake]]
