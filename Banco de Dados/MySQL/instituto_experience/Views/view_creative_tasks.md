---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 25
tags: [view]
---

# view_creative_tasks

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 25 |

## Lê de
[[creative_tasks]]

## Lida por
—

## Definição SQL

```sql
select `instituto_experience`.`creative_tasks`.`task_id` AS `task_id`,`instituto_experience`.`creative_tasks`.`unique_id` AS `unique_id`,`instituto_experience`.`creative_tasks`.`creative_name` AS `creative_name`,`instituto_experience`.`creative_tasks`.`creative_link` AS `creative_link`,`instituto_experience`.`creative_tasks`.`creative_status` AS `creative_status`,`instituto_experience`.`creative_tasks`.`task_relationship` AS `task_relationship`,`instituto_experience`.`creative_tasks`.`body_number` AS `body_number`,`instituto_experience`.`creative_tasks`.`clickbait_number` AS `clickbait_number`,`instituto_experience`.`creative_tasks`.`video_variation_number` AS `video_variation_number`,`instituto_experience`.`creative_tasks`.`created_at_date` AS `created_at_date`,`instituto_experience`.`creative_tasks`.`traffic_source` AS `traffic_source`,`instituto_experience`.`creative_tasks`.`creative_format` AS `creative_format`,`instituto_experience`.`creative_tasks`.`total_price` AS `total_price`,`instituto_experience`.`creative_tasks`.`commission` AS `commission`,`instituto_experience`.`creative_tasks`.`amount_spent` AS `amount_spent`,`instituto_experience`.`creative_tasks`.`impressions` AS `impressions`,`instituto_experience`.`creative_tasks`.`link_clicks` AS `link_clicks`,`instituto_experience`.`creative_tasks`.`sales` AS `sales`,`instituto_experience`.`creative_tasks`.`margem` AS `margem`,`instituto_experience`.`creative_tasks`.`copywriter_owner` AS `copywriter_owner`,`instituto_experience`.`creative_tasks`.`designer_owner` AS `designer_owner`,`instituto_experience`.`creative_tasks`.`supervisor_owner` AS `supervisor_owner`,`instituto_experience`.`creative_tasks`.`funnel_id` AS `funnel_id`,`instituto_experience`.`creative_tasks`.`assertividade_geral` AS `assertividade_geral`,`instituto_experience`.`creative_tasks`.`assertividade_detalhada` AS `assertividade_detalhada` from `instituto_experience`.`creative_tasks`
```
