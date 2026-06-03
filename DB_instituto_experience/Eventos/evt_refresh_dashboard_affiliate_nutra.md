---
tipo: evento
definer: "tadeu_lopes@%"
status: "DISABLED"
intervalo: "10"
unidade: "MINUTE"
ultima_execucao: "2026-06-02 22:20:14"
execucoes: 1036
tags: [evento]
---

# evt_refresh_dashboard_affiliate_nutra

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 10 MINUTE |
| Início | 2026-03-03 12:50:14 |
| Última execução | 2026-06-02 22:20:14 |

## Dispara
[[refresh_dashboard_affiliate_nutra]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[refresh_dashboard_affiliate_nutra]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 1,036 |
| Tempo médio | 20.7 s |
| Tempo máx | 8m19s |
| Tempo total | 5h57m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 0 |

## Corpo SQL

```sql
CALL instituto_experience.refresh_dashboard_affiliate_nutra()
```
