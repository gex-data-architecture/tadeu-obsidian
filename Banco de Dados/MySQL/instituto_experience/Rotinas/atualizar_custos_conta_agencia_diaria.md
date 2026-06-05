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

# atualizar_custos_conta_agencia_diaria

## Dependências

- **Lê:** [[custos_conta_agencia]]
- **Escreve:** [[custos_conta_agencia_diaria_stage]]
- **Cria:** —
- **Trunca:** [[custos_conta_agencia_diaria_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 144 ms |
| Tempo máx | 1.3 s |
| Tempo total | 26.3 s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 50,960 |

## Corpo SQL

```sql
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.custos_conta_agencia_diaria_stage;
        RESIGNAL;
    END;
    TRUNCATE TABLE instituto_experience.custos_conta_agencia_diaria_stage;
    INSERT INTO instituto_experience.custos_conta_agencia_diaria_stage
        (data, fonte, agencia, produto, gestor, taxa, custo, custo_real, status)
    WITH RECURSIVE dias AS (
        SELECT 0 AS offset_dia
        UNION ALL
        SELECT offset_dia + 1 FROM dias WHERE offset_dia < 6
    )
    SELECT
        DATE_ADD(c.data_inicio, INTERVAL d.offset_dia DAY) AS data,
        c.fonte,
        c.agencia,
        c.produto,
        c.gestor,
        c.taxa,
        ROUND(c.custo      / 7, 2) AS custo,
        ROUND(c.custo_real / 7, 2) AS custo_real,
        c.status
    FROM instituto_experience.custos_conta_agencia c
    CROSS JOIN dias d
    WHERE c.is_current = 1
    ORDER BY data, fonte, gestor, produto;
    RENAME TABLE
        instituto_experience.custos_conta_agencia_diaria       TO instituto_experience.custos_conta_agencia_diaria_old,
        instituto_experience.custos_conta_agencia_diaria_stage TO instituto_experience.custos_conta_agencia_diaria,
        instituto_experience.custos_conta_agencia_diaria_old   TO instituto_experience.custos_conta_agencia_diaria_stage;
END
```
