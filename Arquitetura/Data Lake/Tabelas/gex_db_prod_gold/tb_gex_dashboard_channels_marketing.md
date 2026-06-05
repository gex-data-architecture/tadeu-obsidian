---
tipo: tabela-datalake
database: gex_db_prod_gold
ambiente: prod
camada: gold
formato: parquet
colunas: 52
tags: [datalake, gold, prod]
---

# tb_gex_dashboard_channels_marketing

> `gex_db_prod_gold` · camada **gold** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_gold |
| Camada | gold |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-gold-prod/gex_dashboard_channels_marketing/` |
| Tipo | EXTERNAL_TABLE |
| Partições | data_venda |
| Nº colunas | 52 |
| Atualizada em | 2026-04-23 15:02:43-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | canal | string |
| 2 | nome_produto | string |
| 3 | niche | string |
| 4 | tipo_venda | string |
| 5 | is_reference_row | int |
| 6 | is_global_reference_row | int |
| 7 | units_1_2 | bigint |
| 8 | units_2_3 | bigint |
| 9 | units_3_4 | bigint |
| 10 | units_5_6 | bigint |
| 11 | units_3_5 | bigint |
| 12 | units_4 | bigint |
| 13 | units_5 | bigint |
| 14 | units_6_plus | bigint |
| 15 | units_7_plus | bigint |
| 16 | total_vendas | bigint |
| 17 | revenue | decimal(22,4) |
| 18 | product_cost | decimal(22,4) |
| 19 | commission | decimal(22,4) |
| 20 | taxes | decimal(22,4) |
| 21 | imposto | decimal(25,6) |
| 22 | total_refund | decimal(22,4) |
| 23 | net_sales_value | decimal(18,6) |
| 24 | revenue_no_funnel | decimal(29,4) |
| 25 | ob_count | bigint |
| 26 | ob_revenue | decimal(20,2) |
| 27 | up1_count | bigint |
| 28 | up1_revenue | decimal(20,2) |
| 29 | up2_count | bigint |
| 30 | up2_revenue | decimal(20,2) |
| 31 | up3_count | bigint |
| 32 | up3_revenue | decimal(20,2) |
| 33 | down1_count | bigint |
| 34 | down1_revenue | decimal(20,2) |
| 35 | down2_count | bigint |
| 36 | down2_revenue | decimal(20,2) |
| 37 | down3_count | bigint |
| 38 | down3_revenue | decimal(20,2) |
| 39 | company_frontend_sales_brl | decimal(25,3) |
| 40 | cost_sms_pct | decimal(12,8) |
| 41 | recup_target | decimal(14,4) |
| 42 | monet_target | decimal(14,4) |
| 43 | geral_target | decimal(14,4) |
| 44 | email_recup_target | decimal(14,4) |
| 45 | email_monet_target | decimal(14,4) |
| 46 | email_geral_target | decimal(14,4) |
| 47 | whats_recup_target | decimal(14,4) |
| 48 | whats_monet_target | decimal(14,4) |
| 49 | whats_geral_target | decimal(14,4) |
| 50 | cost_sms | decimal(18,6) |
| 51 | cost_sms_allocated | decimal(31,14) |
| 52 | origem | string |

## Chaves de partição

- `data_venda` (string)

## Relacionados
[[00-Data-Lake]]
