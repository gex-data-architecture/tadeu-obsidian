---
tipo: evento
definer: "tadeu_lopes@%"
status: "DISABLED"
intervalo: "5"
unidade: "MINUTE"
ultima_execucao: "2026-04-08 01:10:12"
execucoes: ""
tags: [evento]
---

# refresh_dashboard_sms_marketing_event

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 5 MINUTE |
| Início | 2025-12-19 13:05:12 |
| Última execução | 2026-04-08 01:10:12 |

## Dispara
[[refresh_dashboard_sms_marketing]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[refresh_dashboard_sms_marketing]]

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
CALL refresh_dashboard_sms_marketing()
```
