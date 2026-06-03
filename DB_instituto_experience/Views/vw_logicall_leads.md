---
tipo: view
definer: "diego@%"
security_type: "DEFINER"
colunas: 3
tags: [view]
---

# vw_logicall_leads

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | diego@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 3 |

## Lê de
[[unified_lead_events_new]]

## Lida por
[[vw_logicall_rpl]]

## Definição SQL

```sql
select `instituto_experience`.`unified_lead_events_new`.`order_date` AS `data`,`instituto_experience`.`unified_lead_events_new`.`product_name` AS `nome_produto`,count(distinct concat(`instituto_experience`.`unified_lead_events_new`.`client_email`,'-',`instituto_experience`.`unified_lead_events_new`.`product_name`)) AS `leads_logicall` from `instituto_experience`.`unified_lead_events_new` where ((`instituto_experience`.`unified_lead_events_new`.`event_type` = 'lost_cart') and (`instituto_experience`.`unified_lead_events_new`.`status_call_center` = 'SENT') and (`instituto_experience`.`unified_lead_events_new`.`call_center_target` = 'logicall') and (`instituto_experience`.`unified_lead_events_new`.`log_call_center` like '%"success":true%')) group by `instituto_experience`.`unified_lead_events_new`.`order_date`,`instituto_experience`.`unified_lead_events_new`.`product_name`
```
