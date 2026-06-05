---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 2
tags: [view]
---

# v_primeiro_mes_afiliado

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 2 |

## Lê de
[[dashboard_affiliate_nutra_usd]]

## Lida por
[[v_novos_recorrentes]]

## Definição SQL

```sql
select `instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` AS `affiliate_name`,date_format(min(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`created_at_date`),'%Y-%m') AS `primeiro_mes` from `instituto_experience`.`dashboard_affiliate_nutra_usd` where (`instituto_experience`.`dashboard_affiliate_nutra_usd`.`payment_status` = 'approved') group by `instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name`
```
