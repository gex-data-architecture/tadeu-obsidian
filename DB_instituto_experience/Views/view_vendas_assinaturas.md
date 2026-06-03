---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 11
tags: [view]
---

# view_vendas_assinaturas

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 11 |

## Lê de
[[cartpanda_physical]], [[guru_info]], [[guru_physical]], [[hotmart_info]], [[payt_info]], [[payt_physical]]

## Lida por
—

## Definição SQL

```sql
select `combined_data`.`transaction_id` AS `transaction_id`,`combined_data`.`client_email` AS `client_email`,`combined_data`.`payment_status` AS `payment_status`,`combined_data`.`total_price` AS `total_price`,`combined_data`.`commission` AS `commission`,`combined_data`.`created_at_date` AS `created_at_date`,(case when (`combined_data`.`commission` <> 0) then (`combined_data`.`total_price` * 0.10) else 0 end) AS `imposto`,`combined_data`.`subscription_id` AS `subscription_id`,`combined_data`.`subscription_status` AS `subscription_status`,`combined_data`.`subscription_cycle` AS `subscription_cycle`,`combined_data`.`subscription_next_charge_at` AS `subscription_next_charge_at` from (select `instituto_experience`.`hotmart_info`.`transaction_id` AS `transaction_id`,`instituto_experience`.`hotmart_info`.`client_email` AS `client_email`,`instituto_experience`.`hotmart_info`.`payment_status` AS `payment_status`,`instituto_experience`.`hotmart_info`.`total_price` AS `total_price`,`instituto_experience`.`hotmart_info`.`commission` AS `commission`,`instituto_experience`.`hotmart_info`.`created_at_date` AS `created_at_date`,`instituto_experience`.`hotmart_info`.`subscription_id` AS `subscription_id`,`instituto_experience`.`hotmart_info`.`subscription_status` AS `subscription_status`,`instituto_experience`.`hotmart_info`.`subscription_cycle` AS `subscription_cycle`,`instituto_experience`.`hotmart_info`.`subscription_next_charge_at` AS `subscription_next_charge_at` from `instituto_experience`.`hotmart_info` union all select `instituto_experience`.`payt_info`.`transaction_id` AS `transaction_id`,`instituto_experience`.`payt_info`.`client_email` AS `client_email`,`instituto_experience`.`payt_info`.`payment_status` AS `payment_status`,`instituto_experience`.`payt_info`.`total_price` AS `total_price`,`instituto_experience`.`payt_info`.`commission` AS `commission`,`instituto_experience`.`payt_info`.`created_at_date` AS `created_at_date`,`instituto_experience`.`payt_info`.`subscription_id` AS `subscription_id`,`instituto_experience`.`payt_info`.`subscription_status` AS `subscription_status`,`instituto_experience`.`payt_info`.`subscription_cycle` AS `subscription_cycle`,`instituto_experience`.`payt_info`.`subscription_next_charge_at` AS `subscription_next_charge_at` from `instituto_experience`.`payt_info` union all select `instituto_experience`.`guru_info`.`transaction_id` AS `transaction_id`,`instituto_experience`.`guru_info`.`client_email` AS `client_email`,`instituto_experience`.`guru_info`.`payment_status` AS `payment_status`,`instituto_experience`.`guru_info`.`total_price` AS `total_price`,`instituto_experience`.`guru_info`.`commission` AS `commission`,`instituto_experience`.`guru_info`.`created_at_date` AS `created_at_date`,`instituto_experience`.`guru_info`.`subscription_id` AS `subscription_id`,`instituto_experience`.`guru_info`.`subscription_status` AS `subscription_status`,`instituto_experience`.`guru_info`.`subscription_cycle` AS `subscription_cycle`,`instituto_experience`.`guru_info`.`subscription_next_charge_at` AS `subscription_next_charge_at` from `instituto_experience`.`guru_info` union all select `instituto_experience`.`payt_physical`.`transaction_id` AS `transaction_id`,`instituto_experience`.`payt_physical`.`client_email` AS `client_email`,`instituto_experience`.`payt_physical`.`payment_status` AS `payment_status`,`instituto_experience`.`payt_physical`.`total_price` AS `total_price`,`instituto_experience`.`payt_physical`.`commission` AS `commission`,`instituto_experience`.`payt_physical`.`created_at_date` AS `created_at_date`,NULL AS `subscription_id`,NULL AS `subscription_status`,NULL AS `subscription_cycle`,NULL AS `subscription_next_charge_at` from `instituto_experience`.`payt_physical` union all select `instituto_experience`.`cartpanda_physical`.`transaction_id` AS `transaction_id`,`instituto_experience`.`cartpanda_physical`.`client_email` AS `client_email`,`instituto_experience`.`cartpanda_physical`.`payment_status` AS `payment_status`,`instituto_experience`.`cartpanda_physical`.`total_price` AS `total_price`,`instituto_experience`.`cartpanda_physical`.`commission` AS `commission`,`instituto_experience`.`cartpanda_physical`.`created_at_date` AS `created_at_date`,NULL AS `subscription_id`,NULL AS `subscription_status`,NULL AS `subscription_cycle`,NULL AS `subscription_next_charge_at` from `instituto_experience`.`cartpanda_physical` union all select `instituto_experience`.`guru_physical`.`transaction_id` AS `transaction_id`,`instituto_experience`.`guru_physical`.`client_email` AS `client_email`,`instituto_experience`.`guru_physical`.`payment_status` AS `payment_status`,`instituto_experience`.`guru_physical`.`total_price` AS `total_price`,`instituto_experience`.`guru_physical`.`commission` AS `commission`,`instituto_experience`.`guru_physical`.`created_at_date` AS `created_at_date`,NULL AS `subscription_id`,NULL AS `subscription_status`,NULL AS `subscription_cycle`,NULL AS `subscription_next_charge_at` from `instituto_experience`.`guru_physical`) `combined_data` where (`combined_data`.`payment_status` in ('approved','refunded','chargeback'))
```
