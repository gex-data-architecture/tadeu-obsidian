---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 14
tags: [view]
---

# vw_weekly_trend_by_tier

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 14 |

## Lê de
[[mat_daily_overview_by_tier]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`mat_daily_overview_by_tier`.`tier` AS `tier`,year(`instituto_experience`.`mat_daily_overview_by_tier`.`report_date`) AS `report_year`,week(`instituto_experience`.`mat_daily_overview_by_tier`.`report_date`,1) AS `report_week`,min(`instituto_experience`.`mat_daily_overview_by_tier`.`report_date`) AS `week_start`,sum(`instituto_experience`.`mat_daily_overview_by_tier`.`total_msgs`) AS `total_msgs`,sum(`instituto_experience`.`mat_daily_overview_by_tier`.`team_msgs`) AS `team_msgs`,sum(`instituto_experience`.`mat_daily_overview_by_tier`.`affiliate_msgs`) AS `affiliate_msgs`,round(avg(`instituto_experience`.`mat_daily_overview_by_tier`.`active_groups`),0) AS `avg_active_groups`,sum(`instituto_experience`.`mat_daily_overview_by_tier`.`total_conversations`) AS `total_conversations`,sum(`instituto_experience`.`mat_daily_overview_by_tier`.`answered`) AS `answered`,sum(`instituto_experience`.`mat_daily_overview_by_tier`.`unanswered`) AS `unanswered`,round(avg(`instituto_experience`.`mat_daily_overview_by_tier`.`avg_response_min`),0) AS `avg_response_min`,round(((sum(`instituto_experience`.`mat_daily_overview_by_tier`.`answered`) * 100.0) / nullif(sum(`instituto_experience`.`mat_daily_overview_by_tier`.`total_conversations`),0)),1) AS `answer_rate_pct`,round(((((sum(`instituto_experience`.`mat_daily_overview_by_tier`.`bucket_0_5`) + sum(`instituto_experience`.`mat_daily_overview_by_tier`.`bucket_6_15`)) + sum(`instituto_experience`.`mat_daily_overview_by_tier`.`bucket_16_30`)) * 100.0) / nullif(sum(`instituto_experience`.`mat_daily_overview_by_tier`.`answered`),0)),1) AS `pct_under_30min` from `instituto_experience`.`mat_daily_overview_by_tier` group by `instituto_experience`.`mat_daily_overview_by_tier`.`tier`,year(`instituto_experience`.`mat_daily_overview_by_tier`.`report_date`),week(`instituto_experience`.`mat_daily_overview_by_tier`.`report_date`,1)
```
