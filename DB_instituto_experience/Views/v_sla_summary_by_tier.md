---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 14
tags: [view]
---

# v_sla_summary_by_tier

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 14 |

## Lê de
[[v_sla_calculations]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`sla`.`tier` AS `tier`,count(0) AS `total_conversations`,sum(`instituto_experience`.`sla`.`was_answered`) AS `answered`,sum((case when (`instituto_experience`.`sla`.`was_answered` = 0) then 1 else 0 end)) AS `unanswered`,round(avg((case when (`instituto_experience`.`sla`.`was_answered` = 1) then `instituto_experience`.`sla`.`response_minutes` end)),0) AS `avg_response_min`,round(avg((case when (`instituto_experience`.`sla`.`was_answered` = 1) then `instituto_experience`.`sla`.`response_minutes` end)),0) AS `median_approx`,round(((sum((case when ((`instituto_experience`.`sla`.`was_answered` = 1) and (`instituto_experience`.`sla`.`response_minutes` <= (case when (`instituto_experience`.`sla`.`tier` = 'Tier 1') then 60 when (`instituto_experience`.`sla`.`tier` = 'Tier 2') then 120 else 180 end))) then 1 else 0 end)) / greatest(sum(`instituto_experience`.`sla`.`was_answered`),1)) * 100),1) AS `sla_compliance_pct`,sum((case when ((`instituto_experience`.`sla`.`was_answered` = 1) and (`instituto_experience`.`sla`.`response_minutes` <= 5)) then 1 else 0 end)) AS `bucket_0_5`,sum((case when ((`instituto_experience`.`sla`.`was_answered` = 1) and (`instituto_experience`.`sla`.`response_minutes` between 6 and 15)) then 1 else 0 end)) AS `bucket_6_15`,sum((case when ((`instituto_experience`.`sla`.`was_answered` = 1) and (`instituto_experience`.`sla`.`response_minutes` between 16 and 30)) then 1 else 0 end)) AS `bucket_16_30`,sum((case when ((`instituto_experience`.`sla`.`was_answered` = 1) and (`instituto_experience`.`sla`.`response_minutes` between 31 and 60)) then 1 else 0 end)) AS `bucket_31_60`,sum((case when ((`instituto_experience`.`sla`.`was_answered` = 1) and (`instituto_experience`.`sla`.`response_minutes` between 61 and 120)) then 1 else 0 end)) AS `bucket_61_120`,sum((case when ((`instituto_experience`.`sla`.`was_answered` = 1) and (`instituto_experience`.`sla`.`response_minutes` > 120)) then 1 else 0 end)) AS `bucket_120_plus`,sum(`instituto_experience`.`sla`.`responded_outside_window`) AS `outside_window_responses` from `instituto_experience`.`v_sla_calculations` `sla` group by `instituto_experience`.`sla`.`tier`
```
