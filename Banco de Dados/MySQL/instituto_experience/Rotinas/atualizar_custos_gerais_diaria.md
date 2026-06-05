---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-03-25 16:54:36"
alterada_em: "2026-03-25 16:54:36"
execucoes: 182
tags: [rotina, procedure]
---

# atualizar_custos_gerais_diaria

## Dependências

- **Lê:** [[custos_gerais]]
- **Escreve:** [[custos_gerais_diaria_stage]]
- **Cria:** —
- **Trunca:** [[custos_gerais_diaria_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 142 ms |
| Tempo máx | 5.5 s |
| Tempo total | 25.9 s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 27,300 |

## Corpo SQL

```sql
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.custos_gerais_diaria_stage;
        RESIGNAL;
    END;

    TRUNCATE TABLE instituto_experience.custos_gerais_diaria_stage;

    INSERT INTO instituto_experience.custos_gerais_diaria_stage
        (data, data_mes, fonte, gestor, custo, status)
    WITH RECURSIVE dias AS (
        SELECT 1 AS dia
        UNION ALL
        SELECT dia + 1 FROM dias WHERE dia < 30
    )
    SELECT
        DATE_ADD(c.data_mes, INTERVAL (d.dia - 1) DAY) AS data,
        c.data_mes,
        c.fonte,
        c.gestor,
        ROUND(c.custo / 30, 2) AS custo,
        c.status
    FROM instituto_experience.custos_gerais c
    CROSS JOIN dias d
    WHERE c.is_current = 1
    ORDER BY data, fonte, gestor;

    RENAME TABLE
        instituto_experience.custos_gerais_diaria       TO instituto_experience.custos_gerais_diaria_old,
        instituto_experience.custos_gerais_diaria_stage TO instituto_experience.custos_gerais_diaria,
        instituto_experience.custos_gerais_diaria_old   TO instituto_experience.custos_gerais_diaria_stage;
END
```
