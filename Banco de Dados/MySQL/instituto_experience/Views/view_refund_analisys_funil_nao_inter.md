---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 6
tags: [view]
---

# view_refund_analisys_funil_nao_inter

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 6 |

## Lê de
[[guru_info]], [[hotmart_info]], [[payt_info]]

## Lida por
—

## Definição SQL

```sql
select `combined_data`.`product_name` AS `product_name`,`combined_data`.`created_at_date` AS `created_at_date`,`combined_data`.`offer_name` AS `offer_name`,sum((case when (`combined_data`.`payment_status` in ('refunded','chargeback','refunded_partial')) then `combined_data`.`total_price` else 0 end)) AS `sum_refunded_total_price`,count((case when (`combined_data`.`payment_status` in ('approved','refunded','chargeback','refunded_partial')) then 1 else NULL end)) AS `total_sales_count`,sum((case when (`combined_data`.`payment_status` in ('refunded','chargeback','refunded_partial')) then 1 else 0 end)) AS `refunded_sales_count` from (select `instituto_experience`.`hotmart_info`.`product_name` AS `product_name`,`instituto_experience`.`hotmart_info`.`created_at_date` AS `created_at_date`,`instituto_experience`.`hotmart_info`.`total_price` AS `total_price`,`instituto_experience`.`hotmart_info`.`payment_status` AS `payment_status`,`instituto_experience`.`hotmart_info`.`offer_name` AS `offer_name` from `instituto_experience`.`hotmart_info` where ((`instituto_experience`.`hotmart_info`.`offer_name` like '%Funil de Nova Ideia%') and (not((`instituto_experience`.`hotmart_info`.`offer_name` like '%_INTER%')))) union all select `instituto_experience`.`payt_info`.`product_name` AS `product_name`,`instituto_experience`.`payt_info`.`created_at_date` AS `created_at_date`,`instituto_experience`.`payt_info`.`total_price` AS `total_price`,`instituto_experience`.`payt_info`.`payment_status` AS `payment_status`,`instituto_experience`.`payt_info`.`offer_name` AS `offer_name` from `instituto_experience`.`payt_info` where ((`instituto_experience`.`payt_info`.`offer_name` like '%Funil de Nova Ideia%') and (not((`instituto_experience`.`payt_info`.`offer_name` like '%_INTER%')))) union all select `instituto_experience`.`guru_info`.`product_name` AS `product_name`,`instituto_experience`.`guru_info`.`created_at_date` AS `created_at_date`,`instituto_experience`.`guru_info`.`total_price` AS `total_price`,`instituto_experience`.`guru_info`.`payment_status` AS `payment_status`,`instituto_experience`.`guru_info`.`offer_name` AS `offer_name` from `instituto_experience`.`guru_info` where ((`instituto_experience`.`guru_info`.`offer_name` like '%Funil de Nova Ideia%') and (not((`instituto_experience`.`guru_info`.`offer_name` like '%_INTER%'))))) `combined_data` group by `combined_data`.`product_name`,`combined_data`.`created_at_date`,`combined_data`.`offer_name`
```
