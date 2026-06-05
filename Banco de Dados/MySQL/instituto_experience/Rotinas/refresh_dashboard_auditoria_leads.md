---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-11 19:57:22"
alterada_em: "2026-05-11 19:57:22"
execucoes: 183
tags: [rotina, procedure]
---

# refresh_dashboard_auditoria_leads

## Dependências

- **Lê:** [[dashboard_channels_marketing]], [[gross_recovery_target]], [[orders]]
- **Escreve:** [[dashboard_auditoria_leads_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_auditoria_leads_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 183 |
| Tempo médio | 3m59s |
| Tempo máx | 1h32m |
| Tempo total | 12h9m |
| Erros | 0 |
| Warnings | 176,416 |
| Linhas afetadas (total) | 410,907,278 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_auditoria_leads_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_auditoria_leads_stage;

    -- 2. Insere na stage
    INSERT INTO instituto_experience.dashboard_auditoria_leads_stage
    WITH

    ds_pivot AS (
        SELECT
            lead_event_id,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'SMS'                                                                   THEN status COLLATE utf8mb4_0900_ai_ci      END) AS status_sms,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'ACTIVECAMPAIGN'                                                        THEN status COLLATE utf8mb4_0900_ai_ci      END) AS status_active_campaign,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'WHATSAPP'                                                              THEN status COLLATE utf8mb4_0900_ai_ci      END) AS status_whatsapp_reportana,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'CALLCENTER' AND extra_status COLLATE utf8mb4_0900_ai_ci = 'SALESBOUND' THEN status COLLATE utf8mb4_0900_ai_ci      END) AS status_salesbound,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'CALLCENTER' AND extra_status COLLATE utf8mb4_0900_ai_ci = 'LOGICALL'   THEN status COLLATE utf8mb4_0900_ai_ci      END) AS status_logicall,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'SMS'                                                                   THEN data_insercao                          END) AS data_insercao_slicktext,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'ACTIVECAMPAIGN'                                                        THEN data_insercao                          END) AS data_insercao_activecampaign,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'WHATSAPP'                                                              THEN data_insercao                          END) AS data_insercao_reportana,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'CALLCENTER' AND extra_status COLLATE utf8mb4_0900_ai_ci = 'LOGICALL'   THEN data_insercao                          END) AS data_insercao_logicall,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'CALLCENTER' AND extra_status COLLATE utf8mb4_0900_ai_ci = 'SALESBOUND' THEN data_insercao                          END) AS data_insercao_salesbound,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'ACTIVECAMPAIGN' AND status COLLATE utf8mb4_0900_ai_ci = 'VALIDATED'    THEN data_insercao                          END) AS data_insercao_active_validated,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'SMS'            THEN channel_log COLLATE utf8mb4_0900_ai_ci            END) AS log_sms,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'ACTIVECAMPAIGN' THEN channel_log COLLATE utf8mb4_0900_ai_ci            END) AS log_active_campaign,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'WHATSAPP'       THEN channel_log COLLATE utf8mb4_0900_ai_ci            END) AS log_reportana
        FROM leads_pipeline.distribution_status
        GROUP BY lead_event_id
    ),

    base AS (

        /* ========================= SMS ========================= */
        SELECT DISTINCT
            'sms'                                                   AS canal,
            o.order_id    COLLATE utf8mb4_0900_ai_ci               AS order_id,
            le.event_type COLLATE utf8mb4_0900_ai_ci               AS event_type,
            o.platform    COLLATE utf8mb4_0900_ai_ci               AS platform,
            o.product     COLLATE utf8mb4_0900_ai_ci               AS product_name,
            o.order_date,
            DATE_FORMAT(o.order_date, '%Y-%m')                     AS mes_order,
            ds.status_sms                                          AS status_canal,
            ds.log_sms                                             AS log_canal,
            NULL                                                   AS call_center_target,
            COALESCE(
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
            ) AS order_datetime_calc,
            CASE
                WHEN ds.status_sms IN ('TAGGED','VALIDATED')
                    THEN ds.data_insercao_slicktext
                WHEN ds.status_sms = 'WAITING'
                    THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')
                ELSE NULL
            END AS data_insercao_calc,
            CASE
                WHEN ds.status_sms IN ('TAGGED','VALIDATED')
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_slicktext)
                WHEN ds.status_sms = 'WAITING'
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo'))
                ELSE NULL
            END AS tempo_segundos_calc,
            CASE
                WHEN ds.status_sms IN ('TAGGED','VALIDATED')
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_slicktext)
                ELSE NULL
            END AS tempo_segundos_tagged,
            NULL AS data_insercao_calc_validated,
            NULL AS tempo_segundos_calc_validated,
            NULL AS tempo_segundos_validated,
            CASE
                WHEN ds.status_sms NOT IN ('TAGGED','VALIDATED','WAITING') THEN 0
                WHEN le.event_type = 'lost_cart' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_sms = 'WAITING' THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_slicktext END
                ) > 660 THEN 1
                WHEN le.event_type IN ('purchase_approved', 'cross_sell') AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_sms = 'WAITING' THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_slicktext END
                ) > 60 THEN 1
                WHEN le.event_type = 'lost_cart_fast' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_sms = 'WAITING' THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_slicktext END
                ) > 60 THEN 1
                ELSE 0
            END AS alerta,
            0 AS alerta_validated
        FROM leads_pipeline.lead_events le
        INNER JOIN leads_pipeline.orders o  ON le.order_id = o.id
        INNER JOIN ds_pivot ds              ON ds.lead_event_id = le.id
        WHERE le.event_type COLLATE utf8mb4_0900_ai_ci IN ('lost_cart','lost_cart_fast','purchase_approved','cross_sell')
          AND o.order_date >= CURDATE() - INTERVAL 30 DAY

        UNION ALL

        /* ========================= EMAIL ========================= */
        SELECT DISTINCT
            'email'                                                 AS canal,
            o.order_id    COLLATE utf8mb4_0900_ai_ci               AS order_id,
            le.event_type COLLATE utf8mb4_0900_ai_ci               AS event_type,
            o.platform    COLLATE utf8mb4_0900_ai_ci               AS platform,
            o.product     COLLATE utf8mb4_0900_ai_ci               AS product_name,
            o.order_date,
            DATE_FORMAT(o.order_date, '%Y-%m')                     AS mes_order,
            ds.status_active_campaign                              AS status_canal,
            ds.log_active_campaign                                 AS log_canal,
            NULL                                                   AS call_center_target,
            COALESCE(
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
            ) AS order_datetime_calc,
            CASE
                WHEN ds.status_active_campaign IN ('TAGGED','VALIDATED')
                    THEN ds.data_insercao_activecampaign
                WHEN ds.status_active_campaign = 'WAITING'
                    THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')
                ELSE NULL
            END AS data_insercao_calc,
            CASE
                WHEN ds.status_active_campaign IN ('TAGGED','VALIDATED')
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_activecampaign)
                WHEN ds.status_active_campaign = 'WAITING'
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo'))
                ELSE NULL
            END AS tempo_segundos_calc,
            CASE
                WHEN ds.status_active_campaign IN ('TAGGED','VALIDATED')
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_activecampaign)
                ELSE NULL
            END AS tempo_segundos_tagged,
            CASE
                WHEN ds.status_active_campaign = 'VALIDATED'
                    THEN ds.data_insercao_active_validated
                WHEN ds.status_active_campaign IN ('TAGGED','WAITING')
                    THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')
                ELSE NULL
            END AS data_insercao_calc_validated,
            CASE
                WHEN ds.status_active_campaign = 'VALIDATED'
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_active_validated)
                WHEN ds.status_active_campaign IN ('TAGGED','WAITING')
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo'))
                ELSE NULL
            END AS tempo_segundos_calc_validated,
            CASE
                WHEN ds.status_active_campaign = 'VALIDATED'
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_active_validated)
                ELSE NULL
            END AS tempo_segundos_validated,
            CASE
                WHEN ds.status_active_campaign NOT IN ('TAGGED','VALIDATED','WAITING') THEN 0
                WHEN le.event_type = 'lost_cart' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_active_campaign = 'WAITING' THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_activecampaign END
                ) > 660 THEN 1
                WHEN le.event_type = 'purchase_approved' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_active_campaign = 'WAITING' THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_activecampaign END
                ) > 60 THEN 1
                WHEN le.event_type = 'lost_cart_fast' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_active_campaign = 'WAITING' THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_activecampaign END
                ) > 60 THEN 1
                ELSE 0
            END AS alerta,
            CASE
                WHEN ds.status_active_campaign NOT IN ('TAGGED','VALIDATED','WAITING') THEN 0
                WHEN le.event_type = 'lost_cart' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_active_campaign IN ('TAGGED','WAITING') THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_active_validated END
                ) > 660 THEN 1
                WHEN le.event_type = 'purchase_approved' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_active_campaign IN ('TAGGED','WAITING') THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_active_validated END
                ) > 90 THEN 1
                WHEN le.event_type = 'lost_cart_fast' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_active_campaign IN ('TAGGED','WAITING') THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_active_validated END
                ) > 90 THEN 1
                ELSE 0
            END AS alerta_validated
        FROM leads_pipeline.lead_events le
        INNER JOIN leads_pipeline.orders o  ON le.order_id = o.id
        INNER JOIN ds_pivot ds              ON ds.lead_event_id = le.id
        WHERE le.event_type COLLATE utf8mb4_0900_ai_ci IN ('lost_cart','lost_cart_fast','purchase_approved')
          AND o.order_date >= CURDATE() - INTERVAL 30 DAY

        UNION ALL

        /* ========================= WHATSAPP ========================= */
        SELECT DISTINCT
            'whatsapp'                                              AS canal,
            o.order_id    COLLATE utf8mb4_0900_ai_ci               AS order_id,
            le.event_type COLLATE utf8mb4_0900_ai_ci               AS event_type,
            o.platform    COLLATE utf8mb4_0900_ai_ci               AS platform,
            o.product     COLLATE utf8mb4_0900_ai_ci               AS product_name,
            o.order_date,
            DATE_FORMAT(o.order_date, '%Y-%m')                     AS mes_order,
            ds.status_whatsapp_reportana                           AS status_canal,
            ds.log_reportana                                       AS log_canal,
            NULL                                                   AS call_center_target,
            COALESCE(
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
            ) AS order_datetime_calc,
            CASE
                WHEN ds.status_whatsapp_reportana IN ('TAGGED','VALIDATED')
                    THEN ds.data_insercao_reportana
                WHEN ds.status_whatsapp_reportana = 'WAITING'
                    THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')
                ELSE NULL
            END AS data_insercao_calc,
            CASE
                WHEN ds.status_whatsapp_reportana IN ('TAGGED','VALIDATED')
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_reportana)
                WHEN ds.status_whatsapp_reportana = 'WAITING'
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo'))
                ELSE NULL
            END AS tempo_segundos_calc,
            CASE
                WHEN ds.status_whatsapp_reportana IN ('TAGGED','VALIDATED')
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_reportana)
                ELSE NULL
            END AS tempo_segundos_tagged,
            NULL AS data_insercao_calc_validated,
            NULL AS tempo_segundos_calc_validated,
            NULL AS tempo_segundos_validated,
            CASE
                WHEN ds.status_whatsapp_reportana NOT IN ('TAGGED','VALIDATED','WAITING') THEN 0
                WHEN le.event_type = 'lost_cart' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_whatsapp_reportana = 'WAITING' THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_reportana END
                ) > 660 THEN 1
                WHEN le.event_type = 'purchase_approved' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_whatsapp_reportana = 'WAITING' THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_reportana END
                ) > 60 THEN 1
                WHEN le.event_type = 'lost_cart_fast' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN ds.status_whatsapp_reportana = 'WAITING' THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo') ELSE ds.data_insercao_reportana END
                ) > 60 THEN 1
                ELSE 0
            END AS alerta,
            0 AS alerta_validated
        FROM leads_pipeline.lead_events le
        INNER JOIN leads_pipeline.orders o  ON le.order_id = o.id
        INNER JOIN ds_pivot ds              ON ds.lead_event_id = le.id
        WHERE le.event_type COLLATE utf8mb4_0900_ai_ci IN ('lost_cart','lost_cart_fast','purchase_approved')
          AND o.order_date >= CURDATE() - INTERVAL 30 DAY

        UNION ALL

        /* ========================= CALL CENTER ========================= */
        SELECT DISTINCT
            'call_center'                                           AS canal,
            o.order_id    COLLATE utf8mb4_0900_ai_ci               AS order_id,
            le.event_type COLLATE utf8mb4_0900_ai_ci               AS event_type,
            o.platform    COLLATE utf8mb4_0900_ai_ci               AS platform,
            o.product     COLLATE utf8mb4_0900_ai_ci               AS product_name,
            o.order_date,
            DATE_FORMAT(o.order_date, '%Y-%m')                     AS mes_order,
            COALESCE(ds.status_logicall, ds.status_salesbound)     AS status_canal,
            NULL                                                   AS log_canal,
            le.call_center_target COLLATE utf8mb4_0900_ai_ci       AS call_center_target,
            COALESCE(
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
            ) AS order_datetime_calc,
            CASE
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) IN ('TAGGED','VALIDATED','SENT')
                    THEN CASE WHEN le.call_center_target COLLATE utf8mb4_0900_ai_ci = 'LOGICALL'
                              THEN ds.data_insercao_logicall ELSE ds.data_insercao_salesbound END
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) = 'WAITING'
                    THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')
                ELSE NULL
            END AS data_insercao_calc,
            CASE
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) IN ('TAGGED','VALIDATED','SENT')
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CASE WHEN le.call_center_target COLLATE utf8mb4_0900_ai_ci = 'LOGICALL'
                                THEN ds.data_insercao_logicall ELSE ds.data_insercao_salesbound END)
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) = 'WAITING'
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo'))
                ELSE NULL
            END AS tempo_segundos_calc,
            CASE
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) IN ('TAGGED','VALIDATED','SENT')
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CASE WHEN le.call_center_target COLLATE utf8mb4_0900_ai_ci = 'LOGICALL'
                                THEN ds.data_insercao_logicall ELSE ds.data_insercao_salesbound END)
                ELSE NULL
            END AS tempo_segundos_tagged,
            NULL AS data_insercao_calc_validated,
            NULL AS tempo_segundos_calc_validated,
            NULL AS tempo_segundos_validated,
            CASE
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) NOT IN ('TAGGED','VALIDATED','SENT','WAITING') THEN 0
                WHEN le.event_type = 'lost_cart' AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN COALESCE(ds.status_logicall, ds.status_salesbound) = 'WAITING'
                         THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')
                         ELSE CASE WHEN le.call_center_target COLLATE utf8mb4_0900_ai_ci = 'LOGICALL' THEN ds.data_insercao_logicall ELSE ds.data_insercao_salesbound END END
                ) > 660 THEN 1
                WHEN le.event_type IN ('purchase_approved','lost_cart_fast') AND TIMESTAMPDIFF(SECOND,
                    COALESCE(
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                        STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                    ),
                    CASE WHEN COALESCE(ds.status_logicall, ds.status_salesbound) = 'WAITING'
                         THEN CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')
                         ELSE CASE WHEN le.call_center_target COLLATE utf8mb4_0900_ai_ci = 'LOGICALL' THEN ds.data_insercao_logicall ELSE ds.data_insercao_salesbound END END
                ) > 60 THEN 1
                ELSE 0
            END AS alerta,
            0 AS alerta_validated
        FROM leads_pipeline.lead_events le
        INNER JOIN leads_pipeline.orders o  ON le.order_id = o.id
        INNER JOIN ds_pivot ds              ON ds.lead_event_id = le.id
        WHERE le.event_type COLLATE utf8mb4_0900_ai_ci IN ('lost_cart','lost_cart_fast','purchase_approved')
          AND o.order_date >= CURDATE() - INTERVAL 30 DAY
    ),

    base_calc AS (
        SELECT
            b.*,
            CASE WHEN b.tempo_segundos_tagged         > 0 THEN b.tempo_segundos_tagged         END AS tempo_segundos_pos,
            CASE WHEN b.tempo_segundos_calc           > 0 THEN b.tempo_segundos_calc           END AS tempo_segundos_calc_pos,
            CASE WHEN b.tempo_segundos_validated      > 0 THEN b.tempo_segundos_validated      END AS tempo_segundos_validated_pos,
            CASE WHEN b.tempo_segundos_calc_validated > 0 THEN b.tempo_segundos_calc_validated END AS tempo_segundos_calc_validated_pos
        FROM base b
    ),

    agregado_dia AS (
        SELECT
            canal,
            order_id,
            event_type,
            platform,
            product_name,
            order_date,
            mes_order,
            status_canal,
            log_canal,
            call_center_target,
            COUNT(DISTINCT order_id)                                                           AS orders,
            AVG(tempo_segundos_calc_pos)                                                       AS media_segundos_dia,
            SUM(CASE WHEN tempo_segundos_pos           IS NOT NULL THEN 1 ELSE 0 END)          AS qtd_tagged,
            SUM(CASE WHEN tempo_segundos_validated_pos IS NOT NULL THEN 1 ELSE 0 END)          AS qtd_validated,
            AVG(tempo_segundos_calc_validated_pos)                                             AS media_segundos_dia_validated,
            SUM(alerta)                                                                        AS total_alertas,
            SUM(alerta_validated)                                                              AS total_alertas_email_validated,
            COUNT(*) OVER (PARTITION BY canal, order_date, product_name)                       AS total_linhas_grupo
        FROM base_calc
        GROUP BY
            canal, order_id, event_type, platform, product_name,
            order_date, mes_order, status_canal, log_canal, call_center_target
    ),

    sms_recuperacao AS (
        SELECT canal, data_venda, LOWER(nome_produto) AS product_name,
            SUM(revenue) AS revenue_recup, SUM(company_frontend_sales_brl) AS front_end_sales
        FROM instituto_experience.dashboard_channels_marketing
        WHERE tipo_venda = 'Recuperação'
        GROUP BY canal, data_venda, LOWER(nome_produto)
    ),

    sms_monetizacao AS (
        SELECT canal, data_venda, LOWER(nome_produto) AS product_name,
            SUM(revenue) AS revenue_monet
        FROM instituto_experience.dashboard_channels_marketing
        WHERE tipo_venda = 'Monetização'
        GROUP BY canal, data_venda, LOWER(nome_produto)
    ),

    gross_recovery_target AS (
        SELECT yearmonth, sms_recuperacao, sms_monetizacao, sms_geral,
            email_recuperacao, email_monetizacao, email_geral,
            whatsapp_recuperacao, whatsapp_monetizacao, whatsapp_geral
        FROM instituto_experience.gross_recovery_target
    )

    SELECT
        a.canal, a.event_type, a.platform, a.product_name, a.order_date, a.mes_order,
        a.status_canal AS status_sms, a.log_canal AS log_sms, a.call_center_target, a.orders,
        CAST(SEC_TO_TIME(LEAST(3020399, GREATEST(0, ROUND(a.media_segundos_dia)))) AS CHAR(10))           AS media_tempo_ate_insercao_dia,
        ROUND(a.media_segundos_dia)                                                                        AS media_tempo_dia_segundos,
        ROUND(a.media_segundos_dia / 60,   2)                                                              AS media_tempo_dia_minutos,
        ROUND(a.media_segundos_dia / 3600, 2)                                                              AS media_tempo_dia_horas,
        CAST(SEC_TO_TIME(LEAST(3020399, GREATEST(0, ROUND(a.media_segundos_dia_validated)))) AS CHAR(10)) AS media_tempo_ate_insercao_dia_validated,
        ROUND(a.media_segundos_dia_validated)                                                              AS media_tempo_dia_segundos_validated,
        ROUND(a.media_segundos_dia_validated / 60,   2)                                                    AS media_tempo_dia_minutos_validated,
        ROUND(a.media_segundos_dia_validated / 3600, 2)                                                    AS media_tempo_dia_horas_validated,
        a.qtd_tagged, a.qtd_validated, a.total_alertas, a.total_alertas_email_validated,
        a.status_canal AS status_base,
        ROUND(s.revenue_recup   / NULLIF(a.total_linhas_grupo, 0), 4) AS revenue_recup,
        ROUND(m.revenue_monet   / NULLIF(a.total_linhas_grupo, 0), 4) AS revenue_monet,
        ROUND(s.front_end_sales / NULLIF(a.total_linhas_grupo, 0), 4) AS front_end_sales,
        t.sms_recuperacao AS recup_target, t.sms_monetizacao AS monet_target, t.sms_geral AS geral_target,
        t.email_recuperacao AS email_recup_target, t.email_monetizacao AS email_monet_target, t.email_geral AS email_geral_target,
        t.whatsapp_recuperacao AS whatsapp_recup_target, t.whatsapp_monetizacao AS whatsapp_monet_target, t.whatsapp_geral AS whatsapp_geral_target
    FROM agregado_dia a
    LEFT JOIN sms_recuperacao s
        ON s.canal = a.canal AND a.order_date = s.data_venda
        AND LOWER(a.product_name) COLLATE utf8mb4_0900_ai_ci = s.product_name COLLATE utf8mb4_0900_ai_ci
    LEFT JOIN sms_monetizacao m
        ON m.canal = a.canal AND a.order_date = m.data_venda
        AND LOWER(a.product_name) COLLATE utf8mb4_0900_ai_ci = m.product_name COLLATE utf8mb4_0900_ai_ci
    LEFT JOIN gross_recovery_target t
        ON a.mes_order = DATE_FORMAT(t.yearmonth, '%Y-%m');

    -- 3. Troca atômica
    RENAME TABLE
        instituto_experience.dashboard_auditoria_leads       TO instituto_experience.dashboard_auditoria_leads_old,
        instituto_experience.dashboard_auditoria_leads_stage TO instituto_experience.dashboard_auditoria_leads,
        instituto_experience.dashboard_auditoria_leads_old   TO instituto_experience.dashboard_auditoria_leads_stage;

END
```
