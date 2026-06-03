---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-11 19:57:23"
alterada_em: "2026-05-11 19:57:23"
execucoes: 182
tags: [rotina, procedure]
---

# refresh_dashboard_leads_alerts

## Dependências

- **Lê:** [[orders]]
- **Escreve:** [[dashboard_leads_alerts_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_leads_alerts_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 49.0 s |
| Tempo máx | 2m55s |
| Tempo total | 2h28m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 32,020,708 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_leads_alerts_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_leads_alerts_stage;

    -- 2. Insere na stage
    INSERT INTO instituto_experience.dashboard_leads_alerts_stage
    WITH

    ds_pivot AS (
        SELECT
            lead_event_id,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'SMS'                                                                   THEN status COLLATE utf8mb4_0900_ai_ci END) AS status_sms,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'ACTIVECAMPAIGN'                                                        THEN status COLLATE utf8mb4_0900_ai_ci END) AS status_active_campaign,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'WHATSAPP'                                                              THEN status COLLATE utf8mb4_0900_ai_ci END) AS status_whatsapp_reportana,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'CALLCENTER' AND extra_status COLLATE utf8mb4_0900_ai_ci = 'SALESBOUND' THEN status COLLATE utf8mb4_0900_ai_ci END) AS status_salesbound,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'CALLCENTER' AND extra_status COLLATE utf8mb4_0900_ai_ci = 'LOGICALL'   THEN status COLLATE utf8mb4_0900_ai_ci END) AS status_logicall,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'SMS'                                                                   THEN data_insercao                    END) AS data_insercao_slicktext,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'ACTIVECAMPAIGN'                                                        THEN data_insercao                    END) AS data_insercao_activecampaign,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'WHATSAPP'                                                              THEN data_insercao                    END) AS data_insercao_reportana,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'CALLCENTER' AND extra_status COLLATE utf8mb4_0900_ai_ci = 'LOGICALL'   THEN data_insercao                    END) AS data_insercao_logicall,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'CALLCENTER' AND extra_status COLLATE utf8mb4_0900_ai_ci = 'SALESBOUND' THEN data_insercao                    END) AS data_insercao_salesbound,
            MAX(CASE WHEN canal COLLATE utf8mb4_0900_ai_ci = 'ACTIVECAMPAIGN' AND status COLLATE utf8mb4_0900_ai_ci = 'VALIDATED'    THEN data_insercao                    END) AS data_insercao_active_validated
        FROM leads_pipeline.distribution_status
        GROUP BY lead_event_id
    ),

    base AS (

        /* ========================= SMS ========================= */
        SELECT DISTINCT
            'sms'                                                   AS canal,
            le.id                                                   AS unique_key,
            o.order_id   COLLATE utf8mb4_0900_ai_ci                AS order_id,
            l.email      COLLATE utf8mb4_0900_ai_ci                AS client_email,
            le.event_type COLLATE utf8mb4_0900_ai_ci               AS event_type,
            o.platform   COLLATE utf8mb4_0900_ai_ci                AS platform,
            CONCAT(
                UPPER(LEFT(REGEXP_REPLACE(REPLACE(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(o.product, ' - ', 1), ' + ', 1)), ' ', ''), '^[0-9]+', ''), 1)),
                LOWER(SUBSTRING(REGEXP_REPLACE(REPLACE(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(o.product, ' - ', 1), ' + ', 1)), ' ', ''), '^[0-9]+', ''), 2))
            ) COLLATE utf8mb4_0900_ai_ci                           AS product_name,
            o.order_date,
            NULL                                                   AS call_center_target,
            COALESCE(
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
            ) AS order_date_hour,
            ds.data_insercao_slicktext                             AS data_insercao,
            NULL                                                   AS data_insercao_validated,
            -- tempo_ate_insercao
            CASE
                WHEN ds.status_sms IN ('TAGGED','VALIDATED')
                    THEN TIMEDIFF(ds.data_insercao_slicktext,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ))
                WHEN ds.status_sms = 'WAITING'
                    THEN TIMEDIFF(CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo'),
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ))
                ELSE NULL
            END AS tempo_ate_insercao,
            -- tempo_segundos
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
            END AS tempo_segundos,
            -- tempo_minutos
            CASE
                WHEN ds.status_sms IN ('TAGGED','VALIDATED')
                    THEN ROUND(TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_slicktext) / 60, 2)
                WHEN ds.status_sms = 'WAITING'
                    THEN ROUND(TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')) / 60, 2)
                ELSE NULL
            END AS tempo_minutos,
            NULL AS tempo_segundos_validated,
            NULL AS tempo_minutos_validated,
            -- alerta
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
            0                                                      AS alerta_validated,
            ds.status_sms                                          AS status_canal,
            NULL                                                   AS status_sms_geral,
            NULL                                                   AS source,
            NULL                                                   AS lambda_name
        FROM leads_pipeline.lead_events le
        INNER JOIN leads_pipeline.orders o  ON le.order_id = o.id
        INNER JOIN leads_pipeline.leads  l  ON le.lead_id  = l.id
        INNER JOIN ds_pivot ds              ON ds.lead_event_id = le.id
        WHERE le.event_type COLLATE utf8mb4_0900_ai_ci IN ('lost_cart','lost_cart_fast','purchase_approved','cross_sell')
          AND o.order_date >= CURDATE() - INTERVAL 30 DAY

        UNION ALL

        /* ========================= EMAIL ========================= */
        SELECT DISTINCT
            'email'                                                 AS canal,
            le.id                                                   AS unique_key,
            o.order_id   COLLATE utf8mb4_0900_ai_ci                AS order_id,
            l.email      COLLATE utf8mb4_0900_ai_ci                AS client_email,
            le.event_type COLLATE utf8mb4_0900_ai_ci               AS event_type,
            o.platform   COLLATE utf8mb4_0900_ai_ci                AS platform,
            CONCAT(
                UPPER(LEFT(REGEXP_REPLACE(REPLACE(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(o.product, ' - ', 1), ' + ', 1)), ' ', ''), '^[0-9]+', ''), 1)),
                LOWER(SUBSTRING(REGEXP_REPLACE(REPLACE(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(o.product, ' - ', 1), ' + ', 1)), ' ', ''), '^[0-9]+', ''), 2))
            ) COLLATE utf8mb4_0900_ai_ci                           AS product_name,
            o.order_date,
            NULL                                                   AS call_center_target,
            COALESCE(
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
            ) AS order_date_hour,
            ds.data_insercao_activecampaign                        AS data_insercao,
            ds.data_insercao_active_validated                      AS data_insercao_validated,
            -- tempo_ate_insercao
            CASE
                WHEN ds.status_active_campaign IN ('TAGGED','VALIDATED')
                    THEN TIMEDIFF(ds.data_insercao_activecampaign,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ))
                WHEN ds.status_active_campaign = 'WAITING'
                    THEN TIMEDIFF(CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo'),
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ))
                ELSE NULL
            END AS tempo_ate_insercao,
            -- tempo_segundos
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
            END AS tempo_segundos,
            -- tempo_minutos
            CASE
                WHEN ds.status_active_campaign IN ('TAGGED','VALIDATED')
                    THEN ROUND(TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_activecampaign) / 60, 2)
                WHEN ds.status_active_campaign = 'WAITING'
                    THEN ROUND(TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')) / 60, 2)
                ELSE NULL
            END AS tempo_minutos,
            -- tempo_segundos_validated
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
            END AS tempo_segundos_validated,
            -- tempo_minutos_validated
            CASE
                WHEN ds.status_active_campaign = 'VALIDATED'
                    THEN ROUND(TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_active_validated) / 60, 2)
                WHEN ds.status_active_campaign IN ('TAGGED','WAITING')
                    THEN ROUND(TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')) / 60, 2)
                ELSE NULL
            END AS tempo_minutos_validated,
            -- alerta
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
            -- alerta_validated
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
            END AS alerta_validated,
            ds.status_active_campaign                              AS status_canal,
            NULL                                                   AS status_sms_geral,
            NULL                                                   AS source,
            NULL                                                   AS lambda_name
        FROM leads_pipeline.lead_events le
        INNER JOIN leads_pipeline.orders o  ON le.order_id = o.id
        INNER JOIN leads_pipeline.leads  l  ON le.lead_id  = l.id
        INNER JOIN ds_pivot ds              ON ds.lead_event_id = le.id
        WHERE le.event_type COLLATE utf8mb4_0900_ai_ci IN ('lost_cart','lost_cart_fast','purchase_approved')
          AND o.order_date >= CURDATE() - INTERVAL 30 DAY

        UNION ALL

        /* ========================= WHATSAPP ========================= */
        SELECT DISTINCT
            'whatsapp'                                              AS canal,
            le.id                                                   AS unique_key,
            o.order_id   COLLATE utf8mb4_0900_ai_ci                AS order_id,
            l.email      COLLATE utf8mb4_0900_ai_ci                AS client_email,
            le.event_type COLLATE utf8mb4_0900_ai_ci               AS event_type,
            o.platform   COLLATE utf8mb4_0900_ai_ci                AS platform,
            CONCAT(
                UPPER(LEFT(REGEXP_REPLACE(REPLACE(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(o.product, ' - ', 1), ' + ', 1)), ' ', ''), '^[0-9]+', ''), 1)),
                LOWER(SUBSTRING(REGEXP_REPLACE(REPLACE(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(o.product, ' - ', 1), ' + ', 1)), ' ', ''), '^[0-9]+', ''), 2))
            ) COLLATE utf8mb4_0900_ai_ci                           AS product_name,
            o.order_date,
            NULL                                                   AS call_center_target,
            COALESCE(
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
            ) AS order_date_hour,
            ds.data_insercao_reportana                             AS data_insercao,
            NULL                                                   AS data_insercao_validated,
            -- tempo_ate_insercao
            CASE
                WHEN ds.status_whatsapp_reportana IN ('TAGGED','VALIDATED')
                    THEN TIMEDIFF(ds.data_insercao_reportana,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ))
                WHEN ds.status_whatsapp_reportana = 'WAITING'
                    THEN TIMEDIFF(CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo'),
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ))
                ELSE NULL
            END AS tempo_ate_insercao,
            -- tempo_segundos
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
            END AS tempo_segundos,
            -- tempo_minutos
            CASE
                WHEN ds.status_whatsapp_reportana IN ('TAGGED','VALIDATED')
                    THEN ROUND(TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), ds.data_insercao_reportana) / 60, 2)
                WHEN ds.status_whatsapp_reportana = 'WAITING'
                    THEN ROUND(TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')) / 60, 2)
                ELSE NULL
            END AS tempo_minutos,
            NULL AS tempo_segundos_validated,
            NULL AS tempo_minutos_validated,
            -- alerta
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
            0                                                      AS alerta_validated,
            ds.status_whatsapp_reportana                           AS status_canal,
            NULL                                                   AS status_sms_geral,
            NULL                                                   AS source,
            NULL                                                   AS lambda_name
        FROM leads_pipeline.lead_events le
        INNER JOIN leads_pipeline.orders o  ON le.order_id = o.id
        INNER JOIN leads_pipeline.leads  l  ON le.lead_id  = l.id
        INNER JOIN ds_pivot ds              ON ds.lead_event_id = le.id
        WHERE le.event_type COLLATE utf8mb4_0900_ai_ci IN ('lost_cart','lost_cart_fast','purchase_approved')
          AND o.order_date >= CURDATE() - INTERVAL 30 DAY

        UNION ALL

        /* ========================= CALL CENTER ========================= */
        SELECT DISTINCT
            'call_center'                                           AS canal,
            le.id                                                   AS unique_key,
            o.order_id   COLLATE utf8mb4_0900_ai_ci                AS order_id,
            l.email      COLLATE utf8mb4_0900_ai_ci                AS client_email,
            le.event_type COLLATE utf8mb4_0900_ai_ci               AS event_type,
            o.platform   COLLATE utf8mb4_0900_ai_ci                AS platform,
            CONCAT(
                UPPER(LEFT(REGEXP_REPLACE(REPLACE(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(o.product, ' - ', 1), ' + ', 1)), ' ', ''), '^[0-9]+', ''), 1)),
                LOWER(SUBSTRING(REGEXP_REPLACE(REPLACE(TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(o.product, ' - ', 1), ' + ', 1)), ' ', ''), '^[0-9]+', ''), 2))
            ) COLLATE utf8mb4_0900_ai_ci                           AS product_name,
            o.order_date,
            le.call_center_target COLLATE utf8mb4_0900_ai_ci       AS call_center_target,
            COALESCE(
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
            ) AS order_date_hour,
            CASE WHEN le.call_center_target COLLATE utf8mb4_0900_ai_ci = 'LOGICALL'
                THEN ds.data_insercao_logicall
                ELSE ds.data_insercao_salesbound
            END                                                    AS data_insercao,
            NULL                                                   AS data_insercao_validated,
            -- tempo_ate_insercao
            CASE
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) IN ('TAGGED','VALIDATED','SENT')
                    THEN TIMEDIFF(
                        CASE WHEN le.call_center_target COLLATE utf8mb4_0900_ai_ci = 'LOGICALL' THEN ds.data_insercao_logicall ELSE ds.data_insercao_salesbound END,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ))
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) = 'WAITING'
                    THEN TIMEDIFF(CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo'),
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ))
                ELSE NULL
            END AS tempo_ate_insercao,
            -- tempo_segundos
            CASE
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) IN ('TAGGED','VALIDATED','SENT')
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CASE WHEN le.call_center_target COLLATE utf8mb4_0900_ai_ci = 'LOGICALL' THEN ds.data_insercao_logicall ELSE ds.data_insercao_salesbound END)
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) = 'WAITING'
                    THEN TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo'))
                ELSE NULL
            END AS tempo_segundos,
            -- tempo_minutos
            CASE
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) IN ('TAGGED','VALIDATED','SENT')
                    THEN ROUND(TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CASE WHEN le.call_center_target COLLATE utf8mb4_0900_ai_ci = 'LOGICALL' THEN ds.data_insercao_logicall ELSE ds.data_insercao_salesbound END) / 60, 2)
                WHEN COALESCE(ds.status_logicall, ds.status_salesbound) = 'WAITING'
                    THEN ROUND(TIMESTAMPDIFF(SECOND,
                        COALESCE(
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i:%s'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', o.order_time), '%Y-%m-%d %H:%i'),
                            STR_TO_DATE(CONCAT(o.order_date, ' ', '00:00:00'),   '%Y-%m-%d %H:%i:%s')
                        ), CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')) / 60, 2)
                ELSE NULL
            END AS tempo_minutos,
            NULL AS tempo_segundos_validated,
            NULL AS tempo_minutos_validated,
            -- alerta
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
            0                                                      AS alerta_validated,
            COALESCE(ds.status_logicall, ds.status_salesbound)    AS status_canal,
            NULL                                                   AS status_sms_geral,
            NULL                                                   AS source,
            NULL                                                   AS lambda_name
        FROM leads_pipeline.lead_events le
        INNER JOIN leads_pipeline.orders o  ON le.order_id = o.id
        INNER JOIN leads_pipeline.leads  l  ON le.lead_id  = l.id
        INNER JOIN ds_pivot ds              ON ds.lead_event_id = le.id
        WHERE le.event_type COLLATE utf8mb4_0900_ai_ci IN ('lost_cart','lost_cart_fast','purchase_approved')
          AND o.order_date >= CURDATE() - INTERVAL 30 DAY
    )

    /* ── SELECT final — só registros com alerta ── */
    SELECT
        canal,
        unique_key,
        order_id,
        client_email,
        event_type,
        platform,
        product_name,
        order_date,
        order_date_hour,
        call_center_target,
        data_insercao,
        data_insercao_validated,
        tempo_ate_insercao,
        tempo_segundos,
        tempo_minutos,
        tempo_segundos_validated,
        tempo_minutos_validated,
        CASE
            WHEN alerta_validated = 1 THEN tempo_segundos_validated
            ELSE tempo_segundos
        END AS tempo_segundos_alerta,
        CASE
            WHEN alerta_validated = 1 THEN tempo_minutos_validated
            ELSE tempo_minutos
        END AS tempo_minutos_alerta,
        alerta,
        alerta_validated,
        CASE
            WHEN alerta = 1 AND alerta_validated = 1 THEN 'ambos'
            WHEN alerta = 1                          THEN 'insercao_original'
            WHEN alerta_validated = 1                THEN 'validated'
            ELSE NULL
        END AS origem_alerta,

        /* ── status_base ── */
        CASE
            WHEN canal = 'call_center' THEN
                CASE
                    WHEN data_insercao IS NOT NULL THEN 'SENT'
                    ELSE 'WAITING'
                END
            ELSE
                CASE
                    WHEN data_insercao_validated IS NOT NULL THEN 'VALIDATED'
                    WHEN data_insercao IS NOT NULL           THEN 'TAGGED'
                    ELSE 'WAITING'
                END
        END AS status_base,

        status_canal                                               AS status_sms,
        status_sms_geral,
        source,
        lambda_name
    FROM base
    WHERE (alerta = 1 OR alerta_validated = 1)
      AND order_date >= CURDATE() - INTERVAL 30 DAY;

    -- 3. Troca atômica
    RENAME TABLE
        instituto_experience.dashboard_leads_alerts       TO instituto_experience.dashboard_leads_alerts_old,
        instituto_experience.dashboard_leads_alerts_stage TO instituto_experience.dashboard_leads_alerts,
        instituto_experience.dashboard_leads_alerts_old   TO instituto_experience.dashboard_leads_alerts_stage;

END
```
