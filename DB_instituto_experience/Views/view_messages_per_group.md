---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 11
tags: [view]
---

# view_messages_per_group

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 11 |

## Lê de
[[telegram_groups_metadata]], [[telegram_team_members]]

## Lida por
—

## Definição SQL

```sql
select `m`.`chat_id` AS `chat_id`,`m`.`group_name` AS `group_name`,`gm`.`tier` AS `tier`,`gm`.`partners` AS `partners`,`gm`.`sla_minutes` AS `sla_minutes`,`gm`.`status` AS `status`,count(0) AS `total_messages`,sum((case when (`tm`.`user_id` is not null) then 1 else 0 end)) AS `team_messages`,sum((case when (`tm`.`user_id` is null) then 1 else 0 end)) AS `affiliate_messages`,min(`m`.`message_sent_at_date`) AS `first_message_date`,max(`m`.`message_sent_at_date`) AS `last_message_date` from ((`instituto_experience`.`telegram_groups_backup` `m` left join `instituto_experience`.`telegram_groups_metadata` `gm` on((`m`.`chat_id` = `gm`.`chat_id`))) left join `instituto_experience`.`telegram_team_members` `tm` on((`m`.`user_id` = `tm`.`user_id`))) group by `m`.`chat_id`,`m`.`group_name`,`gm`.`tier`,`gm`.`partners`,`gm`.`sla_minutes`,`gm`.`status`
```
