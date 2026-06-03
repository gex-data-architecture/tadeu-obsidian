---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 19
tags: [view]
---

# vw_fca_week_comparison

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 19 |

## Lê de
[[mat_team_performance_daily]]

## Lida por
—

## Definição SQL

```sql
select `cw`.`user_id` AS `user_id`,`cw`.`agent_name` AS `agent_name`,`cw`.`role` AS `role`,`cw`.`msgs` AS `msgs_atual`,`cw`.`groups_served` AS `grupos_atual`,`cw`.`responses` AS `respostas_atual`,`cw`.`avg_resp_min` AS `tempo_medio_atual`,`cw`.`sla_pct` AS `sla_pct_atual`,`cw`.`mentions` AS `mentions_atual`,coalesce(`pw`.`msgs`,0) AS `msgs_anterior`,coalesce(`pw`.`groups_served`,0) AS `grupos_anterior`,coalesce(`pw`.`responses`,0) AS `respostas_anterior`,`pw`.`avg_resp_min` AS `tempo_medio_anterior`,`pw`.`sla_pct` AS `sla_pct_anterior`,coalesce(`pw`.`mentions`,0) AS `mentions_anterior`,(`cw`.`msgs` - coalesce(`pw`.`msgs`,0)) AS `delta_msgs`,round((((`cw`.`msgs` - coalesce(`pw`.`msgs`,0)) * 100.0) / nullif(`pw`.`msgs`,0)),1) AS `delta_msgs_pct`,(`cw`.`sla_pct` - coalesce(`pw`.`sla_pct`,0)) AS `delta_sla_pp`,(coalesce(`pw`.`avg_resp_min`,0) - coalesce(`cw`.`avg_resp_min`,0)) AS `delta_tempo_min` from ((select `instituto_experience`.`mat_team_performance_daily`.`user_id` AS `user_id`,`instituto_experience`.`mat_team_performance_daily`.`agent_name` AS `agent_name`,`instituto_experience`.`mat_team_performance_daily`.`role` AS `role`,sum(`instituto_experience`.`mat_team_performance_daily`.`total_msgs`) AS `msgs`,sum(`instituto_experience`.`mat_team_performance_daily`.`groups_served`) AS `groups_served`,sum(`instituto_experience`.`mat_team_performance_daily`.`total_responses`) AS `responses`,round(avg(`instituto_experience`.`mat_team_performance_daily`.`avg_response_min`),0) AS `avg_resp_min`,round(((sum(`instituto_experience`.`mat_team_performance_daily`.`sla_met_count`) * 100.0) / nullif((sum(`instituto_experience`.`mat_team_performance_daily`.`sla_met_count`) + sum(`instituto_experience`.`mat_team_performance_daily`.`sla_missed_count`)),0)),1) AS `sla_pct`,sum(`instituto_experience`.`mat_team_performance_daily`.`times_mentioned`) AS `mentions` from `instituto_experience`.`mat_team_performance_daily` where (`instituto_experience`.`mat_team_performance_daily`.`report_date` >= (curdate() - interval weekday(curdate()) day)) group by `instituto_experience`.`mat_team_performance_daily`.`user_id`,`instituto_experience`.`mat_team_performance_daily`.`agent_name`,`instituto_experience`.`mat_team_performance_daily`.`role`) `cw` left join (select `instituto_experience`.`mat_team_performance_daily`.`user_id` AS `user_id`,sum(`instituto_experience`.`mat_team_performance_daily`.`total_msgs`) AS `msgs`,sum(`instituto_experience`.`mat_team_performance_daily`.`groups_served`) AS `groups_served`,sum(`instituto_experience`.`mat_team_performance_daily`.`total_responses`) AS `responses`,round(avg(`instituto_experience`.`mat_team_performance_daily`.`avg_response_min`),0) AS `avg_resp_min`,round(((sum(`instituto_experience`.`mat_team_performance_daily`.`sla_met_count`) * 100.0) / nullif((sum(`instituto_experience`.`mat_team_performance_daily`.`sla_met_count`) + sum(`instituto_experience`.`mat_team_performance_daily`.`sla_missed_count`)),0)),1) AS `sla_pct`,sum(`instituto_experience`.`mat_team_performance_daily`.`times_mentioned`) AS `mentions` from `instituto_experience`.`mat_team_performance_daily` where ((`instituto_experience`.`mat_team_performance_daily`.`report_date` >= (curdate() - interval (weekday(curdate()) + 7) day)) and (`instituto_experience`.`mat_team_performance_daily`.`report_date` < (curdate() - interval weekday(curdate()) day))) group by `instituto_experience`.`mat_team_performance_daily`.`user_id`) `pw` on((`cw`.`user_id` = `pw`.`user_id`)))
```
