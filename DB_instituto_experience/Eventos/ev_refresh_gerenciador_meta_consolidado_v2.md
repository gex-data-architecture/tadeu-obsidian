---
tipo: evento
definer: "tadeu_lopes@%"
status: "DISABLED"
intervalo: "15"
unidade: "MINUTE"
ultima_execucao: "2026-04-08 01:14:55"
execucoes: ""
tags: [evento]
---

# ev_refresh_gerenciador_meta_consolidado_v2

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 15 MINUTE |
| Início | 2026-04-02 22:29:55 |
| Última execução | 2026-04-08 01:14:55 |

## Dispara
[[refresh_gerenciador_meta_consolidado_v2]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[refresh_gerenciador_meta_consolidado_v2]]

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
CALL instituto_experience.refresh_gerenciador_meta_consolidado_v2()
```
