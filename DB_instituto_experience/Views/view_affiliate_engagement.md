---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 13
tags: [view]
---

# view_affiliate_engagement

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 13 |

## Lê de
[[telegram_groups_metadata]], [[telegram_team_members]]

## Lida por
—

## Definição SQL

```sql
select `m`.`chat_id` AS `chat_id`,`m`.`group_name` AS `group_name`,`gm`.`tier` AS `tier`,`gm`.`partners` AS `partners`,count(0) AS `total_messages`,sum((case when (`t`.`user_id` is not null) then 1 else 0 end)) AS `team_messages`,sum((case when (`t`.`user_id` is null) then 1 else 0 end)) AS `affiliate_messages`,count(distinct `m`.`message_sent_at_date`) AS `active_days`,min(`m`.`message_sent_at_date`) AS `first_msg_date`,max(`m`.`message_sent_at_date`) AS `last_msg_date`,(to_days(curdate()) - to_days(max(`m`.`message_sent_at_date`))) AS `days_since_last_msg`,(cast((case when ((to_days(curdate()) - to_days(max(`m`.`message_sent_at_date`))) <= 3) then 'Saudavel' when ((to_days(curdate()) - to_days(max(`m`.`message_sent_at_date`))) <= 7) then 'Atencao' when ((to_days(curdate()) - to_days(max(`m`.`message_sent_at_date`))) <= 14) then 'Risco' when ((to_days(curdate()) - to_days(max(`m`.`message_sent_at_date`))) <= 30) then 'Critico' else 'Churn' end) as char charset utf8mb4) collate utf8mb4_0900_ai_ci) AS `churn_risk`,round(((sum((case when (`t`.`user_id` is null) then 1 else 0 end)) / count(0)) * 100),1) AS `engagement_pct` from ((`instituto_experience`.`telegram_groups_backup` `m` left join `instituto_experience`.`telegram_groups_metadata` `gm` on((`m`.`chat_id` = `gm`.`chat_id`))) left join `instituto_experience`.`telegram_team_members` `t` on((`m`.`user_id` = `t`.`user_id`))) group by `m`.`chat_id`,`m`.`group_name`,`gm`.`tier`,`gm`.`partners`
```
