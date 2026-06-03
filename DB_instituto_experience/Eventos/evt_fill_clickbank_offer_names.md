---
tipo: evento
definer: "tadeu_lopes@%"
status: "ENABLED"
intervalo: "60"
unidade: "MINUTE"
ultima_execucao: "2026-06-03 15:43:11"
execucoes: 281
tags: [evento]
---

# evt_fill_clickbank_offer_names

## Agenda

| Propriedade | Valor |
|---|---|
| Status | ENABLED |
| Tipo | RECURRING |
| Intervalo | 60 MINUTE |
| Início | 2026-05-27 11:43:11 |
| Última execução | 2026-06-03 15:43:11 |

## Dispara
[[fill_clickbank_offer_names]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[fill_clickbank_offer_names]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 281 |
| Tempo médio | 4.2 s |
| Tempo máx | 2m55s |
| Tempo total | 19m42s |
| Erros | 1 |
| Warnings | 0 |
| Linhas afetadas (total) | 0 |

## Corpo SQL

```sql
CALL instituto_experience.fill_clickbank_offer_names()
```
