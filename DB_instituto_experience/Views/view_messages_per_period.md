---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 11
tags: [view]
---

# view_messages_per_period

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 11 |

## Lê de
[[telegram_team_members]]

## Lida por
—

## Definição SQL

```sql
select `m`.`message_sent_at_date` AS `date`,year(`m`.`message_sent_at_date`) AS `year`,month(`m`.`message_sent_at_date`) AS `month`,week(`m`.`message_sent_at_date`,0) AS `week`,dayname(`m`.`message_sent_at_date`) AS `day_of_week`,count(0) AS `total_messages`,sum((case when (`tm`.`user_id` is not null) then 1 else 0 end)) AS `team_messages`,sum((case when (`tm`.`user_id` is null) then 1 else 0 end)) AS `affiliate_messages`,count(distinct `m`.`chat_id`) AS `active_groups`,count(distinct (case when (`tm`.`user_id` is null) then `m`.`user_id` end)) AS `active_affiliates`,count(distinct (case when (`tm`.`user_id` is not null) then `m`.`user_id` end)) AS `active_team_members` from (`instituto_experience`.`telegram_groups_backup` `m` left join `instituto_experience`.`telegram_team_members` `tm` on((`m`.`user_id` = `tm`.`user_id`))) group by `m`.`message_sent_at_date`,year(`m`.`message_sent_at_date`),month(`m`.`message_sent_at_date`),week(`m`.`message_sent_at_date`,0),dayname(`m`.`message_sent_at_date`)
```
