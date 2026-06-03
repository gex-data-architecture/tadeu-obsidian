---
tipo: evento
definer: "root@%"
status: "ENABLED"
intervalo: "10"
unidade: "MINUTE"
ultima_execucao: "2026-06-03 16:24:13"
execucoes: 1145
tags: [evento]
---

# ev_preenche_valores_financeiros

## Agenda

| Propriedade | Valor |
|---|---|
| Status | ENABLED |
| Tipo | RECURRING |
| Intervalo | 10 MINUTE |
| Início | 2026-04-02 16:44:12 |
| Última execução | 2026-06-03 16:24:13 |

## Dispara
[[sp_preenche_valores_financeiros]]

## Dependências

- **Lê:** —
- **Escreve:** —
- **Trunca:** —
- **Chama:** [[sp_preenche_valores_financeiros]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 1,145 |
| Tempo médio | 9.6 s |
| Tempo máx | 5m25s |
| Tempo total | 3h4m |
| Erros | 1 |
| Warnings | 0 |
| Linhas afetadas (total) | 4,983 |

## Corpo SQL

```sql
CALL sp_preenche_valores_financeiros()
```
