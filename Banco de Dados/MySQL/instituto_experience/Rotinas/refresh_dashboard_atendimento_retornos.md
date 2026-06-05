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

# refresh_dashboard_atendimento_retornos

## Dependências

- **Lê:** [[cw_conversations_mat]], [[cw_messages_mat]]
- **Escreve:** [[dashboard_atendimento_retornos_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_atendimento_retornos_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 179 |
| Tempo médio | 5.5 s |
| Tempo máx | 15.4 s |
| Tempo total | 16m16s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 158,964 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_atendimento_retornos_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_atendimento_retornos_stage;

    -- 2. Insere na stage
    INSERT INTO instituto_experience.dashboard_atendimento_retornos_stage
    SELECT
        data,
        categoria,
        SUM(novas_conversas) AS novas_conversas,
        SUM(retornos)        AS retornos
    FROM (

        SELECT
            DATE(CONVERT_TZ(c.created_at, '+00:00', '-03:00')) AS data,
            CASE
                WHEN c.cached_label_list LIKE '%automacao-clickbank%' THEN 'ClickBank'
                WHEN c.cached_label_list LIKE '%ia%'                  THEN 'IA'
                ELSE 'Orgânico'
            END AS categoria,
            1 AS novas_conversas,
            0 AS retornos
        FROM instituto_experience.cw_conversations_mat c
        WHERE c.account_id = 1
        GROUP BY DATE(CONVERT_TZ(c.created_at, '+00:00', '-03:00')), c.id, c.cached_label_list

        UNION ALL

        SELECT
            DATE(CONVERT_TZ(m.created_at, '+00:00', '-03:00')) AS data,
            CASE
                WHEN c.cached_label_list LIKE '%automacao-clickbank%' THEN 'ClickBank'
                WHEN c.cached_label_list LIKE '%ia%'                  THEN 'IA'
                ELSE 'Orgânico'
            END AS categoria,
            0 AS novas_conversas,
            1 AS retornos
        FROM instituto_experience.cw_messages_mat m
        INNER JOIN instituto_experience.cw_conversations_mat c
            ON m.conversation_id = c.id
        WHERE c.account_id = 1
          AND m.sender_type  = 'Contact'
          AND m.message_type IN (0, 1)
          AND DATE(CONVERT_TZ(m.created_at, '+00:00', '-03:00')) > DATE(CONVERT_TZ(c.created_at, '+00:00', '-03:00'))
        GROUP BY DATE(CONVERT_TZ(m.created_at, '+00:00', '-03:00')), m.conversation_id, c.cached_label_list

    ) t
    GROUP BY data, categoria
    ORDER BY data, categoria;

    -- 3. Troca atômica
    RENAME TABLE
        instituto_experience.dashboard_atendimento_retornos       TO instituto_experience.dashboard_atendimento_retornos_old,
        instituto_experience.dashboard_atendimento_retornos_stage TO instituto_experience.dashboard_atendimento_retornos,
        instituto_experience.dashboard_atendimento_retornos_old   TO instituto_experience.dashboard_atendimento_retornos_stage;

END
```
