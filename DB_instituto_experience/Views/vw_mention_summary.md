---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 9
tags: [view]
---

# vw_mention_summary

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 9 |

## Lê de
[[mat_mention_tracking]]

## Lida por
—

## Definição SQL

```sql
select `mt`.`mentioned_username` AS `mentioned_username`,`mt`.`mentioned_user_id` AS `mentioned_user_id`,`mt`.`mentioned_role` AS `mentioned_role`,`mt`.`message_sent_at_date` AS `message_sent_at_date`,count(0) AS `total_mentions`,sum((case when (`mt`.`sender_type` = 'affiliate') then 1 else 0 end)) AS `mentions_by_affiliates`,sum((case when (`mt`.`sender_type` = 'team') then 1 else 0 end)) AS `mentions_by_team`,count(distinct `mt`.`chat_id`) AS `grupos_distintos`,count(distinct `mt`.`sender_user_id`) AS `pessoas_distintas` from `instituto_experience`.`mat_mention_tracking` `mt` group by `mt`.`mentioned_username`,`mt`.`mentioned_user_id`,`mt`.`mentioned_role`,`mt`.`message_sent_at_date`
```
