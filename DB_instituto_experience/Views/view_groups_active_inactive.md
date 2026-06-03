---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 9
tags: [view]
---

# view_groups_active_inactive

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 9 |

## Lê de
[[telegram_groups_metadata]]

## Lida por
—

## Definição SQL

```sql
select `m`.`chat_id` AS `chat_id`,`m`.`group_name` AS `group_name`,`gm`.`tier` AS `tier`,`gm`.`partners` AS `partners`,`gm`.`status` AS `metadata_status`,max(`m`.`message_sent_at_date`) AS `last_message_date`,(to_days(curdate()) - to_days(max(`m`.`message_sent_at_date`))) AS `days_since_last_message`,(case when ((to_days(curdate()) - to_days(max(`m`.`message_sent_at_date`))) <= 7) then 'Ativo (7d)' when ((to_days(curdate()) - to_days(max(`m`.`message_sent_at_date`))) <= 14) then 'Ativo (14d)' when ((to_days(curdate()) - to_days(max(`m`.`message_sent_at_date`))) <= 30) then 'Ativo (30d)' else 'Inativo' end) AS `activity_status`,count(0) AS `total_messages` from (`instituto_experience`.`telegram_groups_backup` `m` left join `instituto_experience`.`telegram_groups_metadata` `gm` on((`m`.`chat_id` = `gm`.`chat_id`))) group by `m`.`chat_id`,`m`.`group_name`,`gm`.`tier`,`gm`.`partners`,`gm`.`status`
```
