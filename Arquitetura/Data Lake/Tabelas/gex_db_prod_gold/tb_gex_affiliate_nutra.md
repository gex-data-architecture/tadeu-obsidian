---
tipo: tabela-datalake
database: gex_db_prod_gold
ambiente: prod
camada: gold
formato: parquet
colunas: 35
tags: [datalake, gold, prod]
---

# tb_gex_affiliate_nutra

> `gex_db_prod_gold` · camada **gold** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_gold |
| Camada | gold |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-gold-prod/gex_affiliate_nutra/` |
| Tipo | EXTERNAL_TABLE |
| Partições | created_at_date |
| Nº colunas | 35 |
| Atualizada em | 2026-06-11 15:26:10-03:00 |

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
| 10 | total_price | decimal(32,2) |
| 11 | commission | decimal(32,2) |
| 12 | taxes | decimal(32,2) |
| 13 | total_refund | decimal(32,2) |
| 14 | product_cost | decimal(32,2) |
| 15 | affiliate_amount | decimal(32,2) |
| 16 | imposto | decimal(36,5) |
| 17 | 1_2_units_sales | decimal(23,0) |
| 18 | 3_4_units_sales | decimal(23,0) |
| 19 | 5_6_units_sales | decimal(23,0) |
| 20 | faixa_potes | string |
| 21 | ob_count | decimal(32,0) |
| 22 | ob_revenue | decimal(32,2) |
| 23 | up1_count | decimal(32,0) |
| 24 | up1_revenue | decimal(32,2) |
| 25 | up2_count | decimal(32,0) |
| 26 | up2_revenue | decimal(32,2) |
| 27 | up3_count | decimal(32,0) |
| 28 | up3_revenue | decimal(32,2) |
| 29 | down1_count | decimal(32,0) |
| 30 | down1_revenue | decimal(32,2) |
| 31 | down2_count | decimal(32,0) |
| 32 | down2_revenue | decimal(32,2) |
| 33 | down3_count | decimal(32,0) |
| 34 | down3_revenue | decimal(32,2) |
| 35 | revenue_no_funnel | decimal(38,2) |

## Chaves de partição

- `created_at_date` (string)

## Relacionados
[[00-Data-Lake]]
