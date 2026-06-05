---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 5
tags: [view]
---

# v_top5_longtail_mensal

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 5 |

## Lê de
[[dashboard_affiliate_nutra_usd]]

## Lida por
—

## Definição SQL

```sql
select (`final`.`mes_ordem` collate utf8mb4_general_ci) AS `mes_ordem`,(`final`.`mes` collate utf8mb4_general_ci) AS `mes`,(`final`.`categoria` collate utf8mb4_general_ci) AS `categoria`,sum(`final`.`revenue`) AS `revenue`,min(`final`.`created_at_date`) AS `created_at_date` from (select `ranked`.`mes_ordem` AS `mes_ordem`,`ranked`.`mes` AS `mes`,`ranked`.`affiliate_name` AS `affiliate_name`,`ranked`.`revenue` AS `revenue`,`ranked`.`created_at_date` AS `created_at_date`,(case when (`ranked`.`ranking` <= 5) then 'Top 5' else 'Long Tail' end) AS `categoria` from (select date_format(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`,'%Y-%m') AS `mes_ordem`,(case month(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`) when 1 then 'Jan' when 2 then 'Fev' when 3 then 'Mar' when 4 then 'Abr' when 5 then 'Mai' when 6 then 'Jun' when 7 then 'Jul' when 8 then 'Ago' when 9 then 'Set' when 10 then 'Out' when 11 then 'Nov' when 12 then 'Dez' end) AS `mes`,`instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` AS `affiliate_name`,sum(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`total_price`) AS `revenue`,min(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`) AS `created_at_date`,row_number() OVER (PARTITION BY date_format(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`,'%Y-%m') ORDER BY sum(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`total_price`) desc )  AS `ranking` from `instituto_experience`.`dashboard_affiliate_nutra_usd` where (`instituto_experience`.`dashboard_affiliate_nutra_usd`.`payment_status` = 'approved') group by date_format(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`,'%Y-%m'),month(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`),`instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name`) `ranked`) `final` group by `final`.`mes_ordem`,`final`.`mes`,`final`.`categoria` order by `mes_ordem`,`categoria`
```
