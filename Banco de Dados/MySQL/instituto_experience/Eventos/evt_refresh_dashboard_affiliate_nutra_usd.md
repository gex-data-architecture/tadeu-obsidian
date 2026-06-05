---
tipo: evento
definer: "tadeu_lopes@%"
status: "DISABLED"
intervalo: "10"
unidade: "MINUTE"
ultima_execucao: "2026-06-02 22:23:16"
execucoes: 1037
tags: [evento]
---

# evt_refresh_dashboard_affiliate_nutra_usd

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 10 MINUTE |
| Início | 2026-03-03 18:33:16 |
| Última execução | 2026-06-02 22:23:16 |

## Dispara
[[refresh_dashboard_affiliate_nutra_usd]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[refresh_dashboard_affiliate_nutra_usd]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 1,037 |
| Tempo médio | 20.5 s |
| Tempo máx | 15m15s |
| Tempo total | 5h53m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 0 |

## Corpo SQL

```sql
CALL instituto_experience.refresh_dashboard_affiliate_nutra_usd()
```
