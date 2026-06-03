---
tipo: view
definer: "diego@%"
security_type: "DEFINER"
colunas: 3
tags: [view]
---

# vw_phone_lookup

## Propriedades

| Propriedade | Valor |
|---|---|
| Definer | diego@% |
| Atualizável | NO |
| Security type | DEFINER |
| Colunas | 3 |

## Lê de
[[unified_lead_events_new]], [[unified_lead_events_new_backup_1]]

## Lida por
[[sp_phone_lookup]]

## Definição SQL

```sql
select `instituto_experience`.`unified_lead_events_new`.`client_email` AS `email`,`instituto_experience`.`unified_lead_events_new`.`client_phone` AS `phone`,trim(concat(coalesce(`instituto_experience`.`unified_lead_events_new`.`client_first_name`,''),' ',coalesce(`instituto_experience`.`unified_lead_events_new`.`client_last_name`,''))) AS `full_name` from `instituto_experience`.`unified_lead_events_new` where ((trim(coalesce(`instituto_experience`.`unified_lead_events_new`.`client_phone`,'')) <> '') and (trim(coalesce(`instituto_experience`.`unified_lead_events_new`.`client_email`,'')) <> '')) union all select `instituto_experience`.`unified_lead_events_new_backup_1`.`client_email` AS `client_email`,`instituto_experience`.`unified_lead_events_new_backup_1`.`client_phone` AS `client_phone`,trim(concat(coalesce(`instituto_experience`.`unified_lead_events_new_backup_1`.`client_first_name`,''),' ',coalesce(`instituto_experience`.`unified_lead_events_new_backup_1`.`client_last_name`,''))) AS `Name_exp_6` from `instituto_experience`.`unified_lead_events_new_backup_1` where ((trim(coalesce(`instituto_experience`.`unified_lead_events_new_backup_1`.`client_phone`,'')) <> '') and (trim(coalesce(`instituto_experience`.`unified_lead_events_new_backup_1`.`client_email`,'')) <> ''))
```
