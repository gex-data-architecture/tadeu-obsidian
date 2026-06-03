---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 0
tags: [view]
---

# v_team_performance

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 0 |

## Lê de
[[telegram_groups_metadata]], [[telegram_team_members]], [[v_sla_calculations]]

## Lida por
—

## Definição SQL

```sql
with `agent_msgs` as (select `t`.`user_id` AS `user_id`,`t`.`first_name` AS `agent_name`,`t`.`role` AS `role`,`b`.`chat_id` AS `chat_id`,`b`.`message_sent_at_date` AS `message_sent_at_date`,`b`.`message_sent_at_hour` AS `message_sent_at_hour`,hour(`b`.`message_sent_at_hour`) AS `hour_of_day` from ((`instituto_experience`.`telegram_groups_backup` `b` join `instituto_experience`.`telegram_team_members` `t` on(((`b`.`user_id` = `t`.`user_id`) and (`t`.`is_active` = 1)))) join `instituto_experience`.`telegram_groups_metadata` `m` on((`b`.`chat_id` = `m`.`chat_id`)))), `agent_base` as (select `agent_msgs`.`user_id` AS `user_id`,`agent_msgs`.`agent_name` AS `agent_name`,`agent_msgs`.`role` AS `role`,count(0) AS `total_msgs`,count(distinct `agent_msgs`.`chat_id`) AS `groups_served`,count(distinct `agent_msgs`.`message_sent_at_date`) AS `active_days`,min(`agent_msgs`.`message_sent_at_date`) AS `first_active_date`,max(`agent_msgs`.`message_sent_at_date`) AS `last_active_date` from `agent_msgs` group by `agent_msgs`.`user_id`,`agent_msgs`.`agent_name`,`agent_msgs`.`role`), `team_avg` as (select avg(`agent_base`.`total_msgs`) AS `avg_msgs` from `agent_base`), `agent_response` as (select `instituto_experience`.`sla`.`responder_user_id` AS `user_id`,round(avg(`instituto_experience`.`sla`.`response_minutes`),0) AS `avg_response_min`,count(0) AS `total_responses`,sum((case when (`instituto_experience`.`sla`.`response_minutes` <= (case when (`instituto_experience`.`sla`.`tier` = 'Tier 1') then 60 when (`instituto_experience`.`sla`.`tier` = 'Tier 2') then 120 else 180 end)) then 1 else 0 end)) AS `responses_within_sla` from `instituto_experience`.`v_sla_calculations` `sla` where ((`instituto_experience`.`sla`.`responder_user_id` is not null) and (`instituto_experience`.`sla`.`response_minutes` is not null)) group by `instituto_experience`.`sla`.`responder_user_id`),  select `ab`.`user_id` AS `user_id`,`ab`.`agent_name` AS `agent_name`,`ab`.`role` AS `role`,`ab`.`total_msgs` AS `total_msgs`,`ab`.`groups_served` AS `groups_served`,`ab`.`active_days` AS `active_days`,`ab`.`first_active_date` AS `first_active_date`,`ab`.`last_active_date` AS `last_active_date`,round((`ab`.`total_msgs` / `ta`.`avg_msgs`),2) AS `load_ratio`,(case when ((`ab`.`total_msgs` / `ta`.`avg_msgs`) > 1.4) then 'Sobrecarregado' when ((`ab`.`total_msgs` / `ta`.`avg_msgs`) > 1.1) then 'Acima' when ((`ab`.`total_msgs` / `ta`.`avg_msgs`) < 0.6) then 'Abaixo' else 'Normal' end) AS `load_status`,coalesce(`ar`.`avg_response_min`,0) AS `avg_response_min`,coalesce(`ar`.`total_responses`,0) AS `total_responses`,(case when (coalesce(`ar`.`total_responses`,0) > 0) then round(((`ar`.`responses_within_sla` / `ar`.`total_responses`) * 100),1) else 0 end) AS `sla_compliance_pct`,round(`ta`.`avg_msgs`,0) AS `team_avg_msgs` from ((`agent_base` `ab` join `team_avg` `ta`) left join `agent_response` `ar` on((`ab`.`user_id` = `ar`.`user_id`)))
```
