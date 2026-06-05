---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-26 18:45:58"
alterada_em: "2026-05-26 18:45:58"
execucoes: 1
tags: [rotina, procedure]
---

# refresh_dashboard_gold_clickbank_teste

## Dependências

- **Lê:** [[clickbank_physical_new_aws]]
- **Escreve:** [[dashboard_gold_clickbank_stage_new]]
- **Cria:** [[dashboard_gold_clickbank_stage_new]], `tmp_base`, `tmp_classificado`, `tmp_flag_grupo`, `tmp_grupo_id`, `tmp_grupo_id_final`, `tmp_main_por_grupo`, `tmp_ordenado`
- **Trunca:** —
- **Dropa:** [[dashboard_gold_clickbank_stage_new]]
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 1 |
| Tempo médio | 1m16s |
| Tempo máx | 1m16s |
| Tempo total | 1m16s |
| Erros | 2 |
| Warnings | 0 |
| Linhas afetadas (total) | 4,352,654 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        DROP TEMPORARY TABLE IF EXISTS tmp_base;
        DROP TEMPORARY TABLE IF EXISTS tmp_ordenado;
        DROP TEMPORARY TABLE IF EXISTS tmp_flag_grupo;
        DROP TEMPORARY TABLE IF EXISTS tmp_grupo_id;
        DROP TEMPORARY TABLE IF EXISTS tmp_grupo_id_final;
        DROP TEMPORARY TABLE IF EXISTS tmp_classificado;
        DROP TEMPORARY TABLE IF EXISTS tmp_main_por_grupo;

        RESIGNAL;
    END;

    SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

    DROP TABLE IF EXISTS instituto_experience.dashboard_gold_clickbank_stage_new;

    CREATE TABLE instituto_experience.dashboard_gold_clickbank_stage_new
    LIKE instituto_experience.dashboard_gold_clickbank;

    /* =========================================================
       BASE
    ========================================================= */

    CREATE TEMPORARY TABLE tmp_base AS
    SELECT
        cb.*,
        TIMESTAMP(CONCAT(cb.created_at_date,' ',cb.created_at_hour)) AS created_at_ts,
        LOWER(cb.sales_type) AS sales_type_lower,
        LOWER(cb.offer_name) AS offer_name_lower
    FROM instituto_experience.clickbank_physical_new_aws cb
    WHERE cb.created_at_date >= '2026-01-01'
       OR cb.created_at_date IS NULL;

    CREATE INDEX idx_tmp_base_window
    ON tmp_base
    (
        client_email(100),
		vendor_name(100),
        created_at_ts,
        transaction_id
    );

    /* =========================================================
       ORDENADO
    ========================================================= */

    CREATE TEMPORARY TABLE tmp_ordenado AS
    SELECT
        *,
        LAG(created_at_ts) OVER (
            PARTITION BY client_email, vendor_name
            ORDER BY created_at_ts, transaction_id
        ) AS prev_ts
    FROM tmp_base;

    CREATE INDEX idx_tmp_ordenado
    ON tmp_ordenado
    (
        client_email(100),
		vendor_name(100),
        created_at_ts,
        transaction_id
    );

    /* =========================================================
       FLAG GRUPO
    ========================================================= */

    CREATE TEMPORARY TABLE tmp_flag_grupo AS
    SELECT
        *,
        CASE
            WHEN prev_ts IS NULL THEN 1
            WHEN TIMESTAMPDIFF(MINUTE, prev_ts, created_at_ts) > 240 THEN 1
            ELSE 0
        END AS new_group
    FROM tmp_ordenado;

    CREATE INDEX idx_tmp_flag
    ON tmp_flag_grupo
    (
        client_email(100),
		vendor_name(100),
        created_at_ts,
        transaction_id
    );

    /* =========================================================
       GRUPO ID
    ========================================================= */

    CREATE TEMPORARY TABLE tmp_grupo_id AS
    SELECT
        *,
        SUM(new_group) OVER (
            PARTITION BY client_email, vendor_name
            ORDER BY created_at_ts, transaction_id
            ROWS UNBOUNDED PRECEDING
        ) AS purchase_group_id
    FROM tmp_flag_grupo;

    CREATE INDEX idx_tmp_grupo
    ON tmp_grupo_id
    (
        client_email(100),
		vendor_name(100),
        purchase_group_id,
        created_at_ts
    );

    /* =========================================================
       GRUPO FINAL
    ========================================================= */

    CREATE TEMPORARY TABLE tmp_grupo_id_final AS
    SELECT
        g.*,
        SUBSTRING_INDEX(g.transaction_id, '-', 1) AS transaction_id_base,

        CASE
            WHEN MAX(
                CASE
                    WHEN g.product_sku = 'PRIORITYSHIPPING'
                    THEN 1 ELSE 0
                END
            ) OVER (
                PARTITION BY
                    g.client_email,
                    g.vendor_name,
                    SUBSTRING_INDEX(g.transaction_id, '-', 1)
            ) = 1

            THEN MIN(g.purchase_group_id) OVER (
                PARTITION BY
                    g.client_email,
                    g.vendor_name,
                    SUBSTRING_INDEX(g.transaction_id, '-', 1)
            )

            ELSE g.purchase_group_id
        END AS purchase_group_id_final

    FROM tmp_grupo_id g;

    CREATE INDEX idx_tmp_final
    ON tmp_grupo_id_final
    (
        client_email(100),
		vendor_name(100),
        purchase_group_id_final,
        created_at_ts
    );

    /* =========================================================
       CLASSIFICADO
    ========================================================= */

    CREATE TEMPORARY TABLE tmp_classificado AS
    SELECT
        *,

        CASE
            WHEN product_sku = 'PRIORITYSHIPPING'
                THEN 'order_bump'

            WHEN sales_type_lower LIKE 'produto principal%'
                THEN 'main'

            WHEN sales_type_lower = 'order bump'
                THEN 'order_bump'

            WHEN sales_type_lower = 'venda de funil'
                 AND offer_name_lower LIKE '%upsell 1%'
                THEN 'upsell1'

            WHEN sales_type_lower = 'venda de funil'
                 AND offer_name_lower LIKE '%upsell 2%'
                THEN 'upsell2'

            WHEN sales_type_lower = 'venda de funil'
                 AND offer_name_lower LIKE '%upsell 3%'
                THEN 'upsell3'

            WHEN sales_type_lower = 'venda de funil'
                 AND offer_name_lower LIKE '%downsell 1%'
                THEN 'downsell1'

            WHEN sales_type_lower = 'venda de funil'
                 AND offer_name_lower LIKE '%downsell 2%'
                THEN 'downsell2'

            WHEN sales_type_lower = 'venda de funil'
                 AND offer_name_lower LIKE '%downsell 3%'
                THEN 'downsell3'

            WHEN sales_type_lower = 'venda de funil'
                 AND (offer_name IS NULL OR TRIM(offer_name) = '')
                THEN 'funil_sem_offer'

            WHEN sales_type_lower = 'venda de funil'
                THEN 'funil_sem_offer'

            ELSE 'other'
        END AS funnel_type

    FROM tmp_grupo_id_final;

    CREATE INDEX idx_tmp_classificado
    ON tmp_classificado
    (
        client_email(100),
		vendor_name(100),
        purchase_group_id_final,
        funnel_type
    );

    /* =========================================================
       MAIN POR GRUPO
    ========================================================= */

    CREATE TEMPORARY TABLE tmp_main_por_grupo AS
    SELECT
        client_email,
        vendor_name,
        purchase_group_id_final,

        MAX(
            CASE WHEN funnel_type = 'main'
            THEN product_name END
        ) AS main_product_name,

        MAX(
            CASE WHEN funnel_type = 'main'
            THEN offer_name END
        ) AS main_offer_name,

        MAX(
            CASE WHEN funnel_type = 'main'
            THEN product_sku END
        ) AS main_product_sku,

        MIN(created_at_ts) AS grupo_ts

    FROM tmp_classificado
    GROUP BY
        client_email,
        vendor_name,
        purchase_group_id_final;

    CREATE INDEX idx_tmp_main
    ON tmp_main_por_grupo
    (
        client_email,
        vendor_name,
        grupo_ts
    );

    /* =========================================================
       INSERT FINAL
    ========================================================= */

    INSERT INTO instituto_experience.dashboard_gold_clickbank_stage_new

    SELECT
        MIN(c.transaction_id) AS transaction_id,

        MAX(c.payment_status) AS payment_status,

        MAX(c.client_name) AS client_name,

        c.client_email,

        MAX(c.client_phone) AS client_phone,

        MAX(c.client_zip) AS client_zip,

        MAX(c.client_country) AS client_country,

        MAX(c.client_state) AS client_state,

        MAX(c.client_city) AS client_city,

        MAX(c.client_street) AS client_street,

        COALESCE(
            MAX(
                CASE
                    WHEN c.funnel_type = 'main'
                    THEN c.product_name
                END
            ),
            MAX(mp.main_product_name)
        ) AS product_name,

        COALESCE(
            MAX(
                CASE
                    WHEN c.funnel_type = 'main'
                    THEN c.offer_name
                END
            ),
            MAX(mp.main_offer_name)
        ) AS offer_name,

        COALESCE(
            MAX(
                CASE
                    WHEN c.funnel_type = 'main'
                    THEN c.product_sku
                END
            ),
            MAX(mp.main_product_sku)
        ) AS product_sku,

        ROUND(SUM(c.product_cost), 4) AS product_cost,

        ROUND(SUM(c.product_cost_usd), 2) AS product_cost_usd,

        SUM(c.quantity) AS quantity,

        ROUND(SUM(c.total_price), 4) AS total_price,

        ROUND(SUM(c.total_price_usd), 2) AS total_price_usd,

        DATE(MIN(c.created_at_ts)) AS created_at_date,

        TIME_FORMAT(
            TIME(MIN(c.created_at_ts)),
            '%H:%i:%s'
        ) AS created_at_hour,

        MAX(c.vendor_name) AS vendor_name,

        MAX(c.is_house_traffic) AS is_house_traffic

    FROM tmp_classificado c

    LEFT JOIN tmp_main_por_grupo mp
           ON mp.client_email = c.client_email
          AND mp.vendor_name = c.vendor_name
          AND mp.grupo_ts <= c.created_at_ts

    GROUP BY
        c.client_email,
        c.vendor_name,
        c.purchase_group_id_final;

    /* =========================================================
       SWAP ATÔMICO
    ========================================================= */

    RENAME TABLE
        instituto_experience.dashboard_gold_clickbank
            TO instituto_experience.dashboard_gold_clickbank_old,

        instituto_experience.dashboard_gold_clickbank_stage_new
            TO instituto_experience.dashboard_gold_clickbank,

        instituto_experience.dashboard_gold_clickbank_old
            TO instituto_experience.dashboard_gold_clickbank_stage;

    /* =========================================================
       CLEANUP
    ========================================================= */

    DROP TEMPORARY TABLE IF EXISTS tmp_base;
    DROP TEMPORARY TABLE IF EXISTS tmp_ordenado;
    DROP TEMPORARY TABLE IF EXISTS tmp_flag_grupo;
    DROP TEMPORARY TABLE IF EXISTS tmp_grupo_id;
    DROP TEMPORARY TABLE IF EXISTS tmp_grupo_id_final;
    DROP TEMPORARY TABLE IF EXISTS tmp_classificado;
    DROP TEMPORARY TABLE IF EXISTS tmp_main_por_grupo;

END
```
