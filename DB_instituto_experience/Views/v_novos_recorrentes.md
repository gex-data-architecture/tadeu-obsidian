---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 6
tags: [view]
---

# v_novos_recorrentes

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 6 |

## Lê de
[[v_primeiro_mes_afiliado]]

## Lida por
—

## Definição SQL

```sql
select (date_format(`a`.`created_at_date`,'%Y-%m') collate utf8mb4_general_ci) AS `mes_ordem`,((case month(`a`.`created_at_date`) when 1 then 'Jan' when 2 then 'Fev' when 3 then 'Mar' when 4 then 'Abr' when 5 then 'Mai' when 6 then 'Jun' when 7 then 'Jul' when 8 then 'Ago' when 9 then 'Set' when 10 then 'Out' when 11 then 'Nov' when 12 then 'Dez' end) collate utf8mb4_general_ci) AS `mes`,((case when (date_format(`a`.`created_at_date`,'%Y-%m') = (`instituto_experience`.`p`.`primeiro_mes` collate utf8mb4_unicode_ci)) then 'Novo' else 'Recorrente' end) collate utf8mb4_general_ci) AS `tipo`,sum(`a`.`total_price`) AS `revenue`,count(distinct `a`.`affiliate_name`) AS `qtd_afiliados`,min(`a`.`created_at_date`) AS `created_at_date` from (`instituto_experience`.`dashboard_affiliate_nutra_usd` `a` join `instituto_experience`.`v_primeiro_mes_afiliado` `p` on(((`a`.`affiliate_name` collate utf8mb4_unicode_ci) = (`instituto_experience`.`p`.`affiliate_name` collate utf8mb4_unicode_ci)))) where (`a`.`payment_status` = 'approved') group by date_format(`a`.`created_at_date`,'%Y-%m'),month(`a`.`created_at_date`),(case when (date_format(`a`.`created_at_date`,'%Y-%m') = (`instituto_experience`.`p`.`primeiro_mes` collate utf8mb4_unicode_ci)) then 'Novo' else 'Recorrente' end) order by `mes_ordem`,`tipo`
```
