---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 4
tags: [view]
---

# v_top5_longtail

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 4 |

## Lê de
[[affiliate_nutra]]

## Lida por
—

## Definição SQL

```sql
select `sub`.`affiliate_name` AS `affiliate_name`,`sub`.`revenue` AS `revenue`,`sub`.`ranking` AS `ranking`,(case when (`sub`.`ranking` <= 5) then 'Top 5' else 'Long Tail' end) AS `categoria` from (select `instituto_experience`.`affiliate_nutra`.`affiliate_name` AS `affiliate_name`,sum(`instituto_experience`.`affiliate_nutra`.`total_price`) AS `revenue`,row_number() OVER (ORDER BY sum(`instituto_experience`.`affiliate_nutra`.`total_price`) desc )  AS `ranking` from `instituto_experience`.`affiliate_nutra` where ((`instituto_experience`.`affiliate_nutra`.`offer_name` like '%Affiliate Marketing%') and (`instituto_experience`.`affiliate_nutra`.`affiliate_name` is not null) and (`instituto_experience`.`affiliate_nutra`.`payment_status` = 'approved')) group by `instituto_experience`.`affiliate_nutra`.`affiliate_name`) `sub`
```
