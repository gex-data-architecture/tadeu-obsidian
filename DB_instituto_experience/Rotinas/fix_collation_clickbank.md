---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-01 16:47:13"
alterada_em: "2026-05-01 16:47:13"
execucoes: 183
tags: [rotina, procedure]
---

# fix_collation_clickbank

## Dependências

- **Lê:** —
- **Escreve:** —
- **Cria:** —
- **Trunca:** —
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 183 |
| Tempo médio | 684 ms |
| Tempo máx | 1m35s |
| Tempo total | 2m5s |
| Erros | 1 |
| Warnings | 0 |
| Linhas afetadas (total) | 0 |

## Corpo SQL

```sql
BEGIN
    ALTER TABLE instituto_experience.clickbank_physical_new_aws 
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
END
```
