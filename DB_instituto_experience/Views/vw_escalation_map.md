---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 9
tags: [view]
---

# vw_escalation_map

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 9 |

## Lê de
[[mat_messages_enriched]]

## Lida por
—

## Definição SQL

```sql
select `mt`.`tier` AS `tier`,`mt`.`chat_id` AS `chat_id`,`me`.`group_name` AS `group_name`,`mt`.`sender_name` AS `afiliado`,`mt`.`mentioned_username` AS `agente_acionado`,`mt`.`mentioned_role` AS `cargo_agente`,`mt`.`message_sent_at_date` AS `message_sent_at_date`,count(0) AS `vezes_acionado`,group_concat(left(`me`.`message`,80) order by `me`.`created_at` DESC separator ' | ') AS `ultimas_msgs` from (`instituto_experience`.`mat_mention_tracking` `mt` left join `instituto_experience`.`mat_messages_enriched` `me` on((`mt`.`event_id` = `me`.`event_id`))) where (`mt`.`sender_type` = 'affiliate') group by `mt`.`tier`,`mt`.`chat_id`,`me`.`group_name`,`mt`.`sender_name`,`mt`.`mentioned_username`,`mt`.`mentioned_role`,`mt`.`message_sent_at_date`
```
