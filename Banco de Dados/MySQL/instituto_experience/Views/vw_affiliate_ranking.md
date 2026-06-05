---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 3
tags: [view]
---

# vw_affiliate_ranking

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
[[vw_affiliate_share]]

## Definição SQL

```sql
select `instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` AS `affiliate_name`,sum(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`total_price`) AS `revenue`,row_number() OVER (ORDER BY sum(`instituto_experience`.`dashboard_affiliate_nutra_usd`.`total_price`) desc )  AS `ranking` from `instituto_experience`.`dashboard_affiliate_nutra_usd` where ((`instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name` is not null) and (`instituto_experience`.`dashboard_affiliate_nutra_usd`.`payment_status` = 'approved')) group by `instituto_experience`.`dashboard_affiliate_nutra_usd`.`affiliate_name`
```
