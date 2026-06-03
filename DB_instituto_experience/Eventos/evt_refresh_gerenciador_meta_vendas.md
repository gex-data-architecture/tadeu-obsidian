---
tipo: evento
definer: "tadeu_lopes@%"
status: "DISABLED"
intervalo: "10"
unidade: "MINUTE"
ultima_execucao: "2026-04-08 00:57:48"
execucoes: ""
tags: [evento]
---

# evt_refresh_gerenciador_meta_vendas

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 10 MINUTE |
| Início | 2026-02-16 18:07:48 |
| Última execução | 2026-04-08 00:57:48 |

## Dispara
[[sp_refresh_gerenciador_meta_vendas]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[sp_refresh_gerenciador_meta_vendas]]

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
CALL `instituto_experience`.`sp_refresh_gerenciador_meta_vendas`()
```
