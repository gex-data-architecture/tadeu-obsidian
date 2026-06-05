---
tipo: evento
definer: "tadeu_lopes@%"
status: "DISABLED"
intervalo: "5"
unidade: "MINUTE"
ultima_execucao: "2026-04-08 01:23:43"
execucoes: ""
tags: [evento]
---

# ev_refresh_dashboard_gold_clickbank

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 5 MINUTE |
| Início | 2026-03-03 02:13:43 |
| Última execução | 2026-04-08 01:23:43 |

## Dispara
[[refresh_dashboard_gold_clickbank]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[refresh_dashboard_gold_clickbank]]

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
CALL refresh_dashboard_gold_clickbank
```
