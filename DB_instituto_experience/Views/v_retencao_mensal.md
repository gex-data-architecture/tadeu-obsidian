---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 6
tags: [view]
---

# v_retencao_mensal

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 6 |

## Lê de
[[dashboard_affiliate_nutra_usd]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`t`.`mes_ordem` AS `mes_ordem`,(case month(str_to_date(concat(`instituto_experience`.`t`.`mes_ordem`,'-01'),'%Y-%m-%d')) when 1 then 'Jan' when 2 then 'Fev' when 3 then 'Mar' when 4 then 'Abr' when 5 then 'Mai' when 6 then 'Jun' when 7 then 'Jul' when 8 then 'Ago' when 9 then 'Set' when 10 then 'Out' when 11 then 'Nov' when 12 then 'Dez' end) AS `mes`,`instituto_experience`.`t`.`total_afiliados` AS `total_afiliados`,count(distinct `prox`.`affiliate_name`) AS `retidos_proximo_mes`,round(((count(distinct `prox`.`affiliate_name`) / `instituto_experience`.`t`.`total_afiliados`) * 100),2) AS `taxa_retencao`,`instituto_experience`.`t`.`created_at_date` AS `created_at_date` from ((`instituto_experience`.`v_afiliados_por_mes` `t` left join (select distinct date_format(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`,'%Y-%m') AS `mes_ordem`,`instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` AS `affiliate_name` from `instituto_experience`.`dashboard_affiliate_nutra_usd` where ((`instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` is not null) and (`instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` <> '') and (`instituto_experience`.`dashboard_affiliate_nutra_usd`.`payment_status` = 'approved'))) `atual` on((`atual`.`mes_ordem` = `instituto_experience`.`t`.`mes_ordem`))) left join (select distinct date_format(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`,'%Y-%m') AS `mes_ordem`,`instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` AS `affiliate_name` from `instituto_experience`.`dashboard_affiliate_nutra_usd` where ((`instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` is not null) and (`instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` <> '') and (`instituto_experience`.`dashboard_affiliate_nutra_usd`.`payment_status` = 'approved'))) `prox` on(((`atual`.`affiliate_name` = `prox`.`affiliate_name`) and (`prox`.`mes_ordem` = date_format((str_to_date(concat(`instituto_experience`.`t`.`mes_ordem`,'-01'),'%Y-%m-%d') + interval 1 month),'%Y-%m'))))) group by `instituto_experience`.`t`.`mes_ordem`,`instituto_experience`.`t`.`total_afiliados`,`instituto_experience`.`t`.`created_at_date` order by `instituto_experience`.`t`.`mes_ordem`
```
