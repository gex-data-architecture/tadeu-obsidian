---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 36
tags: [view]
---

# affiliate_nutra_clickbank_new

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 36 |

## Lê de
[[clickbank_physical_new]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`clickbank_physical_new`.`transaction_id` AS `transaction_id`,`instituto_experience`.`clickbank_physical_new`.`client_email` AS `client_email`,`instituto_experience`.`clickbank_physical_new`.`product_name` AS `product_name`,`instituto_experience`.`clickbank_physical_new`.`product_cost` AS `product_cost`,`instituto_experience`.`clickbank_physical_new`.`offer_name` AS `offer_name`,`instituto_experience`.`clickbank_physical_new`.`payment_status` AS `payment_status`,`instituto_experience`.`clickbank_physical_new`.`total_price` AS `total_price`,`instituto_experience`.`clickbank_physical_new`.`commission` AS `commission`,`instituto_experience`.`clickbank_physical_new`.`taxes` AS `taxes`,`instituto_experience`.`clickbank_physical_new`.`total_refund` AS `total_refund`,0 AS `has_order_bump`,0.00 AS `total_price_order_bump`,0 AS `has_upsell`,0.00 AS `total_price_upsell`,0 AS `has_upsell2`,0.00 AS `total_price_upsell2`,0 AS `has_upsell3`,0.00 AS `total_price_upsell3`,0 AS `has_downsell`,0.00 AS `total_price_downsell`,0 AS `has_downsell2`,0.00 AS `total_price_downsell2`,0 AS `has_downsell3`,0.00 AS `total_price_downsell3`,`instituto_experience`.`clickbank_physical_new`.`created_at_date` AS `created_at_date`,`instituto_experience`.`clickbank_physical_new`.`created_at_hour` AS `created_at_hour`,`instituto_experience`.`clickbank_physical_new`.`affiliate_name` AS `affiliate_name`,cast(NULL as char(50) charset utf8mb4) AS `affiliate_id`,`instituto_experience`.`clickbank_physical_new`.`affiliate_amount` AS `affiliate_amount`,`instituto_experience`.`clickbank_physical_new`.`utm_content` AS `utm_content`,cast(NULL as char(50) charset utf8mb4) AS `coupon_code`,'clickbank' AS `platform`,(case when ((lower(`instituto_experience`.`clickbank_physical_new`.`product_sku`) like '%1unit%') or (lower(`instituto_experience`.`clickbank_physical_new`.`product_sku`) like '%2unit%')) then 1 else 0 end) AS `1_2_units_sales`,(case when ((lower(`instituto_experience`.`clickbank_physical_new`.`product_sku`) like '%3unit%') or (lower(`instituto_experience`.`clickbank_physical_new`.`product_sku`) like '%4unit%')) then 1 else 0 end) AS `3_4_units_sales`,(case when ((lower(`instituto_experience`.`clickbank_physical_new`.`product_sku`) like '%5unit%') or (lower(`instituto_experience`.`clickbank_physical_new`.`product_sku`) like '%6unit%')) then 1 else 0 end) AS `5_6_units_sales`,(case when (`instituto_experience`.`clickbank_physical_new`.`payment_status` in ('approved','refunded_partial')) then (case when (`instituto_experience`.`clickbank_physical_new`.`created_at_date` >= '2025-04-01') then (`instituto_experience`.`clickbank_physical_new`.`total_price` * 0.03) else (`instituto_experience`.`clickbank_physical_new`.`total_price` * 0.10) end) else 0 end) AS `imposto` from `instituto_experience`.`clickbank_physical_new` where ((`instituto_experience`.`clickbank_physical_new`.`payment_status` in ('approved','refunded','chargeback','refunded_partial')) and (`instituto_experience`.`clickbank_physical_new`.`affiliate_name` is not null) and (`instituto_experience`.`clickbank_physical_new`.`affiliate_name` <> ''))
```
