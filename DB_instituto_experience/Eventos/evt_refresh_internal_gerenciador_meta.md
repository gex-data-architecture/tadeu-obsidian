---
tipo: evento
definer: "root@%"
status: "DISABLED"
intervalo: "5"
unidade: "MINUTE"
ultima_execucao: "2026-02-16 18:03:26"
execucoes: ""
tags: [evento]
---

# evt_refresh_internal_gerenciador_meta

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 5 MINUTE |
| Início | 2026-01-16 16:28:26 |
| Última execução | 2026-02-16 18:03:26 |

## Dispara
[[sp_refresh_internal_gerenciador_meta]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[sp_refresh_internal_gerenciador_meta]]

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
CALL instituto_experience.sp_refresh_internal_gerenciador_meta()
```
