---
tipo: evento
definer: "root@%"
status: "DISABLED"
intervalo: "5"
unidade: "MINUTE"
ultima_execucao: "2026-02-16 15:27:53"
execucoes: ""
tags: [evento]
---

# refresh_internal_sales_event

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 5 MINUTE |
| Início | 2025-11-18 03:22:53 |
| Última execução | 2026-02-16 15:27:53 |

## Dispara
[[refresh_internal_sales]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[refresh_internal_sales]]

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
CALL refresh_internal_sales()
```
