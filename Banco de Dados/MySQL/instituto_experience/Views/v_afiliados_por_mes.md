---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 3
tags: [view]
---

# v_afiliados_por_mes

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 3 |

## Lê de
[[dashboard_affiliate_nutra_usd]]

## Lida por
—

## Definição SQL

```sql
select date_format(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`,'%Y-%m') AS `mes_ordem`,count(distinct `instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name`) AS `total_afiliados`,min(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`) AS `created_at_date` from `instituto_experience`.`dashboard_affiliate_nutra_usd` where (`instituto_experience`.`dashboard_affiliate_nutra_usd`.`payment_status` = 'approved') group by date_format(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`,'%Y-%m')
```
