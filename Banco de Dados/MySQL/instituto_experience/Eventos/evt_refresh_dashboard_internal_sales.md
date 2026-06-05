---
tipo: evento
definer: "tadeu_lopes@%"
status: "DISABLED"
intervalo: "10"
unidade: "MINUTE"
ultima_execucao: "2026-04-08 01:01:28"
execucoes: ""
tags: [evento]
---

# evt_refresh_dashboard_internal_sales

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 10 MINUTE |
| Início | 2026-02-16 15:01:28 |
| Última execução | 2026-04-08 01:01:28 |

## Dispara
[[refresh_dashboard_internal_sales]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[refresh_dashboard_internal_sales]]

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
CALL `instituto_experience`.`refresh_dashboard_internal_sales`()
```
