---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 23
tags: [view]
---

# v_messages_enriched

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 23 |

## Lê de
[[telegram_groups_metadata]], [[telegram_team_members]]

## Lida por
—

## Definição SQL

```sql
select `b`.`event_id` AS `event_id`,`b`.`message_id` AS `message_id`,`b`.`chat_id` AS `chat_id`,coalesce(`m`.`group_name`,`b`.`group_name`) AS `group_name`,`b`.`user_id` AS `user_id`,`b`.`first_name` AS `first_name`,`b`.`telegram_username` AS `telegram_username`,`b`.`message` AS `message`,`b`.`message_sent_at_date` AS `message_sent_at_date`,`b`.`message_sent_at_hour` AS `message_sent_at_hour`,`b`.`created_at` AS `created_at`,(case when (`t`.`user_id` is not null) then 'team' else 'affiliate' end) AS `sender_type`,`t`.`first_name` AS `agent_name`,`t`.`role` AS `agent_role`,`m`.`tier` AS `tier`,`m`.`partners` AS `partners`,`m`.`status` AS `group_status`,(case when (`m`.`tier` = 'Tier 1') then 60 when (`m`.`tier` = 'Tier 2') then 120 else 180 end) AS `sla_target_minutes`,hour(`b`.`message_sent_at_hour`) AS `hour_of_day`,dayofweek(`b`.`message_sent_at_date`) AS `day_of_week`,(case dayofweek(`b`.`message_sent_at_date`) when 1 then 'Dom' when 2 then 'Seg' when 3 then 'Ter' when 4 then 'Qua' when 5 then 'Qui' when 6 then 'Sex' when 7 then 'Sab' end) AS `day_name`,(case when (hour(`b`.`message_sent_at_hour`) >= 8) then 1 else 0 end) AS `is_within_window`,(case when (`b`.`message` = 'photo') then 'photo' when (`b`.`message` like 'http%') then 'link' when (`b`.`message` like '/%') then 'command' else 'text' end) AS `message_type` from ((`instituto_experience`.`telegram_groups_backup` `b` join `instituto_experience`.`telegram_groups_metadata` `m` on((`b`.`chat_id` = `m`.`chat_id`))) left join `instituto_experience`.`telegram_team_members` `t` on(((`b`.`user_id` = `t`.`user_id`) and (`t`.`is_active` = 1))))
```
