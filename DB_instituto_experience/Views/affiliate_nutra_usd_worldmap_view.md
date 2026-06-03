---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 15
tags: [view]
---

# affiliate_nutra_usd_worldmap_view

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 15 |

## Lê de
[[cartpanda_physical]], [[digistore_physical]]

## Lida por
—

## Definição SQL

```sql
select `combined`.`transaction_id` AS `transaction_id`,`combined`.`client_email` AS `client_email`,`combined`.`client_country` AS `client_country`,`combined`.`client_state` AS `client_state`,`combined`.`client_city` AS `client_city`,`combined`.`client_zip` AS `client_zip`,`combined`.`product_name` AS `product_name`,`combined`.`offer_name` AS `offer_name`,`combined`.`payment_status` AS `payment_status`,round((`combined`.`total_price` / 5.5),2) AS `total_price`,round((`combined`.`total_refund` / 5.5),2) AS `total_refund`,`combined`.`affiliate_name` AS `affiliate_name`,`combined`.`affiliate_id` AS `affiliate_id`,`combined`.`created_at_date` AS `created_at_date`,`combined`.`platform` AS `platform` from (select `instituto_experience`.`cartpanda_physical`.`transaction_id` AS `transaction_id`,`instituto_experience`.`cartpanda_physical`.`client_email` AS `client_email`,`instituto_experience`.`cartpanda_physical`.`client_country` AS `client_country`,`instituto_experience`.`cartpanda_physical`.`client_state` AS `client_state`,`instituto_experience`.`cartpanda_physical`.`client_city` AS `client_city`,`instituto_experience`.`cartpanda_physical`.`client_zip` AS `client_zip`,`instituto_experience`.`cartpanda_physical`.`product_name` AS `product_name`,`instituto_experience`.`cartpanda_physical`.`offer_name` AS `offer_name`,`instituto_experience`.`cartpanda_physical`.`payment_status` AS `payment_status`,`instituto_experience`.`cartpanda_physical`.`total_price` AS `total_price`,`instituto_experience`.`cartpanda_physical`.`total_refund` AS `total_refund`,`instituto_experience`.`cartpanda_physical`.`affiliate_name` AS `affiliate_name`,`instituto_experience`.`cartpanda_physical`.`affiliate_id` AS `affiliate_id`,`instituto_experience`.`cartpanda_physical`.`created_at_date` AS `created_at_date`,'cartpanda' AS `platform` from `instituto_experience`.`cartpanda_physical` where ((`instituto_experience`.`cartpanda_physical`.`payment_status` in ('approved','refunded','chargeback','refunded_partial')) and (`instituto_experience`.`cartpanda_physical`.`affiliate_name` is not null) and (`instituto_experience`.`cartpanda_physical`.`affiliate_name` <> '')) union all select `instituto_experience`.`digistore_physical`.`transaction_id` AS `transaction_id`,`instituto_experience`.`digistore_physical`.`client_email` AS `client_email`,`instituto_experience`.`digistore_physical`.`client_country` AS `client_country`,`instituto_experience`.`digistore_physical`.`client_state` AS `client_state`,`instituto_experience`.`digistore_physical`.`client_city` AS `client_city`,`instituto_experience`.`digistore_physical`.`client_zip` AS `client_zip`,`instituto_experience`.`digistore_physical`.`product_name` AS `product_name`,`instituto_experience`.`digistore_physical`.`offer_name` AS `offer_name`,`instituto_experience`.`digistore_physical`.`payment_status` AS `payment_status`,`instituto_experience`.`digistore_physical`.`total_price` AS `total_price`,`instituto_experience`.`digistore_physical`.`total_refund` AS `total_refund`,`instituto_experience`.`digistore_physical`.`affiliate_name` AS `affiliate_name`,`instituto_experience`.`digistore_physical`.`affiliate_id` AS `affiliate_id`,`instituto_experience`.`digistore_physical`.`created_at_date` AS `created_at_date`,'digistore' AS `platform` from `instituto_experience`.`digistore_physical` where ((`instituto_experience`.`digistore_physical`.`payment_status` in ('approved','refunded','chargeback','refunded_partial')) and (`instituto_experience`.`digistore_physical`.`affiliate_name` is not null) and (`instituto_experience`.`digistore_physical`.`affiliate_name` <> ''))) `combined`
```
