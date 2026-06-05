---
tipo: view
definer: "diego@%"
security_type: "DEFINER"
colunas: 0
tags: [view]
---

# vw_enriquecimento_buygoods

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | diego@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 0 |

## Lê de
[[buygoods_new]], [[buygoods_physical]], [[unified_lead_events_new]], [[unified_lead_events_new_backup_1]], [[unified_lead_events_v2]]

## Lida por
—

## Definição SQL

```sql
select (trim(concat(coalesce(`instituto_experience`.`unified_lead_events_new`.`client_first_name`,''),' ',coalesce(`instituto_experience`.`unified_lead_events_new`.`client_last_name`,''))) collate utf8mb4_unicode_ci) AS `full_name`,(`instituto_experience`.`unified_lead_events_new`.`client_email` collate utf8mb4_unicode_ci) AS `email`,(`instituto_experience`.`unified_lead_events_new`.`client_phone` collate utf8mb4_unicode_ci) AS `phone`,`instituto_experience`.`unified_lead_events_new`.`order_date` AS `order_date` from `instituto_experience`.`unified_lead_events_new` where ((`instituto_experience`.`unified_lead_events_new`.`platform` = 'buygoods') and (trim(coalesce(`instituto_experience`.`unified_lead_events_new`.`client_phone`,'')) <> '') and (trim(coalesce(`instituto_experience`.`unified_lead_events_new`.`client_email`,'')) <> '')) union all select (trim(concat(coalesce(`instituto_experience`.`unified_lead_events_new_backup_1`.`client_first_name`,''),' ',coalesce(`instituto_experience`.`unified_lead_events_new_backup_1`.`client_last_name`,''))) collate utf8mb4_unicode_ci) AS `Name_exp_5`,(`instituto_experience`.`unified_lead_events_new_backup_1`.`client_email` collate utf8mb4_unicode_ci) AS `client_email COLLATE utf8mb4_unicode_ci`,(`instituto_experience`.`unified_lead_events_new_backup_1`.`client_phone` collate utf8mb4_unicode_ci) AS `client_phone COLLATE utf8mb4_unicode_ci`,`instituto_experience`.`unified_lead_events_new_backup_1`.`order_date` AS `order_date` from `instituto_experience`.`unified_lead_events_new_backup_1` where ((`instituto_experience`.`unified_lead_events_new_backup_1`.`platform` = 'buygoods') and (trim(coalesce(`instituto_experience`.`unified_lead_events_new_backup_1`.`client_phone`,'')) <> '') and (trim(coalesce(`instituto_experience`.`unified_lead_events_new_backup_1`.`client_email`,'')) <> '')) union all select (trim(concat(coalesce(`instituto_experience`.`unified_lead_events_v2`.`client_first_name`,''),' ',coalesce(`instituto_experience`.`unified_lead_events_v2`.`client_last_name`,''))) collate utf8mb4_unicode_ci) AS `Name_exp_9`,(`instituto_experience`.`unified_lead_events_v2`.`client_email` collate utf8mb4_unicode_ci) AS `client_email COLLATE utf8mb4_unicode_ci`,(`instituto_experience`.`unified_lead_events_v2`.`client_phone` collate utf8mb4_unicode_ci) AS `client_phone COLLATE utf8mb4_unicode_ci`,`instituto_experience`.`unified_lead_events_v2`.`order_date` AS `order_date` from `instituto_experience`.`unified_lead_events_v2` where ((`instituto_experience`.`unified_lead_events_v2`.`platform` = 'buygoods') and (trim(coalesce(`instituto_experience`.`unified_lead_events_v2`.`client_phone`,'')) <> '') and (trim(coalesce(`instituto_experience`.`unified_lead_events_v2`.`client_email`,'')) <> '')) union all select (`instituto_experience`.`buygoods_physical`.`client_name` collate utf8mb4_unicode_ci) AS `client_name  COLLATE utf8mb4_unicode_ci`,(`instituto_experience`.`buygoods_physical`.`client_email` collate utf8mb4_unicode_ci) AS `client_email COLLATE utf8mb4_unicode_ci`,(`instituto_experience`.`buygoods_physical`.`client_phone` collate utf8mb4_unicode_ci) AS `client_phone COLLATE utf8mb4_unicode_ci`,`instituto_experience`.`buygoods_physical`.`created_at_date` AS `created_at_date` from `instituto_experience`.`buygoods_physical` where ((trim(coalesce(`instituto_experience`.`buygoods_physical`.`client_phone`,'')) <> '') and (trim(coalesce(`instituto_experience`.`buygoods_physical`.`client_email`,'')) <> '') and (`instituto_experience`.`buygoods_physical`.`payment_status` = 'COMPLETE')) union all select (trim(concat(coalesce(`instituto_experience`.`buygoods_new`.`customer_firstname`,''),' ',coalesce(`instituto_experience`.`buygoods_new`.`customer_lastname`,''))) collate utf8mb4_unicode_ci) AS `Name_exp_17`,(`instituto_experience`.`buygoods_new`.`customer_emailaddress` collate utf8mb4_unicode_ci) AS `customer_emailaddress COLLATE utf8mb4_unicode_ci`,(`instituto_experience`.`buygoods_new`.`customer_phone` collate utf8mb4_unicode_ci) AS `customer_phone        COLLATE utf8mb4_unicode_ci`,str_to_date(`instituto_experience`.`buygoods_new`.`order_date`,'%m/%d/%Y') AS `STR_TO_DATE(order_date, '%m/%d/%Y')` from `instituto_experience`.`buygoods_new` where ((trim(coalesce(`instituto_experience`.`buygoods_new`.`customer_phone`,'')) <> '') and (trim(coalesce(`instituto_experience`.`buygoods_new`.`customer_emailaddress`,'')) <> '') and (`instituto_experience`.`buygoods_new`.`payment_status` = 'COMPLETE')) union all select (trim(concat(coalesce(`instituto_experience`.`buygoods_orders`.`customer_firstname`,''),' ',coalesce(`instituto_experience`.`buygoods_orders`.`customer_lastname`,''))) collate utf8mb4_unicode_ci) AS `Name_exp_21`,(`instituto_experience`.`buygoods_orders`.`customer_emailaddress` collate utf8mb4_unicode_ci) AS `customer_emailaddress COLLATE utf8mb4_unicode_ci`,(`instituto_experience`.`buygoods_orders`.`customer_phone` collate utf8mb4_unicode_ci) AS `customer_phone        COLLATE utf8mb4_unicode_ci`,str_to_date(`instituto_experience`.`buygoods_orders`.`order_date`,'%m/%d/%Y') AS `STR_TO_DATE(order_date, '%m/%d/%Y')` from `instituto_experience`.`buygoods_orders` where ((trim(coalesce(`instituto_experience`.`buygoods_orders`.`customer_phone`,'')) <> '') and (trim(coalesce(`instituto_experience`.`buygoods_orders`.`customer_emailaddress`,'')) <> '') and (`instituto_experience`.`buygoods_orders`.`payment_status` = 'COMPLETE'))
```
