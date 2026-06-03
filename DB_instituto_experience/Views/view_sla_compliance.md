---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 8
tags: [view]
---

# view_sla_compliance

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 8 |

## Lê de
[[telegram_groups_metadata]], [[telegram_team_members]]

## Lida por
—

## Definição SQL

```sql
select `sub`.`chat_id` AS `chat_id`,`sub`.`group_name` AS `group_name`,`sub`.`tier` AS `tier`,`sub`.`message_sent_at_date` AS `message_sent_at_date`,`sub`.`responder_name` AS `responder_name`,`sub`.`response_time_minutes` AS `response_time_minutes`,(case when (`sub`.`response_time_minutes` <= 30) then 'Dentro SLA' when (`sub`.`response_time_minutes` <= 60) then 'Atencao' when (`sub`.`response_time_minutes` <= 120) then 'Critico' else 'Fora SLA' end) AS `sla_status`,(case when (`sub`.`response_time_minutes` <= 30) then 1 else 0 end) AS `within_sla` from (select `m`.`chat_id` AS `chat_id`,`m`.`group_name` AS `group_name`,`gm`.`tier` AS `tier`,`m`.`message_sent_at_date` AS `message_sent_at_date`,`m`.`first_name` AS `responder_name`,`m`.`user_id` AS `user_id`,(case when (`t1`.`user_id` is not null) then 'time' else 'afiliado' end) AS `sender_type`,lag((case when (`t1`.`user_id` is not null) then 'time' else 'afiliado' end)) OVER (PARTITION BY `m`.`chat_id` ORDER BY `m`.`message_sent_at_date`,`m`.`message_sent_at_hour`,`m`.`event_id` )  AS `prev_sender_type`,timestampdiff(MINUTE,lag(concat(`m`.`message_sent_at_date`,' ',`m`.`message_sent_at_hour`)) OVER (PARTITION BY `m`.`chat_id` ORDER BY `m`.`message_sent_at_date`,`m`.`message_sent_at_hour`,`m`.`event_id` ) ,concat(`m`.`message_sent_at_date`,' ',`m`.`message_sent_at_hour`)) AS `response_time_minutes` from ((`instituto_experience`.`telegram_groups_backup` `m` left join `instituto_experience`.`telegram_groups_metadata` `gm` on((`m`.`chat_id` = `gm`.`chat_id`))) left join `instituto_experience`.`telegram_team_members` `t1` on((`m`.`user_id` = `t1`.`user_id`)))) `sub` where ((`sub`.`sender_type` = 'time') and (`sub`.`prev_sender_type` = 'afiliado') and (`sub`.`response_time_minutes` is not null) and (`sub`.`response_time_minutes` > 0))
```
