---
tipo: evento
definer: "tadeu_lopes@%"
status: "DISABLED"
intervalo: "15"
unidade: "MINUTE"
ultima_execucao: "2026-04-08 01:24:37"
execucoes: ""
tags: [evento]
---

# ev_refresh_custos_diarios

## Agenda

| Propriedade | Valor |
|---|---|
| Status | DISABLED |
| Tipo | RECURRING |
| Intervalo | 15 MINUTE |
| Início | 2026-03-25 16:54:37 |
| Última execução | 2026-04-08 01:24:37 |

## Dispara
[[atualizar_custos_conta_agencia_diaria]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[atualizar_custos_conta_agencia_diaria]], [[atualizar_custos_gerais_diaria]], [[atualizar_custos_trafego_diaria]]

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN
    CALL instituto_experience.atualizar_custos_trafego_diaria();
    CALL instituto_experience.atualizar_custos_conta_agencia_diaria();
    CALL instituto_experience.atualizar_custos_gerais_diaria();
END
```
