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

# refresh_dashboard_atendimento

## Dependências

- **Lê:** [[cw_conversations_mat]], [[cw_messages_mat]], [[cw_teams_mat]], [[cw_users_mat]]
- **Escreve:** [[dashboard_atendimento_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_atendimento_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 179 |
| Tempo médio | 1m11s |
| Tempo máx | 2m48s |
| Tempo total | 3h31m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 95,359,362 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_atendimento_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_atendimento_stage;

    -- 2. Insere na stage
    INSERT INTO instituto_experience.dashboard_atendimento_stage
    WITH

    nrt_msgs AS (
        SELECT
            c_msg.conversation_id,
            c_msg.created_at                                AS msg_cliente_at,
            MIN(a_msg.created_at)                           AS proxima_msg_agente_at
        FROM instituto_experience.cw_messages_mat c_msg
        INNER JOIN (
            SELECT id FROM instituto_experience.cw_conversations_mat WHERE account_id = 1
        ) conv ON c_msg.conversation_id = conv.id
        INNER JOIN instituto_experience.cw_messages_mat a_msg
            ON  c_msg.conversation_id = a_msg.conversation_id
            AND a_msg.created_at > c_msg.created_at
            AND a_msg.sender_type = 'User'
            AND a_msg.message_type IN (0, 1)
        WHERE c_msg.message_type IN (0, 1)
          AND c_msg.sender_type = 'Contact'
        GROUP BY c_msg.conversation_id, c_msg.created_at
    ),

    nrt_agregado AS (
        SELECT
            conversation_id,
            AVG(TIMESTAMPDIFF(MINUTE, msg_cliente_at, proxima_msg_agente_at)) AS nrt_minutos
        FROM nrt_msgs
        GROUP BY conversation_id
    )

    SELECT
        c.id AS conversation_id,
        c.display_id,
        CONCAT('https://chat.institutoexperience.com/app/accounts/1/conversations/', c.display_id) AS url_conversa,
        c.status,
        CASE c.status
            WHEN 0 THEN 'open'
            WHEN 1 THEN 'resolved'
            WHEN 2 THEN 'pending'
            WHEN 3 THEN 'snoozed'
        END AS status_label,
        CONVERT_TZ(c.created_at,             '+00:00', '-03:00') AS created_at,
        CONVERT_TZ(c.updated_at,             '+00:00', '-03:00') AS updated_at,
        CONVERT_TZ(c.first_reply_created_at, '+00:00', '-03:00') AS first_reply_created_at,
        CONVERT_TZ(c.waiting_since,          '+00:00', '-03:00') AS waiting_since,
        DATE(CONVERT_TZ(c.created_at,        '+00:00', '-03:00')) AS data_criacao,
        DAYOFWEEK(CONVERT_TZ(c.created_at,   '+00:00', '-03:00')) AS dia_semana_num,
        CASE DAYOFWEEK(CONVERT_TZ(c.created_at, '+00:00', '-03:00'))
            WHEN 1 THEN 'Domingo'
            WHEN 2 THEN 'Segunda'
            WHEN 3 THEN 'Terça'
            WHEN 4 THEN 'Quarta'
            WHEN 5 THEN 'Quinta'
            WHEN 6 THEN 'Sexta'
            WHEN 7 THEN 'Sábado'
        END AS dia_semana,
        HOUR(CONVERT_TZ(c.created_at, '+00:00', '-03:00')) AS hora_abertura,
        c.team_id,
        t.name AS team_name,
        CASE
            WHEN t.name LIKE '%sac%'         THEN 'SAC'
            WHEN t.name LIKE '%retenção%'    THEN 'Retenção'
            WHEN t.name LIKE '%back office%' THEN 'Back Office'
            WHEN t.name LIKE '%brasil%'      THEN 'Atendimento BR'
            WHEN t.name IS NULL              THEN 'Não cadastrado'
            ELSE t.name
        END AS nome_time,
        c.assignee_id,
        u.name AS assignee_name,
        c.cached_label_list,
        CASE
            WHEN c.cached_label_list LIKE '%automacao-clickbank%' THEN 'ClickBank'
            WHEN c.cached_label_list LIKE '%ia%'                 THEN 'IA'
            ELSE 'Orgânico'
        END AS categoria,
        c.priority,
        CASE WHEN c.status = 0 THEN 1 ELSE 0 END AS is_open,
        CASE WHEN c.status = 1 THEN 1 ELSE 0 END AS is_resolved,
        CASE WHEN c.status = 2 THEN 1 ELSE 0 END AS is_pending,
        CASE WHEN c.status = 3 THEN 1 ELSE 0 END AS is_snoozed,
        CASE WHEN c.status = 0
                  AND c.cached_label_list NOT LIKE '%automacao-clickbank%'
                  AND c.cached_label_list NOT LIKE '%ia%'
             THEN 1 ELSE 0 END AS is_backlog_organico,
        CASE WHEN c.status = 0
                  AND c.cached_label_list LIKE '%automacao-clickbank%'
             THEN 1 ELSE 0 END AS is_backlog_clickbank,

        -- FRT
        CASE
            WHEN msg.primeira_msg_ia IS NULL
                 AND msg.primeira_msg_agente IS NOT NULL
            THEN TIMESTAMPDIFF(MINUTE, c.created_at, msg.primeira_msg_agente)
            WHEN msg.primeira_msg_ia IS NOT NULL
                 AND msg.primeira_msg_agente IS NOT NULL
                 AND msg.primeira_msg_agente <= msg.primeira_msg_ia
            THEN TIMESTAMPDIFF(MINUTE, c.created_at, msg.primeira_msg_agente)
            WHEN msg.primeira_msg_ia IS NOT NULL
                 AND msg.primeira_msg_agente IS NOT NULL
                 AND msg.primeira_msg_agente > msg.primeira_msg_ia
                 AND ia_antes_humano.ultima_ia_antes_humano IS NOT NULL
            THEN TIMESTAMPDIFF(MINUTE,
                    ia_antes_humano.ultima_ia_antes_humano,
                    msg.primeira_msg_agente)
            ELSE NULL
        END AS frt_minutos,

        -- FRT handoff IA → humano
        CASE
            WHEN c.cached_label_list LIKE '%ia%'
                 AND ultima_ia.ultima_msg_ia IS NOT NULL
                 AND primeira_humana.primeira_msg_humano_pos_ia IS NOT NULL
            THEN TIMESTAMPDIFF(MINUTE, ultima_ia.ultima_msg_ia, primeira_humana.primeira_msg_humano_pos_ia)
            ELSE NULL
        END AS frt_handoff_minutos,

        -- NRT
        nrt.nrt_minutos,

        -- Contagem de mensagens
        msg.total_mensagens,
        msg.mensagens_ia,
        msg.mensagens_humano,
        msg.mensagens_cliente,
        CONVERT_TZ(msg.ultimo_retorno_cliente, '+00:00', '-03:00') AS ultimo_retorno_cliente,
        DATE(CONVERT_TZ(msg.ultimo_retorno_cliente, '+00:00', '-03:00')) AS data_retorno_cliente,
        CASE WHEN msg.ultimo_retorno_cliente > msg.primeira_msg_agente
             THEN 1 ELSE 0 END AS is_retorno

    FROM (
        SELECT * FROM instituto_experience.cw_conversations_mat
        WHERE account_id = 1
    ) c
    LEFT JOIN instituto_experience.cw_teams_mat t
        ON c.team_id = t.id
    LEFT JOIN instituto_experience.cw_users_mat u
        ON c.assignee_id = u.id
    LEFT JOIN (
        SELECT
            m.conversation_id,
            COUNT(*)                                                        AS total_mensagens,
            SUM(CASE WHEN m.sender_type = 'User' AND m.sender_id = 2
                THEN 1 ELSE 0 END)                                          AS mensagens_ia,
            SUM(CASE WHEN m.sender_type = 'User' AND m.sender_id != 2
                THEN 1 ELSE 0 END)                                          AS mensagens_humano,
            SUM(CASE WHEN m.sender_type = 'Contact'
                THEN 1 ELSE 0 END)                                          AS mensagens_cliente,
            MAX(CASE WHEN m.sender_type = 'Contact'
                THEN m.created_at ELSE NULL END)                            AS ultimo_retorno_cliente,
            MIN(CASE WHEN m.sender_type = 'User' AND m.sender_id != 2
                THEN m.created_at ELSE NULL END)                            AS primeira_msg_agente,
            MIN(CASE WHEN m.sender_type = 'User' AND m.sender_id = 2
                THEN m.created_at ELSE NULL END)                            AS primeira_msg_ia
        FROM instituto_experience.cw_messages_mat m
        INNER JOIN (
            SELECT id FROM instituto_experience.cw_conversations_mat WHERE account_id = 1
        ) conv ON m.conversation_id = conv.id
        WHERE m.message_type IN (0, 1)
        GROUP BY m.conversation_id
    ) msg ON c.id = msg.conversation_id

    LEFT JOIN (
        SELECT
            m.conversation_id,
            MAX(m.created_at) AS ultima_ia_antes_humano
        FROM instituto_experience.cw_messages_mat m
        INNER JOIN (
            SELECT id FROM instituto_experience.cw_conversations_mat WHERE account_id = 1
        ) conv ON m.conversation_id = conv.id
        INNER JOIN (
            SELECT conversation_id,
                   MIN(CASE WHEN sender_type = 'User' AND sender_id != 2
                       THEN created_at ELSE NULL END) AS primeira_humana
            FROM instituto_experience.cw_messages_mat
            WHERE message_type IN (0, 1)
            GROUP BY conversation_id
        ) ref ON m.conversation_id = ref.conversation_id
              AND m.created_at < ref.primeira_humana
        WHERE m.message_type IN (0, 1)
          AND m.sender_type = 'User'
          AND m.sender_id = 2
        GROUP BY m.conversation_id
    ) ia_antes_humano ON c.id = ia_antes_humano.conversation_id

    LEFT JOIN (
        SELECT
            conversation_id,
            MAX(CASE WHEN sender_id = 2 THEN created_at ELSE NULL END) AS ultima_msg_ia
        FROM instituto_experience.cw_messages_mat
        INNER JOIN (
            SELECT id FROM instituto_experience.cw_conversations_mat WHERE account_id = 1
        ) conv ON conversation_id = conv.id
        WHERE message_type IN (0, 1)
        GROUP BY conversation_id
    ) ultima_ia ON c.id = ultima_ia.conversation_id

    LEFT JOIN (
        SELECT
            m.conversation_id,
            MIN(m.created_at) AS primeira_msg_humano_pos_ia
        FROM instituto_experience.cw_messages_mat m
        INNER JOIN (
            SELECT id FROM instituto_experience.cw_conversations_mat WHERE account_id = 1
        ) conv ON m.conversation_id = conv.id
        INNER JOIN (
            SELECT
                conversation_id,
                MAX(CASE WHEN sender_id = 2 THEN created_at ELSE NULL END) AS ultima_ia
            FROM instituto_experience.cw_messages_mat
            WHERE message_type IN (0, 1)
            GROUP BY conversation_id
        ) ref ON m.conversation_id = ref.conversation_id
              AND m.created_at > ref.ultima_ia
        WHERE m.message_type IN (0, 1)
          AND m.sender_type = 'User'
          AND m.sender_id != 2
        GROUP BY m.conversation_id
    ) primeira_humana ON c.id = primeira_humana.conversation_id

    LEFT JOIN nrt_agregado nrt ON c.id = nrt.conversation_id;

    -- 3. Troca atômica
    RENAME TABLE
        instituto_experience.dashboard_atendimento       TO instituto_experience.dashboard_atendimento_old,
        instituto_experience.dashboard_atendimento_stage TO instituto_experience.dashboard_atendimento,
        instituto_experience.dashboard_atendimento_old   TO instituto_experience.dashboard_atendimento_stage;

END
```
