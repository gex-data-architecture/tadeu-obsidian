---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 41
tags: [view]
---

# dashboard_gold_clickbank_dados_brutos

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 41 |

## Lê de
[[clickbank_physical_new_aws]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`clickbank_physical_new_aws`.`transaction_id` AS `transaction_id`,`instituto_experience`.`clickbank_physical_new_aws`.`payment_status` AS `payment_status`,`instituto_experience`.`clickbank_physical_new_aws`.`client_name` AS `client_name`,`instituto_experience`.`clickbank_physical_new_aws`.`client_email` AS `client_email`,`instituto_experience`.`clickbank_physical_new_aws`.`client_phone` AS `client_phone`,`instituto_experience`.`clickbank_physical_new_aws`.`client_zip` AS `client_zip`,`instituto_experience`.`clickbank_physical_new_aws`.`client_country` AS `client_country`,`instituto_experience`.`clickbank_physical_new_aws`.`client_state` AS `client_state`,`instituto_experience`.`clickbank_physical_new_aws`.`client_city` AS `client_city`,`instituto_experience`.`clickbank_physical_new_aws`.`client_street` AS `client_street`,`instituto_experience`.`clickbank_physical_new_aws`.`product_name` AS `product_name`,`instituto_experience`.`clickbank_physical_new_aws`.`product_sku` AS `product_sku`,`instituto_experience`.`clickbank_physical_new_aws`.`offer_name` AS `offer_name`,`instituto_experience`.`clickbank_physical_new_aws`.`product_cost` AS `product_cost`,`instituto_experience`.`clickbank_physical_new_aws`.`product_cost_usd` AS `product_cost_usd`,`instituto_experience`.`clickbank_physical_new_aws`.`quantity` AS `quantity`,`instituto_experience`.`clickbank_physical_new_aws`.`total_price` AS `total_price`,`instituto_experience`.`clickbank_physical_new_aws`.`total_price_usd` AS `total_price_usd`,`instituto_experience`.`clickbank_physical_new_aws`.`taxes` AS `taxes`,`instituto_experience`.`clickbank_physical_new_aws`.`taxes_usd` AS `taxes_usd`,`instituto_experience`.`clickbank_physical_new_aws`.`total_refund` AS `total_refund`,`instituto_experience`.`clickbank_physical_new_aws`.`total_refund_usd` AS `total_refund_usd`,`instituto_experience`.`clickbank_physical_new_aws`.`commission` AS `commission`,`instituto_experience`.`clickbank_physical_new_aws`.`commission_usd` AS `commission_usd`,`instituto_experience`.`clickbank_physical_new_aws`.`affiliate_amount` AS `affiliate_amount`,`instituto_experience`.`clickbank_physical_new_aws`.`affiliate_amount_usd` AS `affiliate_amount_usd`,`instituto_experience`.`clickbank_physical_new_aws`.`is_house_traffic` AS `is_house_traffic`,`instituto_experience`.`clickbank_physical_new_aws`.`sales_type` AS `sales_type`,`instituto_experience`.`clickbank_physical_new_aws`.`date_refunded` AS `date_refunded`,`instituto_experience`.`clickbank_physical_new_aws`.`utm_source` AS `utm_source`,`instituto_experience`.`clickbank_physical_new_aws`.`utm_medium` AS `utm_medium`,`instituto_experience`.`clickbank_physical_new_aws`.`utm_content` AS `utm_content`,`instituto_experience`.`clickbank_physical_new_aws`.`utm_term` AS `utm_term`,`instituto_experience`.`clickbank_physical_new_aws`.`utm_campaign` AS `utm_campaign`,`instituto_experience`.`clickbank_physical_new_aws`.`src` AS `src`,`instituto_experience`.`clickbank_physical_new_aws`.`platform` AS `platform`,`instituto_experience`.`clickbank_physical_new_aws`.`affiliate_name` AS `affiliate_name`,`instituto_experience`.`clickbank_physical_new_aws`.`vendor_name` AS `vendor_name`,`instituto_experience`.`clickbank_physical_new_aws`.`created_at_date` AS `created_at_date`,`instituto_experience`.`clickbank_physical_new_aws`.`created_at_hour` AS `created_at_hour`,cast(concat(`instituto_experience`.`clickbank_physical_new_aws`.`created_at_date`,' ',`instituto_experience`.`clickbank_physical_new_aws`.`created_at_hour`) as datetime) AS `created_at_ts` from `instituto_experience`.`clickbank_physical_new_aws` FORCE INDEX (`idx_cbp_created_at_date`) where ((`instituto_experience`.`clickbank_physical_new_aws`.`created_at_date` >= '2026-01-01') or (`instituto_experience`.`clickbank_physical_new_aws`.`created_at_date` is null))
```
