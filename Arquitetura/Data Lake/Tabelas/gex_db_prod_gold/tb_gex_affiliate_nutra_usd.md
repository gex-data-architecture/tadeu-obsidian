---
tipo: tabela-datalake
database: gex_db_prod_gold
ambiente: prod
camada: gold
formato: parquet
colunas: 41
tags: [datalake, gold, prod]
---

# tb_gex_affiliate_nutra_usd

> `gex_db_prod_gold` · camada **gold** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_gold |
| Camada | gold |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-gold-prod/gex_affiliate_nutra_usd/` |
| Tipo | EXTERNAL_TABLE |
| Partições | created_at_date |
| Nº colunas | 41 |
| Atualizada em | 2026-06-11 15:26:15-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | clean_product_name | string |
| 2 | platform | string |
| 3 | affiliate_name | string |
| 4 | affiliate_id | string |
| 5 | payment_status | string |
| 6 | funil_id | string |
| 7 | coupon_code | string |
| 8 | niche | string |
| 9 | total_vendas | bigint |
| 10 | total_price | decimal(34,2) |
| 11 | commission | decimal(34,2) |
| 12 | taxes | decimal(34,2) |
| 13 | total_refund | decimal(34,2) |
| 14 | refund_total_amount | decimal(34,2) |
| 15 | refund_partial_amount | decimal(34,2) |
| 16 | chargeback_amount | decimal(34,2) |
| 17 | refund_total_sales | decimal(23,0) |
| 18 | refund_partial_sales | decimal(23,0) |
| 19 | chargeback_sales | decimal(23,0) |
| 20 | product_cost | decimal(34,2) |
| 21 | affiliate_amount | decimal(34,2) |
| 22 | imposto | decimal(35,2) |
| 23 | 1_2_units_sales | decimal(23,0) |
| 24 | 3_4_units_sales | decimal(23,0) |
| 25 | 5_6_units_sales | decimal(23,0) |
| 26 | faixa_potes | string |
| 27 | ob_count | decimal(32,0) |
| 28 | ob_revenue | decimal(34,2) |
| 29 | up1_count | decimal(32,0) |
| 30 | up1_revenue | decimal(34,2) |
| 31 | up2_count | decimal(32,0) |
| 32 | up2_revenue | decimal(34,2) |
| 33 | up3_count | decimal(32,0) |
| 34 | up3_revenue | decimal(34,2) |
| 35 | down1_count | decimal(32,0) |
| 36 | down1_revenue | decimal(34,2) |
| 37 | down2_count | decimal(32,0) |
| 38 | down2_revenue | decimal(34,2) |
| 39 | down3_count | decimal(32,0) |
| 40 | down3_revenue | decimal(34,2) |
| 41 | revenue_no_funnel | decimal(38,2) |

## Chaves de partição

- `created_at_date` (string)

## Relacionados
[[00-Data-Lake]]
