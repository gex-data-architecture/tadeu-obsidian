---
tipo: procedure
definer: "gabriel_gomes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-25 12:43:43"
alterada_em: "2026-05-25 12:43:43"
execucoes: ""
tags: [rotina, procedure]
---

# refresh_dashboard_email_marketing

## Dependências

- **Lê:** [[call_center_sales]], [[cartpanda_physical]], [[dashboard_gold_buygoods]], [[dashboard_gold_clickbank]]
- **Escreve:** [[dashboard_email_marketing]]
- **Cria:** —
- **Trunca:** [[dashboard_email_marketing]]
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN
    TRUNCATE TABLE dashboard_email_marketing;

    INSERT INTO dashboard_email_marketing (
        data_venda,
        nome_produto,
        niche,
        tipo_venda,
        is_reference_row,
        is_global_reference_row,
        units_1_2, units_3_5, units_6_plus,
        total_vendas,
        revenue,
        product_cost,
        commission,
        taxes,
        imposto,
        total_refund,
        net_sales_value,
        revenue_no_funnel,
        ob_count, ob_revenue,
        up1_count, up1_revenue,
        up2_count, up2_revenue,
        up3_count, up3_revenue,
        down1_count, down1_revenue,
        down2_count, down2_revenue,
        down3_count, down3_revenue,
        company_frontend_sales_brl
    )

    WITH

        raw_email AS (
            -- ===================== 1) CARTPANDA =====================
            SELECT
                cp.created_at_date,

                LOWER(REGEXP_REPLACE(
                        TRIM(CASE
                                 WHEN cp.product_name LIKE '%-%' THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                 WHEN REGEXP_LIKE(cp.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                 ELSE cp.product_name
                            END),
                        '[^a-zA-Z0-9]', ''
                      )) COLLATE utf8mb4_unicode_ci AS product_key,

                (CASE
                     WHEN LOWER(cp.offer_name) LIKE '%recup%' THEN 'Recuperação'
                     WHEN LOWER(cp.offer_name) LIKE '%mone%' THEN 'Monetização'
                     WHEN LOWER(cp.offer_name) LIKE '%broad%' THEN 'Broadcast'
                     ELSE 'Outros'
                    END) COLLATE utf8mb4_unicode_ci AS tipo_venda,

                CASE WHEN LOWER(cp.product_sku) REGEXP '1unit|2unit' THEN 1 ELSE 0 END AS is_1_2,
                CASE WHEN LOWER(cp.product_sku) REGEXP '3unit|4unit|5unit' THEN 1 ELSE 0 END AS is_3_5,
                CASE WHEN LOWER(cp.product_sku) REGEXP '6unit|7unit|8unit|9unit|10unit|11unit|12unit' THEN 1 ELSE 0 END AS is_6_plus,

                cp.payment_status COLLATE utf8mb4_unicode_ci AS payment_status,
                cp.total_price,
                cp.product_cost,
                cp.commission,
                cp.taxes,
                cp.total_refund,
                (cp.total_price * 0.05) AS imposto_calc,

                cp.has_order_bump, cp.total_price_order_bump,
                cp.has_upsell, cp.total_price_upsell,
                cp.has_upsell2, cp.total_price_upsell2,
                cp.has_upsell3, cp.total_price_upsell3,
                cp.has_downsell, cp.total_price_downsell,
                cp.has_downsell2, cp.total_price_downsell2,
                cp.has_downsell3, cp.total_price_downsell3

            FROM instituto_experience.cartpanda_physical cp
            WHERE cp.created_at_date >= '2025-01-01'
              AND LOWER(cp.offer_name) LIKE '%mail%'
              AND (
                LOWER(cp.offer_name) LIKE '%recup%'
                    OR LOWER(cp.offer_name) LIKE '%mone%'
                    OR LOWER(cp.offer_name) LIKE '%broad%'
                )
              AND LOWER(cp.offer_name) NOT LIKE '%parceiro%'
              AND UPPER(cp.offer_name) NOT LIKE '%DAMAS%'

            UNION ALL

            -- ===================== 2) CLICKBANK =====================
            SELECT
                cb.created_at_date,

                LOWER(REGEXP_REPLACE(
                        TRIM(CASE
                                 WHEN cb.product_name LIKE '%-%' THEN TRIM(SUBSTRING_INDEX(cb.product_name, '-', 1))
                                 WHEN REGEXP_LIKE(cb.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(cb.product_name, '^[^0-9]+'))
                                 ELSE cb.product_name
                            END),
                        '[^a-zA-Z0-9]', ''
                      )) COLLATE utf8mb4_unicode_ci AS product_key,

                (CASE
                     WHEN LOWER(cb.offer_name) LIKE '%recup%' THEN 'Recuperação'
                     WHEN LOWER(cb.offer_name) LIKE '%mone%' THEN 'Monetização'
                     WHEN LOWER(cb.offer_name) LIKE '%broad%' THEN 'Broadcast'
                     ELSE 'Outros'
                    END) COLLATE utf8mb4_unicode_ci AS tipo_venda,

                CASE
                    WHEN REGEXP_LIKE(cb.product_sku, '([^0-9]|^)[12]UNITS?', 'i')
                        AND NOT REGEXP_LIKE(cb.product_sku, '12UNITS?', 'i')
                        THEN 1 ELSE 0
                    END AS is_1_2,
                CASE
                    WHEN REGEXP_LIKE(cb.product_sku, '([^0-9]|^)[345]UNITS?', 'i')
                        THEN 1 ELSE 0
                    END AS is_3_5,
                CASE
                    WHEN REGEXP_LIKE(cb.product_sku, '([^0-9]|^)[6789]UNITS?', 'i')
                        OR REGEXP_LIKE(cb.product_sku, '1[0-2]UNITS?', 'i')
                        THEN 1 ELSE 0
                    END AS is_6_plus,

                cb.payment_status COLLATE utf8mb4_unicode_ci AS payment_status,
                cb.total_price,
                cb.product_cost,
                cb.commission,
                cb.taxes,
                cb.total_refund,
                (cb.total_price * 0.05) AS imposto_calc,

                cb.has_order_bump, cb.total_price_order_bump,
                cb.has_upsell, cb.total_price_upsell,
                cb.has_upsell2, cb.total_price_upsell2,
                cb.has_upsell3, cb.total_price_upsell3,
                cb.has_downsell, cb.total_price_downsell,
                cb.has_downsell2, cb.total_price_downsell2,
                cb.has_downsell3, cb.total_price_downsell3

            FROM instituto_experience.dashboard_gold_clickbank cb
            WHERE cb.created_at_date >= '2025-01-01'
              AND LOWER(cb.offer_name) LIKE '%mail%'
              AND (
                LOWER(cb.offer_name) LIKE '%recup%'
                    OR LOWER(cb.offer_name) LIKE '%mone%'
                    OR LOWER(cb.offer_name) LIKE '%broad%'
                )
              AND LOWER(cb.offer_name) NOT LIKE '%parceiro%'
              AND UPPER(cb.offer_name) NOT LIKE '%DAMAS%'
              AND (cb.is_house_traffic = 0 OR cb.is_house_traffic IS NULL)

            UNION ALL

            -- ===================== 3) BUYGOODS =====================
            SELECT
                bg.created_at_date,

                LOWER(REGEXP_REPLACE(
                        TRIM(CASE
                                 WHEN bg.product_name LIKE '%-%' THEN TRIM(SUBSTRING_INDEX(bg.product_name, '-', 1))
                                 WHEN REGEXP_LIKE(bg.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(bg.product_name, '^[^0-9]+'))
                                 ELSE bg.product_name
                            END),
                        '[^a-zA-Z0-9]', ''
                      )) COLLATE utf8mb4_unicode_ci AS product_key,

                (CASE
                     WHEN LOWER(bg.offer_name) LIKE '%recup%' THEN 'Recuperação'
                     WHEN LOWER(bg.offer_name) LIKE '%mone%' THEN 'Monetização'
                     WHEN LOWER(bg.offer_name) LIKE '%broad%' THEN 'Broadcast'
                     ELSE 'Outros'
                    END) COLLATE utf8mb4_unicode_ci AS tipo_venda,

                CASE
                    WHEN REGEXP_LIKE(bg.product_sku, '([^0-9]|^)[12]UNITS?', 'i')
                        AND NOT REGEXP_LIKE(bg.product_sku, '12UNITS?', 'i')
                        THEN 1 ELSE 0
                    END AS is_1_2,
                CASE
                    WHEN REGEXP_LIKE(bg.product_sku, '([^0-9]|^)[345]UNITS?', 'i')
                        THEN 1 ELSE 0
                    END AS is_3_5,
                CASE
                    WHEN REGEXP_LIKE(bg.product_sku, '([^0-9]|^)[6789]UNITS?', 'i')
                        OR REGEXP_LIKE(bg.product_sku, '1[0-2]UNITS?', 'i')
                        THEN 1 ELSE 0
                    END AS is_6_plus,

                bg.payment_status COLLATE utf8mb4_unicode_ci AS payment_status,
                bg.total_price,
                bg.product_cost,
                bg.commission,
                bg.taxes,
                bg.total_refund,
                (bg.total_price * 0.05) AS imposto_calc,

                bg.has_order_bump, bg.total_price_order_bump,
                bg.has_upsell, bg.total_price_upsell,
                bg.has_upsell2, bg.total_price_upsell2,
                bg.has_upsell3, bg.total_price_upsell3,
                bg.has_downsell, bg.total_price_downsell,
                bg.has_downsell2, bg.total_price_downsell2,
                bg.has_downsell3, bg.total_price_downsell3

            FROM instituto_experience.dashboard_gold_buygoods bg
            WHERE bg.created_at_date >= '2025-01-01'
              AND LOWER(bg.offer_name) LIKE '%mail%'
              AND (
                LOWER(bg.offer_name) LIKE '%recup%'
                    OR LOWER(bg.offer_name) LIKE '%mone%'
                    OR LOWER(bg.offer_name) LIKE '%broad%'
                )
              AND LOWER(bg.offer_name) NOT LIKE '%parceiro%'
              AND UPPER(bg.offer_name) NOT LIKE '%DAMAS%'
              AND (bg.is_house_traffic = 0 OR bg.is_house_traffic IS NULL)
        ),

        aggregated_email AS (
            SELECT
                created_at_date,
                product_key,
                tipo_venda,

                SUM(is_1_2) AS sum_1_2,
                SUM(is_3_5) AS sum_3_5,
                SUM(is_6_plus) AS sum_6_plus,

                COUNT(CASE WHEN payment_status IS NOT NULL THEN 1 END) AS total_vendas,
                COALESCE(SUM(total_price), 0) AS rev,
                COALESCE(SUM(product_cost), 0) AS cost,
                COALESCE(SUM(commission), 0) AS comm,
                COALESCE(SUM(taxes), 0) AS tax,
                COALESCE(SUM(imposto_calc), 0) AS imp,
                COALESCE(SUM(total_refund), 0) AS ref,

                (COALESCE(SUM(commission), 0)
                    - COALESCE(SUM(product_cost), 0)
                    - COALESCE(SUM(imposto_calc), 0)
                    ) AS net_val,

                COALESCE(SUM(has_order_bump), 0) AS ob_c,
                COALESCE(SUM(total_price_order_bump), 0) AS ob_r,
                COALESCE(SUM(has_upsell), 0) AS up1_c,
                COALESCE(SUM(total_price_upsell), 0) AS up1_r,
                COALESCE(SUM(has_upsell2), 0) AS up2_c,
                COALESCE(SUM(total_price_upsell2), 0) AS up2_r,
                COALESCE(SUM(has_upsell3), 0) AS up3_c,
                COALESCE(SUM(total_price_upsell3), 0) AS up3_r,
                COALESCE(SUM(has_downsell), 0) AS down1_c,
                COALESCE(SUM(total_price_downsell), 0) AS down1_r,
                COALESCE(SUM(has_downsell2), 0) AS down2_c,
                COALESCE(SUM(total_price_downsell2), 0) AS down2_r,
                COALESCE(SUM(has_downsell3), 0) AS down3_c,
                COALESCE(SUM(total_price_downsell3), 0) AS down3_r

            FROM raw_email
            GROUP BY created_at_date, product_key, tipo_venda
        ),

        frontend AS (
            SELECT
                data,
                LOWER(REGEXP_REPLACE(nome_produto, '[^a-zA-Z0-9]', '')) COLLATE utf8mb4_unicode_ci AS join_key,
                MAX(niche) AS niche,
                COALESCE(SUM(frontend_sales * 5.4), 0) AS front_brl
            FROM call_center_sales
            WHERE nome_produto != 'Geral'
              AND nome_produto NOT LIKE '%Sem Nome%'
              AND nome_produto NOT LIKE '%Outros%'
            GROUP BY data, join_key
        ),

        tipos AS (
            SELECT 'Recuperação' COLLATE utf8mb4_unicode_ci AS tipo_venda
            UNION ALL
            SELECT 'Monetização' COLLATE utf8mb4_unicode_ci
            UNION ALL
            SELECT 'Broadcast' COLLATE utf8mb4_unicode_ci
        ),

        base_universe AS (
            SELECT DISTINCT created_at_date AS dt, product_key AS pk FROM aggregated_email
            UNION
            SELECT DISTINCT data AS dt, join_key AS pk FROM frontend
        ),

        universe AS (
            SELECT
                bu.dt,
                bu.pk,
                t.tipo_venda
            FROM base_universe bu
                     CROSS JOIN tipos t
        ),

        final_prep AS (
            SELECT
                u.dt,
                u.pk,
                fe.niche,
                u.tipo_venda,

                COALESCE(ae.sum_1_2, 0) AS sum_1_2,
                COALESCE(ae.sum_3_5, 0) AS sum_3_5,
                COALESCE(ae.sum_6_plus, 0) AS sum_6_plus,
                COALESCE(ae.total_vendas, 0) AS total_vendas,
                COALESCE(ae.rev, 0) AS rev,
                COALESCE(ae.cost, 0) AS cost,
                COALESCE(ae.comm, 0) AS comm,
                COALESCE(ae.tax, 0) AS tax,
                COALESCE(ae.imp, 0) AS imp,
                COALESCE(ae.ref, 0) AS ref,
                COALESCE(ae.net_val, 0) AS net_val,

                COALESCE(ae.ob_c, 0) AS ob_c, COALESCE(ae.ob_r, 0) AS ob_r,
                COALESCE(ae.up1_c, 0) AS up1_c, COALESCE(ae.up1_r, 0) AS up1_r,
                COALESCE(ae.up2_c, 0) AS up2_c, COALESCE(ae.up2_r, 0) AS up2_r,
                COALESCE(ae.up3_c, 0) AS up3_c, COALESCE(ae.up3_r, 0) AS up3_r,
                COALESCE(ae.down1_c, 0) AS down1_c, COALESCE(ae.down1_r, 0) AS down1_r,
                COALESCE(ae.down2_c, 0) AS down2_c, COALESCE(ae.down2_r, 0) AS down2_r,
                COALESCE(ae.down3_c, 0) AS down3_c, COALESCE(ae.down3_r, 0) AS down3_r,

                COALESCE(fe.front_brl, 0) AS front_total_brl,

                ROW_NUMBER() OVER (
                    PARTITION BY u.dt, u.pk, u.tipo_venda
                    ORDER BY COALESCE(ae.rev, 0) DESC
                    ) AS row_rank,

                ROW_NUMBER() OVER (
                    PARTITION BY u.dt, u.pk
                    ORDER BY COALESCE(ae.rev, 0) DESC, u.tipo_venda ASC
                    ) AS global_row_rank

            FROM universe u
                     LEFT JOIN aggregated_email ae
                               ON u.dt = ae.created_at_date
                                   AND u.pk = ae.product_key
                                   AND u.tipo_venda = ae.tipo_venda
                     LEFT JOIN frontend fe
                               ON u.dt = fe.data
                                   AND u.pk = fe.join_key
        )

    SELECT
        dt,
        pk,
        niche,
        tipo_venda,
        CASE WHEN row_rank = 1 THEN 1 ELSE 0 END,
        CASE WHEN global_row_rank = 1 THEN 1 ELSE 0 END,

        sum_1_2, sum_3_5, sum_6_plus,

        total_vendas,
        rev,
        cost,
        comm,
        tax,
        imp,
        ref,
        net_val,

        (rev - (ob_r + up1_r + up2_r + up3_r + down1_r + down2_r + down3_r)),

        ob_c, ob_r,
        up1_c, up1_r,
        up2_c, up2_r,
        up3_c, up3_r,
        down1_c, down1_r,
        down2_c, down2_r,
        down3_c, down3_r,

        front_total_brl

    FROM final_prep;

END
```
