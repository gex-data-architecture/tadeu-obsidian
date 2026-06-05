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

# refresh_dashboard_sla_times

## Dependências

- **Lê:** [[cw_activities_mat]], [[cw_conversations_mat]], [[cw_messages_mat]], [[cw_team_members_mat]], [[cw_users_mat]]
- **Escreve:** [[dashboard_sla_times_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_sla_times_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 179 |
| Tempo médio | 1m5s |
| Tempo máx | 1m42s |
| Tempo total | 3h13m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 95,361,477 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_sla_times_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_sla_times_stage;

    -- 2. Insere na stage
    INSERT INTO instituto_experience.dashboard_sla_times_stage
    WITH

    entradas_time AS (
        SELECT
            c.id AS conversation_id,
            COALESCE(
                MAX(CASE WHEN a.content LIKE '%time de sac%'
                              OR a.content LIKE '%equipe de sac%'
                    THEN a.created_at ELSE NULL END),
                c.created_at
            )                                               AS entrada_sac,
            MAX(CASE WHEN a.content LIKE '%time de retenção%'
                THEN a.created_at ELSE NULL END)            AS entrada_retencao,
            MAX(CASE WHEN a.content LIKE '%time de back office%'
                       OR a.content LIKE '%equipe de backoffice%'
                THEN a.created_at ELSE NULL END)            AS entrada_backoffice
        FROM instituto_experience.cw_conversations_mat c
        LEFT JOIN instituto_experience.cw_activities_mat a
            ON c.id = a.conversation_id
        WHERE c.account_id = 1
        GROUP BY c.id, c.created_at
    ),

    msgs_base AS (
        SELECT
            m.conversation_id,
            m.created_at,
            m.sender_type,
            m.sender_id,
            tm.team_id                                      AS agente_team_id
        FROM instituto_experience.cw_messages_mat m
        LEFT JOIN instituto_experience.cw_team_members_mat tm
            ON m.sender_id = tm.user_id
        INNER JOIN (
            SELECT id FROM instituto_experience.cw_conversations_mat
            WHERE account_id = 1
        ) conv ON m.conversation_id = conv.id
        WHERE m.message_type IN (0, 1)
    ),

    nrt_msgs AS (
        SELECT
            c_msg.conversation_id,
            c_msg.created_at                                AS msg_cliente_at,
            et.entrada_sac,
            et.entrada_retencao,
            et.entrada_backoffice,
            CASE
                WHEN et.entrada_backoffice IS NOT NULL
                     AND c_msg.created_at >= et.entrada_backoffice THEN 'backoffice'
                WHEN et.entrada_retencao IS NOT NULL
                     AND c_msg.created_at >= et.entrada_retencao  THEN 'retencao'
                WHEN et.entrada_sac IS NOT NULL
                     AND c_msg.created_at >= et.entrada_sac       THEN 'sac'
                ELSE 'sac'
            END                                             AS time_vigente,
            MIN(a_msg.created_at)                           AS proxima_msg_agente_at
        FROM msgs_base c_msg
        INNER JOIN msgs_base a_msg
            ON  c_msg.conversation_id = a_msg.conversation_id
            AND a_msg.created_at > c_msg.created_at
            AND a_msg.sender_type = 'User'
        LEFT JOIN entradas_time et
            ON c_msg.conversation_id = et.conversation_id
        WHERE c_msg.sender_type = 'Contact'
        GROUP BY
            c_msg.conversation_id,
            c_msg.created_at,
            et.entrada_sac,
            et.entrada_retencao,
            et.entrada_backoffice
    ),

    nrt_agregado AS (
        SELECT
            conversation_id,
            AVG(CASE WHEN time_vigente = 'sac'
                THEN TIMESTAMPDIFF(MINUTE, msg_cliente_at, proxima_msg_agente_at)
                ELSE NULL END)                              AS nrt_sac_minutos,
            AVG(CASE WHEN time_vigente = 'retencao'
                THEN TIMESTAMPDIFF(MINUTE, msg_cliente_at, proxima_msg_agente_at)
                ELSE NULL END)                              AS nrt_retencao_minutos,
            AVG(CASE WHEN time_vigente = 'backoffice'
                THEN TIMESTAMPDIFF(MINUTE, msg_cliente_at, proxima_msg_agente_at)
                ELSE NULL END)                              AS nrt_backoffice_minutos,
            AVG(TIMESTAMPDIFF(MINUTE, msg_cliente_at, proxima_msg_agente_at))
                                                            AS nrt_global_minutos
        FROM nrt_msgs
        GROUP BY conversation_id
    ),

    msgs AS (
        SELECT
            m.conversation_id,
            MIN(CASE WHEN m.sender_type = 'User'
                          AND m.sender_id != 2
                THEN m.created_at ELSE NULL END)            AS primeira_msg_agente,
            MIN(CASE WHEN m.sender_type = 'User'
                          AND m.sender_id = 2
                THEN m.created_at ELSE NULL END)            AS primeira_msg_ia,
            MIN(CASE WHEN m.sender_type = 'User'
                          AND m.sender_id != 2
                          AND tm.team_id = 1
                THEN m.created_at ELSE NULL END)            AS primeira_msg_sac,
            MIN(CASE WHEN m.sender_type = 'User'
                          AND m.sender_id != 2
                          AND tm.team_id = 2
                THEN m.created_at ELSE NULL END)            AS primeira_msg_retencao,
            MIN(CASE WHEN m.sender_type = 'User'
                          AND m.sender_id != 2
                          AND tm.team_id = 3
                THEN m.created_at ELSE NULL END)            AS primeira_msg_backoffice
        FROM instituto_experience.cw_messages_mat m
        LEFT JOIN instituto_experience.cw_team_members_mat tm
            ON m.sender_id = tm.user_id
        INNER JOIN (
            SELECT id FROM instituto_experience.cw_conversations_mat
            WHERE account_id = 1
        ) conv ON m.conversation_id = conv.id
        WHERE m.message_type IN (0, 1)
        GROUP BY m.conversation_id
    ),

    ia_antes_humano AS (
        SELECT
            m.conversation_id,
            MAX(m.created_at)                               AS ultima_ia_antes_humano
        FROM instituto_experience.cw_messages_mat m
        INNER JOIN (
            SELECT id FROM instituto_experience.cw_conversations_mat
            WHERE account_id = 1
        ) conv ON m.conversation_id = conv.id
        INNER JOIN (
            SELECT
                conversation_id,
                MIN(CASE WHEN sender_type = 'User' AND sender_id != 2
                    THEN created_at ELSE NULL END)          AS primeira_humana
            FROM instituto_experience.cw_messages_mat
            WHERE message_type IN (0, 1)
            GROUP BY conversation_id
        ) ref ON m.conversation_id = ref.conversation_id
              AND m.created_at < ref.primeira_humana
        WHERE m.message_type IN (0, 1)
          AND m.sender_type = 'User'
          AND m.sender_id = 2
        GROUP BY m.conversation_id
    )

    SELECT
        c.id                                                            AS conversation_id,
        c.display_id,
        CONCAT('https://chat.institutoexperience.com/app/accounts/1/conversations/',
            c.display_id)                                               AS url_conversa,
        DATE(CONVERT_TZ(c.created_at, '+00:00', '-03:00'))              AS data_criacao,
        CONVERT_TZ(c.created_at, '+00:00', '-03:00')                    AS created_at,
        c.team_id,
        CASE c.team_id
            WHEN 1 THEN 'SAC'
            WHEN 2 THEN 'Retenção'
            WHEN 3 THEN 'Back Office'
            WHEN 4 THEN 'Atendimento BR'
            WHEN 5 THEN 'Atendimento SMS'
            ELSE 'Não cadastrado'
        END                                                             AS nome_time,
        u.name                                                          AS assignee_name,
        CASE
            WHEN c.cached_label_list LIKE '%automacao-clickbank%'       THEN 'ClickBank'
            WHEN c.cached_label_list LIKE '%ia%'                        THEN 'IA'
            ELSE 'Orgânico'
        END                                                             AS categoria,
        CASE c.status
            WHEN 0 THEN 'open'
            WHEN 1 THEN 'resolved'
            WHEN 2 THEN 'pending'
            WHEN 3 THEN 'snoozed'
        END                                                             AS status_label,
        CONVERT_TZ(et.entrada_sac,        '+00:00', '-03:00')           AS entrada_sac,
        CONVERT_TZ(et.entrada_retencao,   '+00:00', '-03:00')           AS entrada_retencao,
        CONVERT_TZ(et.entrada_backoffice, '+00:00', '-03:00')           AS entrada_backoffice,
        CASE WHEN et.entrada_sac IS NOT NULL
                  AND msgs.primeira_msg_sac IS NOT NULL
                  AND msgs.primeira_msg_sac >= et.entrada_sac
            THEN TIMESTAMPDIFF(MINUTE, et.entrada_sac, msgs.primeira_msg_sac)
            ELSE NULL
        END                                                             AS sla_fila_sac_minutos,
        CASE WHEN et.entrada_retencao IS NOT NULL
                  AND msgs.primeira_msg_retencao IS NOT NULL
                  AND msgs.primeira_msg_retencao >= et.entrada_retencao
            THEN TIMESTAMPDIFF(MINUTE, et.entrada_retencao, msgs.primeira_msg_retencao)
            ELSE NULL
        END                                                             AS sla_fila_retencao_minutos,
        CASE WHEN et.entrada_backoffice IS NOT NULL
                  AND msgs.primeira_msg_backoffice IS NOT NULL
                  AND msgs.primeira_msg_backoffice >= et.entrada_backoffice
            THEN TIMESTAMPDIFF(MINUTE, et.entrada_backoffice, msgs.primeira_msg_backoffice)
            ELSE NULL
        END                                                             AS sla_fila_backoffice_minutos,
        CASE
            WHEN msgs.primeira_msg_sac IS NULL THEN NULL
            WHEN msgs.primeira_msg_ia IS NULL
                THEN TIMESTAMPDIFF(MINUTE, c.created_at, msgs.primeira_msg_sac)
            WHEN msgs.primeira_msg_sac <= msgs.primeira_msg_ia
                THEN TIMESTAMPDIFF(MINUTE, c.created_at, msgs.primeira_msg_sac)
            WHEN msgs.primeira_msg_sac > msgs.primeira_msg_ia
                 AND ia_antes_humano.ultima_ia_antes_humano IS NOT NULL
                THEN TIMESTAMPDIFF(MINUTE, ia_antes_humano.ultima_ia_antes_humano, msgs.primeira_msg_sac)
            ELSE NULL
        END                                                             AS frt_sac_minutos,
        CASE
            WHEN msgs.primeira_msg_retencao IS NULL THEN NULL
            WHEN et.entrada_retencao IS NULL THEN NULL
            WHEN msgs.primeira_msg_retencao < et.entrada_retencao THEN NULL
            WHEN msgs.primeira_msg_ia IS NULL
                THEN TIMESTAMPDIFF(MINUTE, et.entrada_retencao, msgs.primeira_msg_retencao)
            WHEN msgs.primeira_msg_retencao <= msgs.primeira_msg_ia
                THEN TIMESTAMPDIFF(MINUTE, et.entrada_retencao, msgs.primeira_msg_retencao)
            WHEN msgs.primeira_msg_retencao > msgs.primeira_msg_ia
                 AND ia_antes_humano.ultima_ia_antes_humano IS NOT NULL
                 AND ia_antes_humano.ultima_ia_antes_humano >= et.entrada_retencao
                THEN TIMESTAMPDIFF(MINUTE, ia_antes_humano.ultima_ia_antes_humano, msgs.primeira_msg_retencao)
            ELSE TIMESTAMPDIFF(MINUTE, et.entrada_retencao, msgs.primeira_msg_retencao)
        END                                                             AS frt_retencao_minutos,
        CASE
            WHEN msgs.primeira_msg_backoffice IS NULL THEN NULL
            WHEN et.entrada_backoffice IS NULL THEN NULL
            WHEN msgs.primeira_msg_backoffice < et.entrada_backoffice THEN NULL
            WHEN msgs.primeira_msg_ia IS NULL
                THEN TIMESTAMPDIFF(MINUTE, et.entrada_backoffice, msgs.primeira_msg_backoffice)
            WHEN msgs.primeira_msg_backoffice <= msgs.primeira_msg_ia
                THEN TIMESTAMPDIFF(MINUTE, et.entrada_backoffice, msgs.primeira_msg_backoffice)
            WHEN msgs.primeira_msg_backoffice > msgs.primeira_msg_ia
                 AND ia_antes_humano.ultima_ia_antes_humano IS NOT NULL
                 AND ia_antes_humano.ultima_ia_antes_humano >= et.entrada_backoffice
                THEN TIMESTAMPDIFF(MINUTE, ia_antes_humano.ultima_ia_antes_humano, msgs.primeira_msg_backoffice)
            ELSE TIMESTAMPDIFF(MINUTE, et.entrada_backoffice, msgs.primeira_msg_backoffice)
        END                                                             AS frt_backoffice_minutos,
        nrt.nrt_sac_minutos,
        nrt.nrt_retencao_minutos,
        nrt.nrt_backoffice_minutos,
        nrt.nrt_global_minutos

    FROM (
        SELECT * FROM instituto_experience.cw_conversations_mat
        WHERE account_id = 1
    ) c
    LEFT JOIN instituto_experience.cw_users_mat u
        ON c.assignee_id = u.id
    LEFT JOIN entradas_time et
        ON c.id = et.conversation_id
    LEFT JOIN msgs
        ON c.id = msgs.conversation_id
    LEFT JOIN ia_antes_humano
        ON c.id = ia_antes_humano.conversation_id
    LEFT JOIN nrt_agregado nrt
        ON c.id = nrt.conversation_id;

    -- 3. Troca atômica
    RENAME TABLE
        instituto_experience.dashboard_sla_times       TO instituto_experience.dashboard_sla_times_old,
        instituto_experience.dashboard_sla_times_stage TO instituto_experience.dashboard_sla_times,
        instituto_experience.dashboard_sla_times_old   TO instituto_experience.dashboard_sla_times_stage;

END
```
