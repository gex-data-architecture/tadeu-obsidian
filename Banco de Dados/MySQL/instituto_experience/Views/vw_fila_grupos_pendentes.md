---
tipo: view
definer: "root@%"
security_type: "DEFINER"
colunas: 12
tags: [view]
---

# vw_fila_grupos_pendentes

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | root@% |
| Atualizável | YES |
| Security type | DEFINER |
| Colunas | 12 |

## Lê de
[[mat_messages_enriched]]

## Lida por
—

## Definição SQL

```sql
select `pending`.`chat_id` AS `chat_id`,`pending`.`group_name` AS `group_name`,`pending`.`tier` AS `tier`,`pending`.`partners` AS `partners`,`pending`.`sla_target_minutes` AS `sla_target_minutes`,`pending`.`last_affiliate_user_id` AS `last_affiliate_user_id`,`pending`.`last_affiliate_name` AS `last_affiliate_name`,`pending`.`last_affiliate_msg` AS `last_affiliate_msg`,`pending`.`last_affiliate_msg_at` AS `last_affiliate_msg_at`,timestampdiff(MINUTE,`pending`.`last_affiliate_msg_at`,now()) AS `minutos_aguardando`,(case when (timestampdiff(MINUTE,`pending`.`last_affiliate_msg_at`,now()) > coalesce(`pending`.`sla_target_minutes`,30)) then 'SLA estourado' when (timestampdiff(MINUTE,`pending`.`last_affiliate_msg_at`,now()) > (coalesce(`pending`.`sla_target_minutes`,30) * 0.8)) then 'Quase estourando' else 'Dentro do SLA' end) AS `urgencia`,`pending`.`msgs_seguidas_afiliado` AS `msgs_seguidas_afiliado` from (select `last_msg`.`chat_id` AS `chat_id`,`last_msg`.`group_name` AS `group_name`,`last_msg`.`tier` AS `tier`,`last_msg`.`partners` AS `partners`,`last_msg`.`sla_target_minutes` AS `sla_target_minutes`,`last_msg`.`user_id` AS `last_affiliate_user_id`,`last_msg`.`first_name` AS `last_affiliate_name`,left(`last_msg`.`message`,120) AS `last_affiliate_msg`,`last_msg`.`created_at` AS `last_affiliate_msg_at`,(select count(0) from `instituto_experience`.`mat_messages_enriched` `seq` where ((`seq`.`chat_id` = `last_msg`.`chat_id`) and (`seq`.`created_at` >= (select coalesce(max(`t2`.`created_at`),'1970-01-01') from `instituto_experience`.`mat_messages_enriched` `t2` where ((`t2`.`chat_id` = `last_msg`.`chat_id`) and (`t2`.`sender_type` = 'team')))) and (`seq`.`sender_type` = 'affiliate'))) AS `msgs_seguidas_afiliado` from (`instituto_experience`.`mat_messages_enriched` `last_msg` join (select `instituto_experience`.`mat_messages_enriched`.`chat_id` AS `chat_id`,max(`instituto_experience`.`mat_messages_enriched`.`created_at`) AS `max_ts` from `instituto_experience`.`mat_messages_enriched` group by `instituto_experience`.`mat_messages_enriched`.`chat_id`) `latest` on(((`last_msg`.`chat_id` = `latest`.`chat_id`) and (`last_msg`.`created_at` = `latest`.`max_ts`)))) where (`last_msg`.`sender_type` = 'affiliate')) `pending` order by timestampdiff(MINUTE,`pending`.`last_affiliate_msg_at`,now()) desc
```
