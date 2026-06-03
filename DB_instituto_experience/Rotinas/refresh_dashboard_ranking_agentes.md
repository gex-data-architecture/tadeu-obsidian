---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-04-30 01:15:01"
alterada_em: "2026-04-30 01:15:01"
execucoes: 179
tags: [rotina, procedure]
---

# refresh_dashboard_ranking_agentes

## Dependências

- **Lê:** [[cw_conversations_mat]], [[cw_messages_mat]], [[cw_users_mat]], [[dashboard_atendimento]], [[dashboard_reembolso]], [[dashboard_sla_times]]
- **Escreve:** [[dashboard_ranking_agentes_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_ranking_agentes_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 179 |
| Tempo médio | 13.8 s |
| Tempo máx | 34.1 s |
| Tempo total | 41m17s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 2,843,630 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_ranking_agentes_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_ranking_agentes_stage;

    -- 2. Insere na stage
    INSERT INTO instituto_experience.dashboard_ranking_agentes_stage
    WITH

    intervalos_time AS (
        SELECT
            st.conversation_id,
            st.entrada_sac                                          AS sac_inicio,
            COALESCE(st.entrada_retencao, c.updated_at)             AS sac_fim,
            st.entrada_retencao                                     AS retencao_inicio,
            COALESCE(st.entrada_backoffice, c.updated_at)           AS retencao_fim,
            st.entrada_backoffice                                   AS backoffice_inicio,
            c.updated_at                                            AS backoffice_fim
        FROM instituto_experience.dashboard_sla_times st
        INNER JOIN instituto_experience.cw_conversations_mat c
            ON st.conversation_id = c.id
    ),

    msgs_sac AS (
        SELECT
            DATE(CONVERT_TZ(m.created_at, '+00:00', '-03:00'))      AS data,
            CONVERT(u.name USING utf8mb4) COLLATE utf8mb4_unicode_ci AS agente,
            'SAC'                                                   AS time_ranking,
            COUNT(*)                                                AS volume_msgs,
            COUNT(DISTINCT m.conversation_id)                       AS conversas
        FROM instituto_experience.cw_messages_mat m
        INNER JOIN instituto_experience.cw_users_mat u ON m.sender_id = u.id
        INNER JOIN intervalos_time it ON m.conversation_id = it.conversation_id
        INNER JOIN (SELECT id FROM instituto_experience.cw_conversations_mat WHERE account_id = 1) conv
            ON m.conversation_id = conv.id
        WHERE m.message_type IN (0, 1)
          AND m.sender_type = 'User'
          AND m.sender_id != 2
          AND it.sac_inicio IS NOT NULL
          AND m.created_at >= it.sac_inicio
          AND m.created_at < it.sac_fim
        GROUP BY DATE(CONVERT_TZ(m.created_at, '+00:00', '-03:00')), u.name
    ),

    msgs_retencao AS (
        SELECT
            DATE(CONVERT_TZ(m.created_at, '+00:00', '-03:00'))      AS data,
            CONVERT(u.name USING utf8mb4) COLLATE utf8mb4_unicode_ci AS agente,
            'Retenção'                                              AS time_ranking,
            COUNT(*)                                                AS volume_msgs,
            COUNT(DISTINCT m.conversation_id)                       AS conversas
        FROM instituto_experience.cw_messages_mat m
        INNER JOIN instituto_experience.cw_users_mat u ON m.sender_id = u.id
        INNER JOIN intervalos_time it ON m.conversation_id = it.conversation_id
        INNER JOIN (SELECT id FROM instituto_experience.cw_conversations_mat WHERE account_id = 1) conv
            ON m.conversation_id = conv.id
        WHERE m.message_type IN (0, 1)
          AND m.sender_type = 'User'
          AND m.sender_id != 2
          AND it.retencao_inicio IS NOT NULL
          AND m.created_at >= it.retencao_inicio
          AND m.created_at < it.retencao_fim
        GROUP BY DATE(CONVERT_TZ(m.created_at, '+00:00', '-03:00')), u.name
    ),

    msgs_backoffice AS (
        SELECT
            DATE(CONVERT_TZ(m.created_at, '+00:00', '-03:00'))      AS data,
            CONVERT(u.name USING utf8mb4) COLLATE utf8mb4_unicode_ci AS agente,
            'Back Office'                                           AS time_ranking,
            COUNT(*)                                                AS volume_msgs,
            COUNT(DISTINCT m.conversation_id)                       AS conversas
        FROM instituto_experience.cw_messages_mat m
        INNER JOIN instituto_experience.cw_users_mat u ON m.sender_id = u.id
        INNER JOIN intervalos_time it ON m.conversation_id = it.conversation_id
        INNER JOIN (SELECT id FROM instituto_experience.cw_conversations_mat WHERE account_id = 1) conv
            ON m.conversation_id = conv.id
        WHERE m.message_type IN (0, 1)
          AND m.sender_type = 'User'
          AND m.sender_id != 2
          AND it.backoffice_inicio IS NOT NULL
          AND m.created_at >= it.backoffice_inicio
          AND m.created_at < it.backoffice_fim
        GROUP BY DATE(CONVERT_TZ(m.created_at, '+00:00', '-03:00')), u.name
    ),

    sla_agente AS (
        SELECT
            st.data_criacao                                         AS data,
            CONVERT(st.assignee_name USING utf8mb4) COLLATE utf8mb4_unicode_ci AS agente,
            ROUND(AVG(st.frt_sac_minutos), 1)                       AS frt_sac,
            ROUND(AVG(st.nrt_sac_minutos), 1)                       AS nrt_sac,
            ROUND(AVG(st.sla_fila_sac_minutos), 1)                  AS sla_sac,
            ROUND(AVG(st.frt_retencao_minutos), 1)                  AS frt_retencao,
            ROUND(AVG(st.nrt_retencao_minutos), 1)                  AS nrt_retencao,
            ROUND(AVG(st.sla_fila_retencao_minutos), 1)             AS sla_retencao,
            ROUND(AVG(st.frt_backoffice_minutos), 1)                AS frt_backoffice,
            ROUND(AVG(st.nrt_backoffice_minutos), 1)                AS nrt_backoffice,
            ROUND(AVG(st.sla_fila_backoffice_minutos), 1)           AS sla_backoffice
        FROM instituto_experience.dashboard_sla_times st
        WHERE st.assignee_name IS NOT NULL
        GROUP BY st.data_criacao, st.assignee_name
    ),

    trv_agente AS (
        SELECT
            DATE(dr.created_at_date)                                AS data,
            CONVERT(dr.assigned_agent USING utf8mb4) COLLATE utf8mb4_unicode_ci AS agente,
            SUM(dr.valor_venda_usd)                                 AS valor_venda_usd,
            SUM(dr.valor_refund_usd)                                AS valor_refund_usd,
            COUNT(CASE WHEN dr.is_refund = 1 THEN 1 END)            AS volume_reembolsos,
            ROUND(AVG(
                CASE WHEN dr.is_refund = 1
                          AND dr.opened_date IS NOT NULL
                          AND dr.closed_date IS NOT NULL
                     THEN TIMESTAMPDIFF(MINUTE, dr.opened_date, dr.closed_date)
                     ELSE NULL END
            ), 1)                                                   AS tempo_medio_processamento_minutos
        FROM instituto_experience.dashboard_reembolso dr
        WHERE dr.assigned_agent IS NOT NULL
        GROUP BY DATE(dr.created_at_date), dr.assigned_agent
    ),

    retornos_agente AS (
        SELECT
            da.data_criacao                                         AS data,
            CONVERT(da.assignee_name USING utf8mb4) COLLATE utf8mb4_unicode_ci AS agente,
            SUM(da.is_retorno)                                      AS retornos
        FROM instituto_experience.dashboard_atendimento da
        WHERE da.nome_time = 'SAC'
          AND da.assignee_name IS NOT NULL
        GROUP BY da.data_criacao, da.assignee_name
    ),

    base AS (
        SELECT data, agente, 'SAC' AS time_ranking FROM msgs_sac
        UNION
        SELECT data, agente, 'Retenção' AS time_ranking FROM msgs_retencao
        UNION
        SELECT data, agente, 'Back Office' AS time_ranking FROM msgs_backoffice
        UNION
        SELECT data, agente, 'SAC' AS time_ranking FROM sla_agente WHERE frt_sac IS NOT NULL
        UNION
        SELECT data, agente, 'Retenção' AS time_ranking FROM sla_agente WHERE frt_retencao IS NOT NULL
        UNION
        SELECT data, agente, 'Back Office' AS time_ranking FROM sla_agente WHERE frt_backoffice IS NOT NULL
        UNION
        SELECT data, agente, 'Retenção' AS time_ranking FROM trv_agente
        UNION
        SELECT data, agente, 'Back Office' AS time_ranking FROM trv_agente
    )

    SELECT
        b.data,
        b.agente,
        b.time_ranking,
        CASE b.time_ranking
            WHEN 'SAC'         THEN COALESCE(ms.volume_msgs, 0)
            WHEN 'Retenção'    THEN COALESCE(mr.volume_msgs, 0)
            WHEN 'Back Office' THEN COALESCE(mb.volume_msgs, 0)
        END                                                         AS volume_msgs,
        CASE b.time_ranking
            WHEN 'SAC'         THEN COALESCE(ms.conversas, 0)
            WHEN 'Retenção'    THEN COALESCE(mr.conversas, 0)
            WHEN 'Back Office' THEN COALESCE(mb.conversas, 0)
        END                                                         AS conversas,
        CASE WHEN b.time_ranking = 'SAC' THEN 80 ELSE NULL END      AS meta_msgs_dia,
        CASE WHEN b.time_ranking = 'SAC'
             THEN ROUND(COALESCE(ms.volume_msgs, 0) / 80 * 100, 1)
             ELSE NULL END                                          AS pct_meta,
        CASE WHEN b.time_ranking = 'SAC'
             THEN COALESCE(ra.retornos, 0)
             ELSE NULL END                                          AS retornos,
        CASE b.time_ranking
            WHEN 'SAC'         THEN sa.frt_sac
            WHEN 'Retenção'    THEN sa.frt_retencao
            WHEN 'Back Office' THEN sa.frt_backoffice
        END                                                         AS frt_minutos,
        CASE b.time_ranking
            WHEN 'SAC'         THEN sa.nrt_sac
            WHEN 'Retenção'    THEN sa.nrt_retencao
            WHEN 'Back Office' THEN sa.nrt_backoffice
        END                                                         AS nrt_minutos,
        CASE b.time_ranking
            WHEN 'SAC'         THEN sa.sla_sac
            WHEN 'Retenção'    THEN sa.sla_retencao
            WHEN 'Back Office' THEN sa.sla_backoffice
        END                                                         AS sla_fila_minutos,
        CASE WHEN b.time_ranking IN ('Retenção', 'Back Office')
             THEN trv.valor_venda_usd ELSE NULL END                  AS valor_venda_usd,
        CASE WHEN b.time_ranking IN ('Retenção', 'Back Office')
             THEN trv.valor_refund_usd ELSE NULL END                 AS valor_refund_usd,
        CASE WHEN b.time_ranking = 'Back Office'
             THEN trv.volume_reembolsos ELSE NULL END                AS volume_reembolsos,
        CASE WHEN b.time_ranking = 'Back Office'
             THEN trv.tempo_medio_processamento_minutos ELSE NULL END AS tempo_processamento_minutos

    FROM (SELECT DISTINCT data, agente, time_ranking FROM base) b
    LEFT JOIN msgs_sac ms
        ON b.data = ms.data AND b.agente = ms.agente AND b.time_ranking = 'SAC'
    LEFT JOIN msgs_retencao mr
        ON b.data = mr.data AND b.agente = mr.agente AND b.time_ranking = 'Retenção'
    LEFT JOIN msgs_backoffice mb
        ON b.data = mb.data AND b.agente = mb.agente AND b.time_ranking = 'Back Office'
    LEFT JOIN sla_agente sa
        ON b.data = sa.data AND b.agente = sa.agente
    LEFT JOIN trv_agente trv
        ON b.data = trv.data AND b.agente = trv.agente
    LEFT JOIN retornos_agente ra
        ON b.data = ra.data AND b.agente = ra.agente AND b.time_ranking = 'SAC'
    ORDER BY b.data, b.time_ranking, b.agente;

    -- 3. Troca atômica
    RENAME TABLE
        instituto_experience.dashboard_ranking_agentes       TO instituto_experience.dashboard_ranking_agentes_old,
        instituto_experience.dashboard_ranking_agentes_stage TO instituto_experience.dashboard_ranking_agentes,
        instituto_experience.dashboard_ranking_agentes_old   TO instituto_experience.dashboard_ranking_agentes_stage;

END
```
