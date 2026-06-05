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

# atualizar_custos_trafego_diaria

## Dependências

- **Lê:** [[custos_trafego_gestores]]
- **Escreve:** [[custos_trafego_gestores_diaria_stage]]
- **Cria:** —
- **Trunca:** [[custos_trafego_gestores_diaria_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 189 ms |
| Tempo máx | 9.3 s |
| Tempo total | 34.4 s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 53,508 |

## Corpo SQL

```sql
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.custos_trafego_gestores_diaria_stage;
        RESIGNAL;
    END;
    TRUNCATE TABLE instituto_experience.custos_trafego_gestores_diaria_stage;
    INSERT INTO instituto_experience.custos_trafego_gestores_diaria_stage
        (data, fonte, produto, gestor, custo_usd, status)
    WITH RECURSIVE dias AS (
        SELECT 0 AS offset_dia
        UNION ALL
        SELECT offset_dia + 1 FROM dias WHERE offset_dia < 6
    )
    SELECT
        DATE_ADD(c.data_inicio, INTERVAL d.offset_dia DAY) AS data,
        c.fonte,
        c.produto,
        c.gestor,
        ROUND(c.custo_usd / 7, 2) AS custo_usd,
        c.status
    FROM instituto_experience.custos_trafego_gestores c
    CROSS JOIN dias d
    WHERE c.is_current = 1
    ORDER BY data, fonte, gestor, produto;
    RENAME TABLE
        instituto_experience.custos_trafego_gestores_diaria       TO instituto_experience.custos_trafego_gestores_diaria_old,
        instituto_experience.custos_trafego_gestores_diaria_stage TO instituto_experience.custos_trafego_gestores_diaria,
        instituto_experience.custos_trafego_gestores_diaria_old   TO instituto_experience.custos_trafego_gestores_diaria_stage;
END
```
