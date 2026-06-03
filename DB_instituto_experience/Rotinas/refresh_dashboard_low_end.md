---
tipo: procedure
definer: "gabriel_gomes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-25 13:34:51"
alterada_em: "2026-05-25 13:34:51"
execucoes: 2289
tags: [rotina, procedure]
---

# refresh_dashboard_low_end

## Dependências

- **Lê:** [[call_center_sales]], [[cartpanda_physical]], [[dashboard_gold_buygoods]], [[dashboard_gold_clickbank]], [[funil_produto_mapping]], [[google_ad_id]]
- **Escreve:** [[dashboard_low_end]]
- **Cria:** —
- **Trunca:** [[dashboard_low_end]]
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 2,289 |
| Tempo médio | 9.0 s |
| Tempo máx | 17m24s |
| Tempo total | 5h42m |
| Erros | 30 |
| Warnings | 22,920,242 |
| Linhas afetadas (total) | 16,230,732 |

## Corpo SQL

```sql
BEGIN
    TRUNCATE TABLE dashboard_low_end;

    INSERT INTO dashboard_low_end (
        data_venda, nome_produto, gestor_trafego, traffic_source,
        is_reference_row,
        units_1_2, units_3_4, units_6_plus,
        total_vendas, revenue, product_cost, commission, taxes, imposto, total_refund, net_sales_value,
        revenue_no_funnel,
        ob_count, ob_revenue,
        up1_count, up1_revenue, up2_count, up2_revenue, up3_count, up3_revenue,
        down1_count, down1_revenue, down2_count, down2_revenue, down3_count, down3_revenue,
        ad_spend, retry_count, retry_revenue,
        company_frontend_sales_brl
    )
    WITH
        -- 1. ADS MAPPED (apenas Google Ads)
        ads_mapped AS (
            SELECT
                g.created_at_date,
                g.campaign_name,
                'Google Ads' COLLATE utf8mb4_unicode_ci AS platform,
                g.amount_spent_brl,
                CONCAT('Funil de Nova Ideia #', REGEXP_SUBSTR(g.campaign_name, '[0-9]+', 1, 1)) AS extracted_funil_id,
                fpm.clean_product_name AS mapped_name
            FROM instituto_experience.google_ad_id g
                     LEFT JOIN instituto_experience.funil_produto_mapping fpm
                               ON CONCAT('Funil de Nova Ideia #', REGEXP_SUBSTR(g.campaign_name, '[0-9]+', 1, 1)) = fpm.funil_id
            WHERE g.created_at_date >= '2025-09-01'
              AND g.campaign_name LIKE '%Nova Ideia%'
              AND g.campaign_name LIKE '%Thales Paternostro%'
        ),

        -- 2. RAW BACKEND
        raw_backend AS (
            -- ===================== 1) CARTPANDA =====================
            SELECT
                cp.created_at_date,
                LOWER(REGEXP_REPLACE(
                        TRIM(CASE
                                 WHEN cp.product_name LIKE '%-%' THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                 WHEN REGEXP_LIKE(cp.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                 ELSE cp.product_name
                            END),
                        '[^a-zA-Z0-9]', '')) COLLATE utf8mb4_unicode_ci AS product_key,
                'Thales Paternostro' COLLATE utf8mb4_unicode_ci AS gestor_trafego,
                (CASE
                     WHEN cp.offer_name LIKE '%: [%]%' THEN TRIM(REGEXP_REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, ': [', -1), ']', 1), '[^a-zA-Z0-9 ]', ''))
                     ELSE 'Outros'
                    END) COLLATE utf8mb4_unicode_ci AS traffic_source,

                CASE WHEN LOWER(cp.product_sku) REGEXP '1unit|2unit|1 pote|2 potes' THEN 1 ELSE 0 END AS is_1_2,
                CASE WHEN LOWER(cp.product_sku) REGEXP '3unit|4unit|3 potes|4 potes' THEN 1 ELSE 0 END AS is_3_4,
                CASE WHEN LOWER(cp.product_sku) REGEXP '6unit|8unit|10unit|12unit|6 potes|8 potes' THEN 1 ELSE 0 END AS is_6_plus,

                cp.payment_status COLLATE utf8mb4_unicode_ci AS payment_status,
                cp.total_price, cp.product_cost, cp.commission, cp.taxes, cp.total_refund, cp.cartpanda_retry,
                (cp.total_price * 0.05) AS imposto_calc,

                cp.has_order_bump, cp.total_price_order_bump,
                cp.has_upsell, cp.total_price_upsell,
                cp.has_upsell2, cp.total_price_upsell2,
                cp.has_upsell3, cp.total_price_upsell3,
                cp.has_downsell, cp.total_price_downsell,
                cp.has_downsell2, cp.total_price_downsell2,
                cp.has_downsell3, cp.total_price_downsell3,

                0 AS amount_spent_brl
            FROM instituto_experience.cartpanda_physical cp
            WHERE cp.created_at_date >= '2025-09-01'
              AND (
                (
                    cp.offer_name LIKE '%Nova Ideia%'
                        AND (cp.offer_name LIKE '%Thales Paternostro%' OR cp.offer_name LIKE '%Low End%' OR cp.offer_name LIKE '%Fundo de Funil%')
                    )
                    OR cp.offer_name LIKE '%Brand Bidding%'
                )

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
                        '[^a-zA-Z0-9]', '')) COLLATE utf8mb4_unicode_ci AS product_key,
                'Thales Paternostro' COLLATE utf8mb4_unicode_ci AS gestor_trafego,
                (CASE
                     WHEN cb.offer_name LIKE '%: [%]%' THEN TRIM(REGEXP_REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(cb.offer_name, ': [', -1), ']', 1), '[^a-zA-Z0-9 ]', ''))
                     ELSE 'Outros'
                    END) COLLATE utf8mb4_unicode_ci AS traffic_source,

                CASE WHEN LOWER(cb.product_sku) REGEXP '1unit|2unit|1 pote|2 potes' THEN 1 ELSE 0 END AS is_1_2,
                CASE WHEN LOWER(cb.product_sku) REGEXP '3unit|4unit|3 potes|4 potes' THEN 1 ELSE 0 END AS is_3_4,
                CASE WHEN LOWER(cb.product_sku) REGEXP '6unit|8unit|10unit|12unit|6 potes|8 potes' THEN 1 ELSE 0 END AS is_6_plus,

                cb.payment_status COLLATE utf8mb4_unicode_ci AS payment_status,
                cb.total_price, cb.product_cost, cb.commission, cb.taxes, cb.total_refund,
                0 AS cartpanda_retry,
                (cb.total_price * 0.05) AS imposto_calc,

                cb.has_order_bump, cb.total_price_order_bump,
                cb.has_upsell, cb.total_price_upsell,
                cb.has_upsell2, cb.total_price_upsell2,
                cb.has_upsell3, cb.total_price_upsell3,
                cb.has_downsell, cb.total_price_downsell,
                cb.has_downsell2, cb.total_price_downsell2,
                cb.has_downsell3, cb.total_price_downsell3,

                0 AS amount_spent_brl
            FROM instituto_experience.dashboard_gold_clickbank cb
            WHERE cb.created_at_date >= '2025-09-01'
              AND (
                (
                    cb.offer_name LIKE '%Nova Ideia%'
                        AND (cb.offer_name LIKE '%Thales Paternostro%' OR cb.offer_name LIKE '%Low End%' OR cb.offer_name LIKE '%Fundo de Funil%')
                    )
                    OR cb.offer_name LIKE '%Brand Bidding%'
                )
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
                        '[^a-zA-Z0-9]', '')) COLLATE utf8mb4_unicode_ci AS product_key,
                'Thales Paternostro' COLLATE utf8mb4_unicode_ci AS gestor_trafego,
                (CASE
                     WHEN bg.offer_name LIKE '%: [%]%' THEN TRIM(REGEXP_REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(bg.offer_name, ': [', -1), ']', 1), '[^a-zA-Z0-9 ]', ''))
                     ELSE 'Outros'
                    END) COLLATE utf8mb4_unicode_ci AS traffic_source,

                CASE WHEN LOWER(bg.product_sku) REGEXP '1unit|2unit|1 pote|2 potes' THEN 1 ELSE 0 END AS is_1_2,
                CASE WHEN LOWER(bg.product_sku) REGEXP '3unit|4unit|3 potes|4 potes' THEN 1 ELSE 0 END AS is_3_4,
                CASE WHEN LOWER(bg.product_sku) REGEXP '6unit|8unit|10unit|12unit|6 potes|8 potes' THEN 1 ELSE 0 END AS is_6_plus,

                bg.payment_status COLLATE utf8mb4_unicode_ci AS payment_status,
                bg.total_price, bg.product_cost, bg.commission, bg.taxes, bg.total_refund,
                0 AS cartpanda_retry,
                (bg.total_price * 0.05) AS imposto_calc,

                bg.has_order_bump, bg.total_price_order_bump,
                bg.has_upsell, bg.total_price_upsell,
                bg.has_upsell2, bg.total_price_upsell2,
                bg.has_upsell3, bg.total_price_upsell3,
                bg.has_downsell, bg.total_price_downsell,
                bg.has_downsell2, bg.total_price_downsell2,
                bg.has_downsell3, bg.total_price_downsell3,

                0 AS amount_spent_brl
            FROM instituto_experience.dashboard_gold_buygoods bg
            WHERE bg.created_at_date >= '2025-09-01'
              AND (
                (
                    bg.offer_name LIKE '%Nova Ideia%'
                        AND (bg.offer_name LIKE '%Thales Paternostro%' OR bg.offer_name LIKE '%Low End%' OR bg.offer_name LIKE '%Fundo de Funil%')
                    )
                    OR bg.offer_name LIKE '%Brand Bidding%'
                )
              AND (bg.is_house_traffic = 0 OR bg.is_house_traffic IS NULL)

            UNION ALL

            -- ===================== 4) ADS =====================
            SELECT
                created_at_date,
                LOWER(REGEXP_REPLACE(TRIM(COALESCE(mapped_name, REGEXP_SUBSTR(campaign_name, "^[a-zA-Z ']+"))), '[^a-zA-Z0-9]', '')) COLLATE utf8mb4_unicode_ci AS product_key,
                'Thales Paternostro' COLLATE utf8mb4_unicode_ci AS gestor_trafego,
                platform COLLATE utf8mb4_unicode_ci AS traffic_source,

                0, 0, 0,
                CAST(NULL AS CHAR) COLLATE utf8mb4_unicode_ci AS payment_status,
                0, 0, 0, 0, 0, 0,
                0,

                0, 0,
                0, 0,
                0, 0,
                0, 0,
                0, 0,
                0, 0,
                0, 0,

                amount_spent_brl
            FROM ads_mapped
        ),

        -- 3. AGREGAÇÃO
        aggregated_backend AS (
            SELECT
                created_at_date, product_key, gestor_trafego, traffic_source,
                SUM(is_1_2) AS sum_1_2, SUM(is_3_4) AS sum_3_4, SUM(is_6_plus) AS sum_6_plus,
                COALESCE(COUNT(CASE WHEN payment_status IS NOT NULL THEN 1 END), 0) AS total_vendas,
                COALESCE(SUM(total_price), 0) AS rev,
                COALESCE(SUM(product_cost), 0) AS cost,
                COALESCE(SUM(commission), 0) AS comm,
                COALESCE(SUM(taxes), 0) AS tax,
                COALESCE(SUM(imposto_calc), 0) AS imp,
                COALESCE(SUM(total_refund), 0) AS ref,
                (COALESCE(SUM(total_price), 0) - COALESCE(SUM(total_refund), 0) - COALESCE(SUM(product_cost), 0) - COALESCE(SUM(taxes), 0) - COALESCE(SUM(commission), 0) - COALESCE(SUM(imposto_calc), 0)) AS net_val,

                COALESCE(SUM(has_order_bump), 0) AS ob_c, COALESCE(SUM(total_price_order_bump), 0) AS ob_r,
                COALESCE(SUM(has_upsell), 0) AS up1_c, COALESCE(SUM(total_price_upsell), 0) AS up1_r,
                COALESCE(SUM(has_upsell2), 0) AS up2_c, COALESCE(SUM(total_price_upsell2), 0) AS up2_r,
                COALESCE(SUM(has_upsell3), 0) AS up3_c, COALESCE(SUM(total_price_upsell3), 0) AS up3_r,

                COALESCE(SUM(has_downsell), 0) AS down1_c, COALESCE(SUM(total_price_downsell), 0) AS down1_r,
                COALESCE(SUM(has_downsell2), 0) AS down2_c, COALESCE(SUM(total_price_downsell2), 0) AS down2_r,
                COALESCE(SUM(has_downsell3), 0) AS down3_c, COALESCE(SUM(total_price_downsell3), 0) AS down3_r,

                COALESCE(SUM(amount_spent_brl), 0) AS ads,
                COALESCE(SUM(CASE WHEN cartpanda_retry > 0 THEN 1 ELSE 0 END), 0) AS ret_c,
                COALESCE(SUM(CASE WHEN cartpanda_retry > 0 THEN total_price ELSE 0 END), 0) AS ret_r

            FROM raw_backend
            GROUP BY 1, 2, 3, 4
        ),

        -- 4. FRONT-END
        frontend AS (
            SELECT
                data,
                LOWER(REGEXP_REPLACE(nome_produto, '[^a-zA-Z0-9]', '')) COLLATE utf8mb4_unicode_ci AS join_key,
                COALESCE(SUM(frontend_sales * 5.4), 0) AS front_brl
            FROM call_center_sales
            WHERE nome_produto != 'Geral' AND nome_produto NOT LIKE '%Sem Nome%' AND nome_produto NOT LIKE '%Outros%'
            GROUP BY 1, 2
        ),

        -- 5. UNIVERSO
        universe AS (
            SELECT created_at_date AS dt, product_key AS pk FROM aggregated_backend
            UNION
            SELECT data AS dt, join_key AS pk FROM frontend
        ),

        -- 6. FULL JOIN
        final_prep AS (
            SELECT
                u.dt, u.pk,
                COALESCE(ab.gestor_trafego, 'Thales Paternostro') AS gestor_trafego,
                ab.traffic_source,
                COALESCE(ab.sum_1_2, 0) AS sum_1_2, COALESCE(ab.sum_3_4, 0) AS sum_3_4, COALESCE(ab.sum_6_plus, 0) AS sum_6_plus,
                COALESCE(ab.total_vendas, 0) AS total_vendas, COALESCE(ab.rev, 0) AS rev, COALESCE(ab.cost, 0) AS cost,
                COALESCE(ab.comm, 0) AS comm, COALESCE(ab.tax, 0) AS tax, COALESCE(ab.imp, 0) AS imp, COALESCE(ab.ref, 0) AS ref,
                COALESCE(ab.net_val, 0) AS net_val,

                COALESCE(ab.ob_c, 0) AS ob_c, COALESCE(ab.ob_r, 0) AS ob_r,
                COALESCE(ab.up1_c, 0) AS up1_c, COALESCE(ab.up1_r, 0) AS up1_r,
                COALESCE(ab.up2_c, 0) AS up2_c, COALESCE(ab.up2_r, 0) AS up2_r,
                COALESCE(ab.up3_c, 0) AS up3_c, COALESCE(ab.up3_r, 0) AS up3_r,

                COALESCE(ab.down1_c, 0) AS down1_c, COALESCE(ab.down1_r, 0) AS down1_r,
                COALESCE(ab.down2_c, 0) AS down2_c, COALESCE(ab.down2_r, 0) AS down2_r,
                COALESCE(ab.down3_c, 0) AS down3_c, COALESCE(ab.down3_r, 0) AS down3_r,

                COALESCE(ab.ads, 0) AS ads, COALESCE(ab.ret_c, 0) AS ret_c, COALESCE(ab.ret_r, 0) AS ret_r,
                COALESCE(fe.front_brl, 0) AS front_total_brl,

                ROW_NUMBER() OVER (PARTITION BY u.dt, u.pk ORDER BY COALESCE(ab.rev, 0) DESC, ab.traffic_source ASC) AS row_rank
            FROM universe u
                     LEFT JOIN aggregated_backend ab ON u.dt = ab.created_at_date AND u.pk = ab.product_key
                     LEFT JOIN frontend fe ON u.dt = fe.data AND u.pk = fe.join_key
        )

    -- 7. INSERT FINAL
    SELECT
        dt, pk, gestor_trafego, traffic_source,
        CASE WHEN row_rank = 1 THEN 1 ELSE 0 END,
        sum_1_2, sum_3_4, sum_6_plus,
        total_vendas, rev, cost, comm, tax, imp, ref, net_val,
        (rev - (ob_r + up1_r + up2_r + up3_r + down1_r + down2_r + down3_r)) AS revenue_no_funnel,
        ob_c, ob_r,
        up1_c, up1_r, up2_c, up2_r, up3_c, up3_r,
        down1_c, down1_r, down2_c, down2_r, down3_c, down3_r,
        ads, ret_c, ret_r,
        front_total_brl
    FROM final_prep;

END
```
