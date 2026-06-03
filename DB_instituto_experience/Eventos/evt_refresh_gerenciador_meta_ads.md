---
tipo: evento
definer: "tadeu_lopes@%"
status: "DISABLED"
intervalo: "10"
unidade: "MINUTE"
ultima_execucao: "2026-04-08 00:52:46"
execucoes: ""
tags: [evento]
---

# evt_refresh_gerenciador_meta_ads

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 10 MINUTE |
| Início | 2026-02-16 18:02:46 |
| Última execução | 2026-04-08 00:52:46 |

## Dispara
[[sp_refresh_gerenciador_meta_ads]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[sp_refresh_gerenciador_meta_ads]]

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
CALL `instituto_experience`.`sp_refresh_gerenciador_meta_ads`()
```
