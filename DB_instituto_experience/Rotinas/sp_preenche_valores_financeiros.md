---
tipo: procedure
definer: "root@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-04-02 16:49:09"
alterada_em: "2026-04-02 16:49:09"
execucoes: 1145
tags: [rotina, procedure]
---

# sp_preenche_valores_financeiros

## Dependências

- **Lê:** [[clickbank_physical_new]]
- **Escreve:** [[cb_tickets]]
- **Cria:** —
- **Trunca:** —
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 1,145 |
| Tempo médio | 9.6 s |
| Tempo máx | 5m20s |
| Tempo total | 3h2m |
| Erros | 1 |
| Warnings | 0 |
| Linhas afetadas (total) | 10,184 |

## Corpo SQL

```sql
BEGIN
    -- UPDATE 1: Preenche sale_amount + product_name (só tickets novos)
    UPDATE cb_tickets t
        JOIN clickbank_physical_new p_main
        ON p_main.transaction_id COLLATE utf8mb4_unicode_ci = t.receipt COLLATE utf8mb4_unicode_ci
        JOIN (
            SELECT
                CASE
                    WHEN transaction_id LIKE '%-b%'
                        THEN LEFT(transaction_id, LOCATE('-b', transaction_id) - 1)
                    ELSE transaction_id
                    END AS base_receipt,
                SUM(total_price_usd) AS total_price,
                SUM(COALESCE(total_refund_usd, 0)) AS total_refund
            FROM clickbank_physical_new
            GROUP BY base_receipt
        ) p_total ON p_total.base_receipt COLLATE utf8mb4_unicode_ci = t.receipt COLLATE utf8mb4_unicode_ci
    SET t.sale_amount = p_total.total_price,
        t.refund_negotiated = CASE
                                  WHEN p_total.total_refund != 0 THEN p_total.total_refund
                                  ELSE t.refund_negotiated
            END,
        t.product_name = CASE
                             WHEN t.product_name IS NULL THEN p_main.product_name
                             ELSE t.product_name
            END,
        t.product_item_no = CASE
                                WHEN t.product_name IS NULL THEN p_main.product_sku
                                ELSE t.product_item_no
            END
    WHERE t.sale_amount IS NULL
      AND t.receipt IS NOT NULL;

    -- UPDATE 2: Atualiza refund_negotiated (tickets que já têm sale_amount mas refund mudou)
    UPDATE cb_tickets t
        JOIN (
            SELECT
                CASE
                    WHEN transaction_id LIKE '%-b%'
                        THEN LEFT(transaction_id, LOCATE('-b', transaction_id) - 1)
                    ELSE transaction_id
                    END AS base_receipt,
                SUM(COALESCE(total_refund_usd, 0)) AS total_refund
            FROM clickbank_physical_new
            GROUP BY base_receipt
        ) p_total ON p_total.base_receipt COLLATE utf8mb4_unicode_ci = t.receipt COLLATE utf8mb4_unicode_ci
    SET t.refund_negotiated = p_total.total_refund
    WHERE t.sale_amount IS NOT NULL
      AND t.receipt IS NOT NULL
      AND p_total.total_refund != 0
      AND (t.refund_negotiated IS NULL OR t.refund_negotiated != p_total.total_refund);
END
```
