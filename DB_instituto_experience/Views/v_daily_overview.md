---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 6
tags: [view]
---

# v_daily_overview

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 6 |

## Lê de
[[telegram_groups_metadata]], [[telegram_team_members]]

## Lida por
—

## Definição SQL

```sql
select `b`.`message_sent_at_date` AS `date`,count(0) AS `total_msgs`,sum((case when (`t`.`user_id` is not null) then 1 else 0 end)) AS `team_msgs`,sum((case when (`t`.`user_id` is null) then 1 else 0 end)) AS `affiliate_msgs`,count(distinct `b`.`chat_id`) AS `active_groups`,count(distinct (case when (`t`.`user_id` is not null) then `b`.`user_id` else NULL end)) AS `active_agents` from ((`instituto_experience`.`telegram_groups_backup` `b` join `instituto_experience`.`telegram_groups_metadata` `m` on((`b`.`chat_id` = `m`.`chat_id`))) left join `instituto_experience`.`telegram_team_members` `t` on(((`b`.`user_id` = `t`.`user_id`) and (`t`.`is_active` = 1)))) group by `b`.`message_sent_at_date`
```
