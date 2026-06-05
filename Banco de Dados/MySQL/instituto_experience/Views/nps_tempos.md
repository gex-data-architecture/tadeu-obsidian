---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 5
tags: [view]
---

# nps_tempos

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 5 |

## Lê de
[[nps_affiliate_groups]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`nps_affiliate_groups`.`ticket_id` AS `ticket_id`,`instituto_experience`.`nps_affiliate_groups`.`event` AS `event`,json_unquote(json_extract(`instituto_experience`.`nps_affiliate_groups`.`all_event_date`,'$.acesso')) AS `data_acesso`,json_unquote(json_extract(`instituto_experience`.`nps_affiliate_groups`.`all_event_date`,'$.finalizacao')) AS `data_finalizacao`,timestampdiff(SECOND,str_to_date(json_unquote(json_extract(`instituto_experience`.`nps_affiliate_groups`.`all_event_date`,'$.acesso')),'%Y-%m-%d %H:%i:%s'),str_to_date(json_unquote(json_extract(`instituto_experience`.`nps_affiliate_groups`.`all_event_date`,'$.finalizacao')),'%Y-%m-%d %H:%i:%s')) AS `tempo_segundos` from `instituto_experience`.`nps_affiliate_groups` where ((`instituto_experience`.`nps_affiliate_groups`.`event` = 'finalizacao') and (json_extract(`instituto_experience`.`nps_affiliate_groups`.`all_event_date`,'$.acesso') is not null) and (json_extract(`instituto_experience`.`nps_affiliate_groups`.`all_event_date`,'$.finalizacao') is not null))
```
