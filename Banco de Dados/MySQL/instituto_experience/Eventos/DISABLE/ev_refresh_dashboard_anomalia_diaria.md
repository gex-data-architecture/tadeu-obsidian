---
tipo: evento
definer: "tadeu_lopes@%"
status: "DISABLED"
intervalo: "15"
unidade: "MINUTE"
ultima_execucao: "2026-04-08 01:20:28"
execucoes: ""
tags: [evento]
---

# ev_refresh_dashboard_anomalia_diaria

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 15 MINUTE |
| Início | 2026-03-08 12:05:28 |
| Última execução | 2026-04-08 01:20:28 |

## Dispara
[[refresh_dashboard_anomalia_diaria]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[refresh_dashboard_anomalia_diaria]]

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
CALL refresh_dashboard_anomalia_diaria()
```
