---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-11 19:57:22"
alterada_em: "2026-05-11 19:57:22"
execucoes: 181
tags: [rotina, procedure]
---

# refresh_dashboard_lead_events

## Dependências

- **Lê:** [[orders]]
- **Escreve:** [[dashboard_lead_events_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_lead_events_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 181 |
| Tempo médio | 2m18s |
| Tempo máx | 5m52s |
| Tempo total | 6h54m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 865,909 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_lead_events_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_lead_events_stage;

    -- 2. Insere na stage (produção continua intacta)
    INSERT INTO instituto_experience.dashboard_lead_events_stage
    WITH ds_pivot AS (
        SELECT
            lead_event_id,
            MAX(CASE WHEN canal = 'SMS'                                        THEN status        END) AS status_sms,
            MAX(CASE WHEN canal = 'ACTIVECAMPAIGN'                             THEN status        END) AS status_active_campaign,
            MAX(CASE WHEN canal = 'CALLCENTER' AND extra_status = 'SALESBOUND' THEN status        END) AS status_salesbound,
            MAX(CASE WHEN canal = 'CALLCENTER' AND extra_status = 'LOGICALL'   THEN status        END) AS status_logicall,
            MAX(CASE WHEN canal = 'SMS'                                        THEN data_insercao END) AS data_insercao_slicktext,
            MAX(CASE WHEN canal = 'ACTIVECAMPAIGN'                             THEN data_insercao END) AS data_insercao_activecampaign,
            MAX(CASE WHEN canal = 'CALLCENTER' AND extra_status = 'LOGICALL'   THEN data_insercao END) AS data_insercao_logicall,
            MAX(CASE WHEN canal = 'CALLCENTER' AND extra_status = 'SALESBOUND' THEN data_insercao END) AS data_insercao_salesbound,
            MAX(CASE WHEN canal = 'WHATSAPP'                                   THEN data_insercao END) AS data_insercao_reportana,
            MAX(CASE WHEN canal = 'ACTIVECAMPAIGN' AND status = 'VALIDATED'    THEN data_insercao END) AS data_insercao_active_validated
        FROM leads_pipeline.distribution_status
        GROUP BY lead_event_id
    )

    SELECT
        le.order_date,
        REGEXP_REPLACE(
            TRIM(
                CASE
                    WHEN o.product LIKE '%-%'
                        THEN TRIM(SUBSTRING_INDEX(o.product, '-', 1))
                    WHEN REGEXP_LIKE(o.product, '[0-9]')
                        THEN TRIM(REGEXP_REPLACE(o.product, '^[0-9\s]+', ''))
                    ELSE o.product
                END
            ),
            '[^a-zA-Z0-9]', ''
        ) AS product_name,
        le.event_type,
        COUNT(DISTINCT l.email)                                                                  AS total_leads,
        COUNT(DISTINCT CASE WHEN le.event_type = 'lost_cart'         THEN l.email END)          AS leads_lost_cart,
        COUNT(DISTINCT CASE WHEN le.event_type = 'lost_cart_fast'    THEN l.email END)          AS leads_lost_cart_fast,
        COUNT(DISTINCT CASE WHEN le.event_type = 'purchase_approved' THEN l.email END)          AS leads_purchase_approved,
        COUNT(DISTINCT CASE WHEN ds.status_sms = 'WAITING'           THEN l.email END)          AS sms_waiting,
        COUNT(DISTINCT CASE WHEN ds.status_sms = 'PENDING'           THEN l.email END)          AS sms_pending,
        COUNT(DISTINCT CASE WHEN ds.status_sms = 'TAGGED'            THEN l.email END)          AS sms_tagged,
        COUNT(DISTINCT CASE WHEN ds.status_sms = 'ERROR'             THEN l.email END)          AS sms_error,
        COUNT(DISTINCT CASE WHEN ds.status_sms = 'PARTIAL_ERROR'     THEN l.email END)          AS sms_partial_error,
        COUNT(DISTINCT CASE WHEN ds.status_active_campaign = 'WAITING'   THEN l.email END)      AS email_waiting,
        COUNT(DISTINCT CASE WHEN ds.status_active_campaign = 'PENDING'   THEN l.email END)      AS email_pending,
        COUNT(DISTINCT CASE WHEN ds.status_active_campaign = 'SENT'      THEN l.email END)      AS email_sent,
        COUNT(DISTINCT CASE WHEN ds.status_active_campaign = 'TAGGED'    THEN l.email END)      AS email_tagged,
        COUNT(DISTINCT CASE WHEN ds.status_active_campaign = 'ERROR'     THEN l.email END)      AS email_error,
        COUNT(DISTINCT CASE WHEN ds.status_active_campaign = 'VALIDATED' THEN l.email END)      AS email_validated,
        COUNT(DISTINCT CASE WHEN ds.status_salesbound = 'WAITING' THEN l.email END)             AS salesbound_waiting,
        COUNT(DISTINCT CASE WHEN ds.status_salesbound = 'PENDING' THEN l.email END)             AS salesbound_pending,
        COUNT(DISTINCT CASE WHEN ds.status_salesbound = 'SENT'    THEN l.email END)             AS salesbound_sent,
        COUNT(DISTINCT CASE WHEN ds.status_salesbound = 'ERROR'   THEN l.email END)             AS salesbound_error,
        COUNT(DISTINCT CASE WHEN ds.status_logicall = 'WAITING' THEN l.email END)               AS logicall_waiting,
        COUNT(DISTINCT CASE WHEN ds.status_logicall = 'PENDING' THEN l.email END)               AS logicall_pending,
        COUNT(DISTINCT CASE WHEN ds.status_logicall = 'SENT'    THEN l.email END)               AS logicall_sent,
        COUNT(DISTINCT CASE WHEN ds.status_logicall = 'ERROR'   THEN l.email END)               AS logicall_error,
        COUNT(DISTINCT CASE WHEN ds.data_insercao_slicktext        IS NOT NULL THEN l.email END) AS leads_com_data_sms,
        COUNT(DISTINCT CASE WHEN ds.data_insercao_activecampaign   IS NOT NULL THEN l.email END) AS leads_com_data_email,
        COUNT(DISTINCT CASE WHEN ds.data_insercao_logicall         IS NOT NULL THEN l.email END) AS leads_com_data_logicall,
        COUNT(DISTINCT CASE WHEN ds.data_insercao_salesbound       IS NOT NULL THEN l.email END) AS leads_com_data_salesbound,
        COUNT(DISTINCT CASE WHEN ds.data_insercao_reportana        IS NOT NULL THEN l.email END) AS leads_com_data_whatsapp,
        COUNT(DISTINCT CASE WHEN ds.data_insercao_active_validated IS NOT NULL THEN l.email END) AS leads_com_data_email_validated

    FROM leads_pipeline.lead_events le
    JOIN leads_pipeline.leads  l  ON le.lead_id  = l.id
    JOIN leads_pipeline.orders o  ON le.order_id = o.id
    LEFT JOIN ds_pivot         ds ON le.id        = ds.lead_event_id

    WHERE le.order_date >= '2026-01-01'
      AND le.event_type IN ('lost_cart', 'lost_cart_fast', 'purchase_approved', 'cross_sell')

    GROUP BY
        le.order_date,
        REGEXP_REPLACE(
            TRIM(
                CASE
                    WHEN o.product LIKE '%-%'
                        THEN TRIM(SUBSTRING_INDEX(o.product, '-', 1))
                    WHEN REGEXP_LIKE(o.product, '[0-9]')
                        THEN TRIM(REGEXP_REPLACE(o.product, '^[0-9\s]+', ''))
                    ELSE o.product
                END
            ),
            '[^a-zA-Z0-9]', ''
        ),
        le.event_type

    ORDER BY
        le.order_date DESC,
        product_name;

    -- 3. Troca atômica
    RENAME TABLE
        instituto_experience.dashboard_lead_events       TO instituto_experience.dashboard_lead_events_old,
        instituto_experience.dashboard_lead_events_stage TO instituto_experience.dashboard_lead_events,
        instituto_experience.dashboard_lead_events_old   TO instituto_experience.dashboard_lead_events_stage;

END
```
