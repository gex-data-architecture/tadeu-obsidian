---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 37
tags: [view]
---

# view_nutra_eua_vendas_reagrupado

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 37 |

## Lê de
[[cartpanda_physical]], [[google_ad_id]], [[meta_ad_id]]

## Lida por
—

## Definição SQL

```sql
select `cp`.`transaction_id` AS `transaction_id`,`cp`.`client_email` AS `client_email`,`cp`.`product_name` AS `product_name`,(case when (`cp`.`payment_status` in ('approved','refunded_partial')) then `cp`.`product_cost` else NULL end) AS `product_cost`,`cp`.`offer_name` AS `offer_name`,`cp`.`payment_status` AS `payment_status`,`cp`.`total_price` AS `total_price`,`cp`.`commission` AS `commission`,`cp`.`taxes` AS `taxes`,`cp`.`total_refund` AS `total_refund`,`cp`.`has_upsell` AS `has_upsell`,`cp`.`total_price_upsell` AS `total_price_upsell`,`cp`.`has_upsell2` AS `has_upsell2`,`cp`.`total_price_upsell2` AS `total_price_upsell2`,`cp`.`has_upsell3` AS `has_upsell3`,`cp`.`total_price_upsell3` AS `total_price_upsell3`,`cp`.`has_downsell` AS `has_downsell`,`cp`.`total_price_downsell` AS `total_price_downsell`,`cp`.`has_downsell2` AS `has_downsell2`,`cp`.`total_price_downsell2` AS `total_price_downsell2`,`cp`.`has_downsell3` AS `has_downsell3`,`cp`.`total_price_downsell3` AS `total_price_downsell3`,`cp`.`created_at_date` AS `created_at_date`,`cp`.`created_at_hour` AS `created_at_hour`,`cp`.`utm_content` AS `utm_content`,`cp`.`platform` AS `platform`,NULL AS `account_id`,NULL AS `account_name`,NULL AS `campaign_name`,NULL AS `adset_name`,NULL AS `ad_name`,NULL AS `ad_id`,NULL AS `amount_spent_brl`,NULL AS `impressions`,NULL AS `reach`,NULL AS `link_clicks`,(case when (`cp`.`payment_status` in ('approved','refunded_partial')) then (case when (`cp`.`created_at_date` >= '2025-05-01') then (`cp`.`total_price` * 0.05) else (`cp`.`total_price` * 0.10) end) else 0 end) AS `imposto` from `instituto_experience`.`cartpanda_physical` `cp` where (`cp`.`payment_status` in ('approved','refunded','chargeback','refunded_partial')) union all select NULL AS `transaction_id`,NULL AS `client_email`,NULL AS `product_name`,NULL AS `product_cost`,NULL AS `offer_name`,NULL AS `payment_status`,NULL AS `total_price`,NULL AS `commission`,NULL AS `taxes`,NULL AS `total_refund`,NULL AS `has_upsell`,NULL AS `total_price_upsell`,NULL AS `has_upsell2`,NULL AS `total_price_upsell2`,NULL AS `has_upsell3`,NULL AS `total_price_upsell3`,NULL AS `has_downsell`,NULL AS `total_price_downsell`,NULL AS `has_downsell2`,NULL AS `total_price_downsell2`,NULL AS `has_downsell3`,NULL AS `total_price_downsell3`,`ma`.`created_at_date` AS `created_at_date`,NULL AS `created_at_hour`,NULL AS `utm_content`,'facebook-ads' AS `platform`,`ma`.`account_id` AS `account_id`,`ma`.`account_name` AS `account_name`,`ma`.`campaign_name` AS `campaign_name`,`ma`.`adset_name` AS `adset_name`,`ma`.`ad_name` AS `ad_name`,`ma`.`ad_id` AS `ad_id`,`ma`.`amount_spent_brl` AS `amount_spent_brl`,`ma`.`impressions` AS `impressions`,`ma`.`reach` AS `reach`,`ma`.`link_clicks` AS `link_clicks`,NULL AS `imposto` from `instituto_experience`.`meta_ad_id` `ma` where (`ma`.`created_at_date` >= '2025-05-01') union all select NULL AS `transaction_id`,NULL AS `client_email`,NULL AS `product_name`,NULL AS `product_cost`,NULL AS `offer_name`,NULL AS `payment_status`,NULL AS `total_price`,NULL AS `commission`,NULL AS `taxes`,NULL AS `total_refund`,NULL AS `has_upsell`,NULL AS `total_price_upsell`,NULL AS `has_upsell2`,NULL AS `total_price_upsell2`,NULL AS `has_upsell3`,NULL AS `total_price_upsell3`,NULL AS `has_downsell`,NULL AS `total_price_downsell`,NULL AS `has_downsell2`,NULL AS `total_price_downsell2`,NULL AS `has_downsell3`,NULL AS `total_price_downsell3`,`ga`.`created_at_date` AS `created_at_date`,NULL AS `created_at_hour`,NULL AS `utm_content`,'google-ads' AS `platform`,`ga`.`account_id` AS `account_id`,`ga`.`account_name` AS `account_name`,`ga`.`campaign_name` AS `campaign_name`,`ga`.`adset_name` AS `adset_name`,`ga`.`ad_name` AS `ad_name`,`ga`.`ad_id` AS `ad_id`,`ga`.`amount_spent_brl` AS `amount_spent_brl`,`ga`.`impressions` AS `impressions`,NULL AS `reach`,`ga`.`link_clicks` AS `link_clicks`,NULL AS `imposto` from `instituto_experience`.`google_ad_id` `ga` where (`ga`.`created_at_date` >= '2025-05-01')
```
