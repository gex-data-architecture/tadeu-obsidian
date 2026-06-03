---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 4
tags: [view]
---

# vw_affiliate_ranking_mes

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 4 |

## Lê de
[[affiliate_nutra]]

## Lida por
—

## Definição SQL

```sql
select date_format(`instituto_experience`.`affiliate_nutra`.`created_at_date`,'%Y-%m') AS `mes`,`instituto_experience`.`affiliate_nutra`.`affiliate_name` AS `affiliate_name`,sum(`instituto_experience`.`affiliate_nutra`.`total_price`) AS `revenue`,row_number() OVER (PARTITION BY date_format(`instituto_experience`.`affiliate_nutra`.`created_at_date`,'%Y-%m') ORDER BY sum(`instituto_experience`.`affiliate_nutra`.`total_price`) desc )  AS `ranking` from `instituto_experience`.`affiliate_nutra` where ((`instituto_experience`.`affiliate_nutra`.`offer_name` like '%Affiliate Marketing%') and (`instituto_experience`.`affiliate_nutra`.`affiliate_name` is not null) and (`instituto_experience`.`affiliate_nutra`.`payment_status` = 'approved')) group by `mes`,`instituto_experience`.`affiliate_nutra`.`affiliate_name`
```
