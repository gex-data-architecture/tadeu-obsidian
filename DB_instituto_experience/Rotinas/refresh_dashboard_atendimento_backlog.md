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

# refresh_dashboard_atendimento_backlog

## Dependências

- **Lê:** [[dashboard_atendimento]]
- **Escreve:** [[dashboard_atendimento_backlog_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_atendimento_backlog_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 179 |
| Tempo médio | 1m6s |
| Tempo máx | 1m26s |
| Tempo total | 3h16m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 1,686,023 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_atendimento_backlog_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_atendimento_backlog_stage;

    -- 2. Insere na stage
    INSERT INTO instituto_experience.dashboard_atendimento_backlog_stage
    WITH RECURSIVE calendario AS (
        SELECT DATE(MIN(created_at)) AS dt
        FROM instituto_experience.dashboard_atendimento

        UNION ALL

        SELECT DATE_ADD(dt, INTERVAL 1 DAY)
        FROM calendario
        WHERE dt < CURDATE()
    )

    SELECT
        cal.dt             AS data_referencia,
        a.nome_time,
        a.categoria,
        CASE
            WHEN a.status_label = 'resolved' AND DATE(a.updated_at) = cal.dt THEN 'resolved'
            WHEN a.status_label = 'resolved' AND DATE(a.updated_at) > cal.dt THEN 'open'
            ELSE a.status_label
        END AS status_label,
        COUNT(*)           AS qtd_conversas
    FROM calendario cal
    INNER JOIN instituto_experience.dashboard_atendimento a
        ON a.data_criacao <= cal.dt
        AND (
            a.status_label != 'resolved'
            OR DATE(a.updated_at) >= cal.dt
        )
    GROUP BY
        cal.dt,
        a.nome_time,
        a.categoria,
        CASE
            WHEN a.status_label = 'resolved' AND DATE(a.updated_at) = cal.dt THEN 'resolved'
            WHEN a.status_label = 'resolved' AND DATE(a.updated_at) > cal.dt THEN 'open'
            ELSE a.status_label
        END
    ORDER BY
        cal.dt,
        a.nome_time,
        a.categoria,
        status_label;

    -- 3. Troca atômica
    RENAME TABLE
        instituto_experience.dashboard_atendimento_backlog       TO instituto_experience.dashboard_atendimento_backlog_old,
        instituto_experience.dashboard_atendimento_backlog_stage TO instituto_experience.dashboard_atendimento_backlog,
        instituto_experience.dashboard_atendimento_backlog_old   TO instituto_experience.dashboard_atendimento_backlog_stage;

END
```
