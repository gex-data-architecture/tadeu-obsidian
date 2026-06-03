---
tipo: evento
definer: "tadeu_lopes@%"
status: "ENABLED"
intervalo: "60"
unidade: "MINUTE"
ultima_execucao: "2026-06-03 16:01:29"
execucoes: 190
tags: [evento]
---

# ev_master_dashboard_refresh

## Agenda

| Propriedade | Valor |
|---|---|
| Status | ENABLED |
| Tipo | RECURRING |
| Intervalo | 60 MINUTE |
| Início | 2026-05-22 19:01:29 |
| Última execução | 2026-06-03 16:01:29 |

## Dispara
[[sp_master_run_all]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 190 |
| Tempo médio | 35m17s |
| Tempo máx | 2h4m |
| Tempo total | 111h43m |
| Erros | 3 |
| Warnings | 0 |
| Linhas afetadas (total) | 0 |

## Corpo SQL

```sql
CALL sp_master_run_all()
```
