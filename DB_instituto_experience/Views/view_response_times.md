---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 12
tags: [view]
---

# view_response_times

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 12 |

## Lê de
[[telegram_groups_metadata]], [[telegram_team_members]]

## Lida por
—

## Definição SQL

```sql
select `m`.`chat_id` AS `chat_id`,`m`.`group_name` AS `group_name`,`m`.`message_id` AS `message_id`,`m`.`message_sent_at_date` AS `message_sent_at_date`,`m`.`message_sent_at_hour` AS `message_sent_at_hour`,`m`.`first_name` AS `responder_name`,`m`.`user_id` AS `responder_user_id`,(case when `m`.`user_id` in (select `instituto_experience`.`telegram_team_members`.`user_id` from `instituto_experience`.`telegram_team_members`) then 'time' else 'afiliado' end) AS `sender_type`,lag(`m`.`user_id`) OVER (PARTITION BY `m`.`chat_id` ORDER BY `m`.`message_sent_at_date`,`m`.`message_sent_at_hour`,`m`.`event_id` )  AS `prev_user_id`,lag((case when `m`.`user_id` in (select `instituto_experience`.`telegram_team_members`.`user_id` from `instituto_experience`.`telegram_team_members`) then 'time' else 'afiliado' end)) OVER (PARTITION BY `m`.`chat_id` ORDER BY `m`.`message_sent_at_date`,`m`.`message_sent_at_hour`,`m`.`event_id` )  AS `prev_sender_type`,timestampdiff(MINUTE,lag(concat(`m`.`message_sent_at_date`,' ',`m`.`message_sent_at_hour`)) OVER (PARTITION BY `m`.`chat_id` ORDER BY `m`.`message_sent_at_date`,`m`.`message_sent_at_hour`,`m`.`event_id` ) ,concat(`m`.`message_sent_at_date`,' ',`m`.`message_sent_at_hour`)) AS `response_time_minutes`,`gm`.`tier` AS `tier` from (`instituto_experience`.`telegram_groups_backup` `m` left join `instituto_experience`.`telegram_groups_metadata` `gm` on((`m`.`chat_id` = `gm`.`chat_id`)))
```
