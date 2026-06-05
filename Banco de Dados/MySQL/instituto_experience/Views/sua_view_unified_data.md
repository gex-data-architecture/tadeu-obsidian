---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 39
tags: [view]
---

# sua_view_unified_data

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 39 |

## Lê de
[[cartpanda_physical]], [[digistore_physical]]

## Lida por
—

## Definição SQL

```sql
select `ud`.`transaction_id` AS `transaction_id`,`ud`.`client_email` AS `client_email`,`ud`.`product_name` AS `product_name`,(case when (`ud`.`payment_status` in ('approved','refunded_partial')) then `ud`.`product_cost` else NULL end) AS `product_cost`,`ud`.`offer_name` AS `offer_name`,`ud`.`payment_status` AS `payment_status`,`ud`.`total_price` AS `total_price`,`ud`.`commission` AS `commission`,`ud`.`taxes` AS `taxes`,`ud`.`total_refund` AS `total_refund`,`ud`.`has_upsell` AS `has_upsell`,`ud`.`total_price_upsell` AS `total_price_upsell`,`ud`.`has_upsell2` AS `has_upsell2`,`ud`.`total_price_upsell2` AS `total_price_upsell2`,`ud`.`has_upsell3` AS `has_upsell3`,`ud`.`total_price_upsell3` AS `total_price_upsell3`,`ud`.`has_downsell` AS `has_downsell`,`ud`.`total_price_downsell` AS `total_price_downsell`,`ud`.`has_downsell2` AS `has_downsell2`,`ud`.`total_price_downsell2` AS `total_price_downsell2`,`ud`.`has_downsell3` AS `has_downsell3`,`ud`.`total_price_downsell3` AS `total_price_downsell3`,`ud`.`created_at_date` AS `created_at_date`,`ud`.`created_at_hour` AS `created_at_hour`,`ud`.`utm_content` AS `utm_content`,`ud`.`platform` AS `platform`,`ud`.`date_refunded` AS `date_refunded`,`ud`.`days_to_refund` AS `days_to_refund`,`ud`.`account_id` AS `account_id`,`ud`.`account_name` AS `account_name`,`ud`.`campaign_name` AS `campaign_name`,`ud`.`adset_name` AS `adset_name`,`ud`.`ad_name` AS `ad_name`,`ud`.`ad_id` AS `ad_id`,`ud`.`amount_spent_brl` AS `amount_spent_brl`,`ud`.`impressions` AS `impressions`,`ud`.`reach` AS `reach`,`ud`.`link_clicks` AS `link_clicks`,(case when (`ud`.`payment_status` in ('approved','refunded_partial')) then (case when (`ud`.`created_at_date` >= '2025-05-01') then (`ud`.`total_price` * 0.05) else (`ud`.`total_price` * 0.10) end) else 0 end) AS `imposto` from (select `cp`.`transaction_id` AS `transaction_id`,`cp`.`client_email` AS `client_email`,`cp`.`product_name` AS `product_name`,`cp`.`product_cost` AS `product_cost`,`cp`.`offer_name` AS `offer_name`,`cp`.`payment_status` AS `payment_status`,`cp`.`total_price` AS `total_price`,`cp`.`commission` AS `commission`,`cp`.`taxes` AS `taxes`,`cp`.`total_refund` AS `total_refund`,`cp`.`has_upsell` AS `has_upsell`,`cp`.`total_price_upsell` AS `total_price_upsell`,`cp`.`has_upsell2` AS `has_upsell2`,`cp`.`total_price_upsell2` AS `total_price_upsell2`,`cp`.`has_upsell3` AS `has_upsell3`,`cp`.`total_price_upsell3` AS `total_price_upsell3`,`cp`.`has_downsell` AS `has_downsell`,`cp`.`total_price_downsell` AS `total_price_downsell`,`cp`.`has_downsell2` AS `has_downsell2`,`cp`.`total_price_downsell2` AS `total_price_downsell2`,`cp`.`has_downsell3` AS `has_downsell3`,`cp`.`total_price_downsell3` AS `total_price_downsell3`,`cp`.`created_at_date` AS `created_at_date`,`cp`.`created_at_hour` AS `created_at_hour`,`cp`.`utm_content` AS `utm_content`,'cartpanda' AS `platform`,`cp`.`date_refunded` AS `date_refunded`,(to_days(`cp`.`date_refunded`) - to_days(`cp`.`created_at_date`)) AS `days_to_refund`,NULL AS `account_id`,NULL AS `account_name`,NULL AS `campaign_name`,NULL AS `adset_name`,NULL AS `ad_name`,NULL AS `ad_id`,NULL AS `amount_spent_brl`,NULL AS `impressions`,NULL AS `reach`,NULL AS `link_clicks` from `instituto_experience`.`cartpanda_physical` `cp` where ((`cp`.`payment_status` in ('approved','refunded','chargeback','refunded_partial')) and (not((lower(`cp`.`client_email`) like '%institutoexperience%')))) union all select `ds`.`transaction_id` AS `transaction_id`,`ds`.`client_email` AS `client_email`,`ds`.`product_name` AS `product_name`,`ds`.`product_cost` AS `product_cost`,`ds`.`offer_name` AS `offer_name`,`ds`.`payment_status` AS `payment_status`,`ds`.`total_price` AS `total_price`,`ds`.`commission` AS `commission`,`ds`.`taxes` AS `taxes`,`ds`.`total_refund` AS `total_refund`,NULL AS `has_upsell`,NULL AS `total_price_upsell`,NULL AS `has_upsell2`,NULL AS `total_price_upsell2`,NULL AS `has_upsell3`,NULL AS `total_price_upsell3`,NULL AS `has_downsell`,NULL AS `total_price_downsell`,NULL AS `has_downsell2`,NULL AS `total_price_downsell2`,NULL AS `has_downsell3`,NULL AS `total_price_downsell3`,`ds`.`created_at_date` AS `created_at_date`,`ds`.`created_at_hour` AS `created_at_hour`,`ds`.`utm_content` AS `utm_content`,'digistore' AS `platform`,`ds`.`date_refunded` AS `date_refunded`,(to_days(`ds`.`date_refunded`) - to_days(`ds`.`created_at_date`)) AS `days_to_refund`,NULL AS `account_id`,NULL AS `account_name`,NULL AS `campaign_name`,NULL AS `adset_name`,NULL AS `ad_name`,NULL AS `ad_id`,NULL AS `amount_spent_brl`,NULL AS `impressions`,NULL AS `reach`,NULL AS `link_clicks` from `instituto_experience`.`digistore_physical` `ds` where ((`ds`.`payment_status` in ('approved','refunded','chargeback','refunded_partial')) and (not((lower(`ds`.`client_email`) like '%institutoexperience%'))))) `ud`
```
