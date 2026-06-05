---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 10
tags: [view]
---

# view_team_performance

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 10 |

## Lê de
[[telegram_team_members]]

## Lida por
—

## Definição SQL

```sql
select `m`.`chat_id` AS `chat_id`,`m`.`group_name` AS `group_name`,`m`.`message_sent_at_date` AS `message_sent_at_date`,`m`.`message_sent_at_hour` AS `message_sent_at_hour`,`m`.`first_name` AS `team_member`,`m`.`user_id` AS `user_id`,`t`.`role` AS `role`,hour(`m`.`message_sent_at_hour`) AS `hour_of_day`,dayofweek(`m`.`message_sent_at_date`) AS `day_of_week`,date_format(`m`.`message_sent_at_date`,'%Y-%m') AS `year_month` from (`instituto_experience`.`telegram_groups_backup` `m` join `instituto_experience`.`telegram_team_members` `t` on((`m`.`user_id` = `t`.`user_id`)))
```
