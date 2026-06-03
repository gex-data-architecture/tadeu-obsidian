---
tipo: evento
definer: "tadeu_lopes@%"
status: "DISABLED"
intervalo: "5"
unidade: "MINUTE"
ultima_execucao: "2026-04-08 01:25:20"
execucoes: ""
tags: [evento]
---

# ev_refresh_dashboard_leads_alerts

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 5 MINUTE |
| Início | 2026-02-19 13:35:20 |
| Última execução | 2026-04-08 01:25:20 |

## Dispara
[[refresh_dashboard_leads_alerts]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[refresh_dashboard_leads_alerts]]

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
CALL refresh_dashboard_leads_alerts()
```
