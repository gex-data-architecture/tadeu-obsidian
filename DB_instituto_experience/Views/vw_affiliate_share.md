---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 3
tags: [view]
---

# vw_affiliate_share

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 3 |

## Lê de
[[vw_affiliate_ranking]]

## Lida por
—

## Definição SQL

```sql
select (case when (`instituto_experience`.`vw_affiliate_ranking`.`ranking` <= 5) then 'Top 5' else 'Long Tail' end) AS `categoria`,sum(`instituto_experience`.`vw_affiliate_ranking`.`revenue`) AS `total`,round((sum(`instituto_experience`.`vw_affiliate_ranking`.`revenue`) / (select sum(`instituto_experience`.`vw_affiliate_ranking`.`revenue`) from `instituto_experience`.`vw_affiliate_ranking`)),3) AS `percentual` from `instituto_experience`.`vw_affiliate_ranking` group by `categoria`
```
