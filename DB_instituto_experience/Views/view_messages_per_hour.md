---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 7
tags: [view]
---

# view_messages_per_hour

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 7 |

## Lê de
[[telegram_team_members]]

## Lida por
—

## Definição SQL

```sql
select cast(substr(`m`.`message_sent_at_hour`,1,2) as unsigned) AS `hour_of_day`,dayname(`m`.`message_sent_at_date`) AS `day_of_week`,dayofweek(`m`.`message_sent_at_date`) AS `day_of_week_num`,count(0) AS `total_messages`,sum((case when (`tm`.`user_id` is not null) then 1 else 0 end)) AS `team_messages`,sum((case when (`tm`.`user_id` is null) then 1 else 0 end)) AS `affiliate_messages`,count(distinct `m`.`chat_id`) AS `groups_with_activity` from (`instituto_experience`.`telegram_groups_backup` `m` left join `instituto_experience`.`telegram_team_members` `tm` on((`m`.`user_id` = `tm`.`user_id`))) group by cast(substr(`m`.`message_sent_at_hour`,1,2) as unsigned),dayname(`m`.`message_sent_at_date`),dayofweek(`m`.`message_sent_at_date`)
```
