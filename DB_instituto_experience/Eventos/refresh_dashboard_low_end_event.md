---
tipo: evento
definer: "gabriel_gomes@%"
status: "ENABLED"
intervalo: "5"
unidade: "MINUTE"
ultima_execucao: "2026-06-03 16:26:32"
execucoes: 2289
tags: [evento]
---

# refresh_dashboard_low_end_event

## Agenda

| Propriedade | Valor |
|---|---|
| Status | ENABLED |
| Tipo | RECURRING |
| Intervalo | 5 MINUTE |
| Início | 2025-11-27 13:01:32 |
| Última execução | 2026-06-03 16:26:32 |

## Dispara
[[refresh_dashboard_low_end]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[refresh_dashboard_low_end]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 2,289 |
| Tempo médio | 9.0 s |
| Tempo máx | 17m24s |
| Tempo total | 5h43m |
| Erros | 30 |
| Warnings | 2,313,216 |
| Linhas afetadas (total) | 16,230,732 |

## Corpo SQL

```sql
CALL refresh_dashboard_low_end()
```
