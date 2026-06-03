---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 9
tags: [view]
---

# v_retencao_dias

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 9 |

## Lê de
[[dashboard_affiliate_nutra_usd]]

## Lida por
—

## Definição SQL

```sql
select count(distinct `sub`.`affiliate_name`) AS `total_afiliados`,sum((case when (`sub`.`dias_vida` >= 30) then 1 else 0 end)) AS `sobreviveram_30d`,sum((case when (`sub`.`dias_vida` >= 60) then 1 else 0 end)) AS `sobreviveram_60d`,sum((case when (`sub`.`dias_vida` >= 90) then 1 else 0 end)) AS `sobreviveram_90d`,sum((case when (`sub`.`dias_vida` >= 120) then 1 else 0 end)) AS `sobreviveram_120d`,round(((sum((case when (`sub`.`dias_vida` >= 30) then 1 else 0 end)) / count(distinct `sub`.`affiliate_name`)) * 100),2) AS `pct_30d`,round(((sum((case when (`sub`.`dias_vida` >= 60) then 1 else 0 end)) / count(distinct `sub`.`affiliate_name`)) * 100),2) AS `pct_60d`,round(((sum((case when (`sub`.`dias_vida` >= 90) then 1 else 0 end)) / count(distinct `sub`.`affiliate_name`)) * 100),2) AS `pct_90d`,round(((sum((case when (`sub`.`dias_vida` >= 120) then 1 else 0 end)) / count(distinct `sub`.`affiliate_name`)) * 100),2) AS `pct_120d` from (select `instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` AS `affiliate_name`,(to_days(max(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`)) - to_days(min(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`))) AS `dias_vida` from `instituto_experience`.`dashboard_affiliate_nutra_usd` where ((`instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` is not null) and (`instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` <> '') and (`instituto_experience`.`dashboard_affiliate_nutra_usd`.`payment_status` = 'approved')) group by `instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name`) `sub`
```
