---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 36
tags: [view]
---

# clickbank_as_affiliate_nutra_usd

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 36 |

## Lê de
[[clickbank_physical]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`clickbank_physical`.`transaction_id` AS `transaction_id`,`instituto_experience`.`clickbank_physical`.`client_email` AS `client_email`,`instituto_experience`.`clickbank_physical`.`product_name` AS `product_name`,`instituto_experience`.`clickbank_physical`.`product_cost_usd` AS `product_cost`,`instituto_experience`.`clickbank_physical`.`offer_name` AS `offer_name`,`instituto_experience`.`clickbank_physical`.`payment_status` AS `payment_status`,`instituto_experience`.`clickbank_physical`.`total_collected_usd` AS `total_price`,`instituto_experience`.`clickbank_physical`.`commission_usd` AS `commission`,`instituto_experience`.`clickbank_physical`.`taxes_usd` AS `taxes`,`instituto_experience`.`clickbank_physical`.`total_refund_usd` AS `total_refund`,NULL AS `has_order_bump`,NULL AS `total_price_order_bump`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'UP1') then 1 else 0 end) AS `has_upsell`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'UP1') then `instituto_experience`.`clickbank_physical`.`total_collected_usd` else '0.00' end) AS `total_price_upsell`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'UP2') then 1 else 0 end) AS `has_upsell2`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'UP2') then `instituto_experience`.`clickbank_physical`.`total_collected_usd` else '0.00' end) AS `total_price_upsell2`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'UP3') then 1 else 0 end) AS `has_upsell3`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'UP3') then `instituto_experience`.`clickbank_physical`.`total_collected_usd` else '0.00' end) AS `total_price_upsell3`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'DW1') then 1 else 0 end) AS `has_downsell`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'DW1') then `instituto_experience`.`clickbank_physical`.`total_collected_usd` else '0.00' end) AS `total_price_downsell`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'DW2') then 1 else 0 end) AS `has_downsell2`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'DW2') then `instituto_experience`.`clickbank_physical`.`total_collected_usd` else '0.00' end) AS `total_price_downsell2`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'DW3') then 1 else 0 end) AS `has_downsell3`,(case when regexp_like(`instituto_experience`.`clickbank_physical`.`offer_id`,'DW3') then `instituto_experience`.`clickbank_physical`.`total_collected_usd` else '0.00' end) AS `total_price_downsell3`,`instituto_experience`.`clickbank_physical`.`created_at_date` AS `created_at_date`,`instituto_experience`.`clickbank_physical`.`created_at_hour` AS `created_at_hour`,`instituto_experience`.`clickbank_physical`.`affiliate_name` AS `affiliate_name`,`instituto_experience`.`clickbank_physical`.`affiliate_id` AS `affiliate_id`,`instituto_experience`.`clickbank_physical`.`affiliate_amount_usd` AS `affiliate_amount`,`instituto_experience`.`clickbank_physical`.`utm_content` AS `utm_content`,NULL AS `coupon_code`,`instituto_experience`.`clickbank_physical`.`platform` AS `platform`,(case when (`instituto_experience`.`clickbank_physical`.`quantity` in (1,2)) then 1 else 0 end) AS `1_2_units_sales`,(case when (`instituto_experience`.`clickbank_physical`.`quantity` in (3,4)) then 1 else 0 end) AS `3_4_units_sales`,(case when (`instituto_experience`.`clickbank_physical`.`quantity` >= 5) then 1 else 0 end) AS `5_6_units_sales`,(case when (`instituto_experience`.`clickbank_physical`.`payment_status` = 'approved') then round((cast(`instituto_experience`.`clickbank_physical`.`total_collected_usd` as decimal(10,2)) * 0.10),2) else 0.00 end) AS `imposto` from `instituto_experience`.`clickbank_physical`
```
