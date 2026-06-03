---
tipo: evento
definer: "gabriel_gomes@%"
status: "ENABLED"
intervalo: "1"
unidade: "HOUR"
ultima_execucao: "2026-06-03 15:40:03"
execucoes: 190
tags: [evento]
---

# atualiza_funil_mapping

## Agenda

| Propriedade | Valor |
|---|---|
| Status | ENABLED |
| Tipo | RECURRING |
| Intervalo | 1 HOUR |
| Início | 2025-11-08 16:40:03 |
| Última execução | 2026-06-03 15:40:03 |

## Dispara
—

## Dependências

- **Lê:** [[cartpanda_physical]]
- **Escreve:** [[funil_produto_mapping]]
- **Trunca:** [[funil_produto_mapping]]
- **Chama:** —

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 190 |
| Tempo médio | 1.7 s |
| Tempo máx | 3.2 s |
| Tempo total | 5m25s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 11,210 |

## Corpo SQL

```sql
BEGIN
        -- Limpar e repopular a tabela
        TRUNCATE TABLE funil_produto_mapping;

        INSERT INTO funil_produto_mapping (funil_id, clean_product_name)
        SELECT
            funil_id,
            MAX(clean_product_name) as clean_product_name
        FROM (
                 SELECT
                     CONCAT('Funil de Nova Ideia #',
                            SUBSTRING_INDEX(REGEXP_SUBSTR(SUBSTRING_INDEX(offer_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'), ' ', 1)
                     ) AS funil_id,
                     TRIM(CASE
                              WHEN product_name LIKE '%-%' THEN TRIM(SUBSTRING_INDEX(product_name, '-', 1))
                              WHEN product_name REGEXP '[0-9]' THEN TRIM(REGEXP_SUBSTR(product_name, '^[^0-9]+'))
                              ELSE product_name
                         END) AS clean_product_name
                 FROM instituto_experience.cartpanda_physical
                 WHERE offer_name LIKE '%Nova Ideia%'
                   AND created_at_date >= '2025-09-01'
                   AND payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
                   AND (affiliate_name IS NULL OR affiliate_name = '')
                   AND NOT (client_email LIKE '%institutoexperience%')
                   AND NOT (LOWER(offer_name) LIKE '%affiliate marketing%')
             ) t
        WHERE funil_id IS NOT NULL
          AND clean_product_name IS NOT NULL
        GROUP BY funil_id;
    END
```
