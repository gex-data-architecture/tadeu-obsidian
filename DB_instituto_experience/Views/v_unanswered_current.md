---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 10
tags: [view]
---

# v_unanswered_current

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 10 |

## Lê de
[[v_sla_calculations]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`sla`.`event_id` AS `event_id`,`instituto_experience`.`sla`.`chat_id` AS `chat_id`,`instituto_experience`.`sla`.`group_name` AS `group_name`,`instituto_experience`.`sla`.`affiliate_name` AS `affiliate_name`,`instituto_experience`.`sla`.`affiliate_msg_time` AS `affiliate_msg_time`,`instituto_experience`.`sla`.`message_sent_at_date` AS `message_sent_at_date`,`instituto_experience`.`sla`.`tier` AS `tier`,`instituto_experience`.`sla`.`sla_target_minutes` AS `sla_target_minutes`,timestampdiff(MINUTE,`instituto_experience`.`sla`.`sla_start_time`,now()) AS `minutes_waiting`,(case when (timestampdiff(MINUTE,`instituto_experience`.`sla`.`sla_start_time`,now()) <= (case when (`instituto_experience`.`sla`.`tier` = 'Tier 1') then 60 when (`instituto_experience`.`sla`.`tier` = 'Tier 2') then 120 else 180 end)) then 'Dentro SLA' when (timestampdiff(MINUTE,`instituto_experience`.`sla`.`sla_start_time`,now()) <= (case when (`instituto_experience`.`sla`.`tier` = 'Tier 1') then 120 when (`instituto_experience`.`sla`.`tier` = 'Tier 2') then 240 else 360 end)) then 'Atenção' else 'Crítico' end) AS `urgency_status` from `instituto_experience`.`v_sla_calculations` `sla` where (`instituto_experience`.`sla`.`was_answered` = 0)
```
