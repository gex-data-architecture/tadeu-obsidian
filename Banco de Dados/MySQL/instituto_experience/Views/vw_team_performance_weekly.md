---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 20
tags: [view]
---

# vw_team_performance_weekly

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 20 |

## Lê de
[[mat_team_performance_daily]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`mat_team_performance_daily`.`user_id` AS `user_id`,`instituto_experience`.`mat_team_performance_daily`.`agent_name` AS `agent_name`,`instituto_experience`.`mat_team_performance_daily`.`role` AS `role`,year(`instituto_experience`.`mat_team_performance_daily`.`report_date`) AS `report_year`,`instituto_experience`.`mat_team_performance_daily`.`report_week` AS `report_week`,min(`instituto_experience`.`mat_team_performance_daily`.`report_date`) AS `week_start`,max(`instituto_experience`.`mat_team_performance_daily`.`report_date`) AS `week_end`,count(`instituto_experience`.`mat_team_performance_daily`.`report_date`) AS `days_active`,sum(`instituto_experience`.`mat_team_performance_daily`.`total_msgs`) AS `total_msgs`,sum(`instituto_experience`.`mat_team_performance_daily`.`groups_served`) AS `groups_served`,sum(`instituto_experience`.`mat_team_performance_daily`.`total_responses`) AS `total_responses`,round(avg(`instituto_experience`.`mat_team_performance_daily`.`avg_response_min`),0) AS `avg_response_min`,min(`instituto_experience`.`mat_team_performance_daily`.`min_response_min`) AS `best_response_min`,max(`instituto_experience`.`mat_team_performance_daily`.`max_response_min`) AS `worst_response_min`,sum(`instituto_experience`.`mat_team_performance_daily`.`sla_met_count`) AS `sla_met_count`,sum(`instituto_experience`.`mat_team_performance_daily`.`sla_missed_count`) AS `sla_missed_count`,round(((sum(`instituto_experience`.`mat_team_performance_daily`.`sla_met_count`) * 100.0) / nullif((sum(`instituto_experience`.`mat_team_performance_daily`.`sla_met_count`) + sum(`instituto_experience`.`mat_team_performance_daily`.`sla_missed_count`)),0)),1) AS `sla_compliance_pct`,sum(`instituto_experience`.`mat_team_performance_daily`.`times_mentioned`) AS `times_mentioned`,min(`instituto_experience`.`mat_team_performance_daily`.`first_msg_time`) AS `earliest_start`,max(`instituto_experience`.`mat_team_performance_daily`.`last_msg_time`) AS `latest_end` from `instituto_experience`.`mat_team_performance_daily` group by `instituto_experience`.`mat_team_performance_daily`.`user_id`,`instituto_experience`.`mat_team_performance_daily`.`agent_name`,`instituto_experience`.`mat_team_performance_daily`.`role`,year(`instituto_experience`.`mat_team_performance_daily`.`report_date`),`instituto_experience`.`mat_team_performance_daily`.`report_week`
```
