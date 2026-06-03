---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-22 17:43:40"
alterada_em: "2026-05-22 17:43:40"
execucoes: 182
tags: [rotina, procedure]
---

# refresh_dashboard_internal_sales_v2

## Dependências

- **Lê:** [[call_center_sales]], [[cartpanda_physical]], [[custos_conta_agencia_diaria]], [[custos_gerais_diaria]], [[custos_trafego_gestores_diaria]], [[dashboard_gold_clickbank_buygoods]], [[dim_copywriter]], [[dim_squad]], [[meta_ad_id]]
- **Escreve:** [[dashboard_internal_sales_v2_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_internal_sales_v2_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 5m7s |
| Tempo máx | 20m26s |
| Tempo total | 15h30m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 292,887 |

## Corpo SQL

```sql
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_internal_sales_v2_stage;
        RESIGNAL;
    END;

    TRUNCATE TABLE instituto_experience.dashboard_internal_sales_v2_stage;

    INSERT INTO instituto_experience.dashboard_internal_sales_v2_stage
    WITH ud_base AS (
    SELECT
        ud.created_at_date,
        ud.product_key,
        ud.clean_product_name,
        ud.gestor_trafego,
        ud.traffic_source,
        ud.coupon_code,
        ud.total_vendas,
        ud.total_price,
        ud.total_price_usd,
        ud.commission,
        ud.commission_usd,
        ud.taxes,
        ud.taxes_usd,
        ud.total_refund,
        ud.total_refund_usd,
        ud.product_cost,
        ud.product_cost_usd,
        ud.imposto,
        ud.`1_2_units_sales`,
        ud.`3_4_units_sales`,
        ud.`5_6_units_sales`,
        ud.ob_count, ud.ob_revenue, ud.ob_revenue_usd,
        ud.up1_count, ud.up1_revenue, ud.up1_revenue_usd,
        ud.up2_count, ud.up2_revenue, ud.up2_revenue_usd,
        ud.up3_count, ud.up3_revenue, ud.up3_revenue_usd,
        ud.down1_count, ud.down1_revenue, ud.down1_revenue_usd,
        ud.down2_count, ud.down2_revenue, ud.down2_revenue_usd,
        ud.down3_count, ud.down3_revenue, ud.down3_revenue_usd,
        (ud.total_price - (
            ud.ob_revenue + ud.up1_revenue + ud.up2_revenue + ud.up3_revenue
            + ud.down1_revenue + ud.down2_revenue + ud.down3_revenue
        )) AS revenue_no_funnel,
        (ud.total_price_usd - (
            ud.ob_revenue_usd + ud.up1_revenue_usd + ud.up2_revenue_usd + ud.up3_revenue_usd
            + ud.down1_revenue_usd + ud.down2_revenue_usd + ud.down3_revenue_usd
        )) AS revenue_no_funnel_usd,
        ud.amount_spent_brl,
        ud.cartpanda_retry_count,
        ud.cartpanda_retry_revenue,
        ud.cartpanda_retry_revenue_usd,
        ud.spent_taxes,
        ud.amount_spent_total,
        ud.revenue_afiliado,
        ud.revenue_afiliado_usd,
        ud.imposto_usd,
        ud.imposto_afiliado,
        ud.product_name_from_campaign,
        COALESCE(ud.clean_product_name, ud.product_name_from_campaign) AS resolved_product_name,
        COALESCE(nl.niche, nl2.niche) AS niche,
        dc.copywriter,
        dc.funil_hippie,
        ds.nome_squad,
        ds.lider AS lider_squad
    FROM (
        -- =================================================================
        -- 1) CARTPANDA + CLICKBANK + BUYGOODS
        -- =================================================================
        SELECT
            cp.created_at_date,
            LOWER(REGEXP_REPLACE(
                TRIM(CASE
                    WHEN cp.product_name LIKE '%-%'            THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                    WHEN REGEXP_LIKE(cp.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                    ELSE cp.product_name
                END), '[^a-zA-Z0-9]', '')) AS product_key,
            CONCAT(
                UPPER(LEFT(LOWER(REGEXP_REPLACE(TRIM(CASE
                    WHEN cp.product_name LIKE '%-%'            THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                    WHEN REGEXP_LIKE(cp.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                    ELSE cp.product_name END), '[^a-zA-Z0-9]', '')), 1)),
                SUBSTRING(LOWER(REGEXP_REPLACE(TRIM(CASE
                    WHEN cp.product_name LIKE '%-%'            THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                    WHEN REGEXP_LIKE(cp.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                    ELSE cp.product_name END), '[^a-zA-Z0-9]', '')), 2)
            ) AS clean_product_name,
            CASE
                WHEN cp.offer_name LIKE '%[Gestor de Tr_fego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Tráfego:', -1), ']', 1))
                WHEN cp.offer_name LIKE '%[Gestor de Trafego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Trafego:', -1), ']', 1))
                ELSE NULL
            END AS gestor_trafego,
            CASE
                WHEN cp.offer_name LIKE '%: [%]%'
                    THEN TRIM(REGEXP_REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, ': [', -1), ']', 1), '[^a-zA-Z0-9 ]', ''))
                ELSE NULL
            END AS traffic_source,
            NULLIF(cp.coupon_code, '') AS coupon_code,
            COUNT(*)                                         AS total_vendas,
            COALESCE(SUM(cp.total_price), 0)                 AS total_price,
            COALESCE(SUM(cp.total_price_usd), 0)             AS total_price_usd,
            COALESCE(SUM(cp.commission), 0)                  AS commission,
            COALESCE(SUM(cp.commission_usd), 0)              AS commission_usd,
            COALESCE(SUM(cp.taxes), 0)                       AS taxes,
            COALESCE(SUM(cp.taxes_usd), 0)                   AS taxes_usd,
            COALESCE(SUM(cp.total_refund), 0)                AS total_refund,
            COALESCE(SUM(cp.total_refund_usd), 0)            AS total_refund_usd,
            COALESCE(SUM(cp.product_cost), 0)                AS product_cost,
            COALESCE(SUM(cp.product_cost_usd), 0)            AS product_cost_usd,
            SUM(CASE WHEN cp.payment_status IN ('approved','refunded_partial') THEN cp.total_price * 0.03 ELSE 0 END) AS imposto,
            SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%1unit%' OR LOWER(cp.product_sku) LIKE '%2unit%' THEN 1 ELSE 0 END) AS `1_2_units_sales`,
            SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%3unit%' OR LOWER(cp.product_sku) LIKE '%4unit%' THEN 1 ELSE 0 END) AS `3_4_units_sales`,
            SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%5unit%' OR LOWER(cp.product_sku) LIKE '%6unit%' THEN 1 ELSE 0 END) AS `5_6_units_sales`,
            COALESCE(SUM(cp.has_order_bump), 0)              AS ob_count,
            COALESCE(SUM(cp.total_price_order_bump), 0)      AS ob_revenue,
            COALESCE(SUM(cp.total_price_order_bump_usd), 0)  AS ob_revenue_usd,
            COALESCE(SUM(cp.has_upsell), 0)                  AS up1_count,
            COALESCE(SUM(cp.total_price_upsell), 0)          AS up1_revenue,
            COALESCE(SUM(cp.total_price_upsell_usd), 0)      AS up1_revenue_usd,
            COALESCE(SUM(cp.has_upsell2), 0)                 AS up2_count,
            COALESCE(SUM(cp.total_price_upsell2), 0)         AS up2_revenue,
            COALESCE(SUM(cp.total_price_upsell2_usd), 0)     AS up2_revenue_usd,
            COALESCE(SUM(cp.has_upsell3), 0)                 AS up3_count,
            COALESCE(SUM(cp.total_price_upsell3), 0)         AS up3_revenue,
            COALESCE(SUM(cp.total_price_upsell3_usd), 0)     AS up3_revenue_usd,
            COALESCE(SUM(cp.has_downsell), 0)                AS down1_count,
            COALESCE(SUM(cp.total_price_downsell), 0)        AS down1_revenue,
            COALESCE(SUM(cp.total_price_downsell_usd), 0)    AS down1_revenue_usd,
            COALESCE(SUM(cp.has_downsell2), 0)               AS down2_count,
            COALESCE(SUM(cp.total_price_downsell2), 0)       AS down2_revenue,
            COALESCE(SUM(cp.total_price_downsell2_usd), 0)   AS down2_revenue_usd,
            COALESCE(SUM(cp.has_downsell3), 0)               AS down3_count,
            COALESCE(SUM(cp.total_price_downsell3), 0)       AS down3_revenue,
            COALESCE(SUM(cp.total_price_downsell3_usd), 0)   AS down3_revenue_usd,
            NULL AS amount_spent_brl,
            SUM(COALESCE(cp.cartpanda_retry, 0))             AS cartpanda_retry_count,
            SUM(CASE WHEN COALESCE(cp.cartpanda_retry,0) = 1 THEN cp.total_price ELSE 0 END) AS cartpanda_retry_revenue,
            SUM(CASE WHEN COALESCE(cp.cartpanda_retry,0) = 1 THEN cp.total_price_usd ELSE 0 END) AS cartpanda_retry_revenue_usd,
            NULL AS spent_taxes,
            NULL AS amount_spent_total,
            COALESCE(SUM(cp.revenue_afiliado), 0)            AS revenue_afiliado,
            COALESCE(SUM(cp.revenue_afiliado_usd), 0)        AS revenue_afiliado_usd,
            SUM(CASE WHEN cp.payment_status IN ('approved','refunded_partial') THEN cp.total_price_usd * 0.03 ELSE 0 END) AS imposto_usd,
            ROUND(COALESCE(SUM(cp.revenue_afiliado), 0) * 0.05, 4) AS imposto_afiliado,
            NULL AS product_name_from_campaign
        FROM (
            SELECT transaction_id, payment_status, client_name, client_email, client_phone,
                client_zip, client_country, client_state, client_city, client_street,
                product_name, offer_name, product_sku,
                product_cost, ROUND(product_cost        / 5.2, 2) AS product_cost_usd,
                quantity, total_price, ROUND(total_price         / 5.2, 2) AS total_price_usd,
                taxes,        ROUND(taxes                / 5.2, 2) AS taxes_usd,
                total_refund, ROUND(total_refund         / 5.2, 2) AS total_refund_usd,
                commission,   ROUND(commission           / 5.2, 2) AS commission_usd,
                NULL AS affiliate_amount, NULL AS affiliate_amount_usd,
                has_upsell, has_upsell2, has_upsell3,
                has_downsell, has_downsell2, has_downsell3, has_order_bump,
                total_price_upsell,   ROUND(total_price_upsell   / 5.2, 2) AS total_price_upsell_usd,
                total_price_upsell2,  ROUND(total_price_upsell2  / 5.2, 2) AS total_price_upsell2_usd,
                total_price_upsell3,  ROUND(total_price_upsell3  / 5.2, 2) AS total_price_upsell3_usd,
                total_price_downsell, ROUND(total_price_downsell / 5.2, 2) AS total_price_downsell_usd,
                total_price_downsell2,ROUND(total_price_downsell2/ 5.2, 2) AS total_price_downsell2_usd,
                total_price_downsell3,ROUND(total_price_downsell3/ 5.2, 2) AS total_price_downsell3_usd,
                total_price_order_bump, ROUND(total_price_order_bump / 5.2, 2) AS total_price_order_bump_usd,
                coupon_code, created_at_date, created_at_hour,
                NULL AS date_refunded,
                NULL AS utm_source, NULL AS utm_medium, NULL AS utm_content,
                NULL AS utm_term, NULL AS utm_campaign, NULL AS src,
                'cartpanda' AS platform, affiliate_name, NULL AS vendor_name,
                cartpanda_retry,
                NULL AS revenue_afiliado,
                NULL AS revenue_afiliado_usd
            FROM `instituto_experience`.`cartpanda_physical`
            WHERE created_at_date >= '2026-01-01'
              AND (affiliate_name IS NULL OR affiliate_name = '')
              AND client_email NOT LIKE '%institutoexperience%'
              AND LOWER(offer_name) NOT LIKE '%affiliate marketing%'
              AND offer_name LIKE '%Nova Ideia%'
              AND offer_name NOT LIKE '%Thales Pater%'
              AND offer_name NOT LIKE '%SEO Marketing%'
            UNION ALL
            SELECT transaction_id, payment_status, client_name, client_email, client_phone,
                client_zip, client_country, client_state, client_city, client_street,
                product_name, offer_name, CONCAT(quantity, 'unit') AS product_sku,
                product_cost, product_cost_usd,
                quantity, total_price, total_price_usd,
                taxes, taxes_usd, total_refund, total_refund_usd,
                commission, commission_usd, affiliate_amount, affiliate_amount_usd,
                has_upsell, has_upsell2, has_upsell3,
                has_downsell, has_downsell2, has_downsell3, has_order_bump,
                total_price_upsell, total_price_upsell_usd,
                total_price_upsell2, total_price_upsell2_usd,
                total_price_upsell3, total_price_upsell3_usd,
                total_price_downsell, total_price_downsell_usd,
                total_price_downsell2, total_price_downsell2_usd,
                total_price_downsell3, total_price_downsell3_usd,
                total_price_order_bump, total_price_order_bump_usd,
                coupon_code, created_at_date, created_at_hour, date_refunded,
                utm_source, utm_medium, utm_content, utm_term, utm_campaign, src,
                platform AS platform, affiliate_name, vendor_name,
                0 AS cartpanda_retry,
                revenue_afiliado,
                revenue_afiliado_usd
            FROM `instituto_experience`.`dashboard_gold_clickbank_buygoods`
            WHERE created_at_date >= '2026-01-01'
              AND is_house_traffic = 1
        ) cp
        WHERE cp.payment_status IN ('approved','refunded','chargeback','refunded_partial')
        GROUP BY
            cp.created_at_date, product_key, clean_product_name,
            CASE WHEN cp.offer_name LIKE '%[Gestor de Tr_fego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Tráfego:', -1), ']', 1))
                 WHEN cp.offer_name LIKE '%[Gestor de Trafego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Trafego:', -1), ']', 1))
                 ELSE NULL END,
            CASE WHEN cp.offer_name LIKE '%: [%]%'
                    THEN TRIM(REGEXP_REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, ': [', -1), ']', 1), '[^a-zA-Z0-9 ]', ''))
                 ELSE NULL END,
            NULLIF(cp.coupon_code, '')

        -- =================================================================
        -- 2) FACEBOOK ADS
        -- =================================================================
        UNION ALL
        SELECT
            ma.created_at_date,
            -- product_key: normalizado lowercase sem especiais (igual ao Cartpanda)
            LOWER(REGEXP_REPLACE(TRIM(SUBSTRING_INDEX(ma.campaign_name, ':', 1)), '[^a-zA-Z0-9]', '')) AS product_key,
            -- clean_product_name: primeira letra maiúscula (igual ao Cartpanda)
            CONCAT(
                UPPER(LEFT(LOWER(REGEXP_REPLACE(TRIM(SUBSTRING_INDEX(ma.campaign_name, ':', 1)), '[^a-zA-Z0-9]', '')), 1)),
                SUBSTRING(LOWER(REGEXP_REPLACE(TRIM(SUBSTRING_INDEX(ma.campaign_name, ':', 1)), '[^a-zA-Z0-9]', '')), 2)
            ) AS clean_product_name,
            CASE WHEN ma.campaign_name LIKE '%[Gestor de Tr_fego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Tráfego:', -1), ']', 1))
                 WHEN ma.campaign_name LIKE '%[Gestor de Trafego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Trafego:', -1), ']', 1))
                 ELSE NULL END,
            'Facebook Ads', NULL,
            NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
            NULL, NULL, NULL,
            NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
            NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
            COALESCE(SUM(ma.amount_spent_brl), 0), 0, 0, NULL,
            COALESCE(SUM(ma.spent_taxes), 0),
            COALESCE(SUM(ma.amount_spent_brl), 0) + COALESCE(SUM(ma.spent_taxes), 0),
            NULL, NULL, NULL, NULL,
            CONCAT(
                UPPER(LEFT(LOWER(REGEXP_REPLACE(TRIM(SUBSTRING_INDEX(ma.campaign_name, ':', 1)), '[^a-zA-Z0-9]', '')), 1)),
                SUBSTRING(LOWER(REGEXP_REPLACE(TRIM(SUBSTRING_INDEX(ma.campaign_name, ':', 1)), '[^a-zA-Z0-9]', '')), 2)
            )
        FROM `instituto_experience`.`meta_ad_id` ma FORCE INDEX (`idx_meta_ads_date`)
        WHERE ma.created_at_date >= '2026-01-01'
          AND ma.campaign_name LIKE '%Nova Ideia%'
          AND ma.campaign_name NOT LIKE '%Thales Pater%'
        GROUP BY ma.created_at_date,
            LOWER(REGEXP_REPLACE(TRIM(SUBSTRING_INDEX(ma.campaign_name, ':', 1)), '[^a-zA-Z0-9]', '')),
            CASE WHEN ma.campaign_name LIKE '%[Gestor de Tr_fego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Tráfego:', -1), ']', 1))
                 WHEN ma.campaign_name LIKE '%[Gestor de Trafego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Trafego:', -1), ']', 1))
                 ELSE NULL END
    ) ud

    LEFT JOIN (
        SELECT product_key, MAX(niche) AS niche
        FROM `instituto_experience`.`call_center_sales`
        WHERE nome_produto != 'Geral'
          AND nome_produto NOT LIKE '%Sem Nome%'
          AND nome_produto NOT LIKE '%Outros%'
        GROUP BY product_key
    ) nl ON ud.product_key = nl.product_key

    LEFT JOIN (
        SELECT
            CONCAT(
                UPPER(LEFT(LOWER(REGEXP_REPLACE(nome_produto, '[^a-zA-Z0-9]', '')), 1)),
                SUBSTRING(LOWER(REGEXP_REPLACE(nome_produto, '[^a-zA-Z0-9]', '')), 2)
            ) AS produto_normalizado,
            MAX(niche) AS niche
        FROM `instituto_experience`.`call_center_sales`
        WHERE nome_produto != 'Geral'
          AND nome_produto NOT LIKE '%Sem Nome%'
          AND nome_produto NOT LIKE '%Outros%'
        GROUP BY produto_normalizado
    ) nl2 ON ud.product_key IS NULL
          AND COALESCE(ud.clean_product_name, ud.product_name_from_campaign) = nl2.produto_normalizado

    LEFT JOIN instituto_experience.dim_copywriter dc
        ON COALESCE(ud.clean_product_name, ud.product_name_from_campaign)
            <=> CONCAT(
                UPPER(LEFT(LOWER(REGEXP_REPLACE(dc.produto, '[^a-zA-Z0-9]', '')), 1)),
                SUBSTRING(LOWER(REGEXP_REPLACE(dc.produto, '[^a-zA-Z0-9]', '')), 2)
            )
        AND ud.created_at_date BETWEEN dc.data_inicio AND dc.data_fim
        AND dc.is_current = 1

    LEFT JOIN instituto_experience.dim_squad ds
        ON  ud.traffic_source = ds.fonte
        AND ud.gestor_trafego = ds.gestor
        AND ds.is_current     = 1
),

-- =================================================================
-- ALTERAÇÃO: custo_usd vem direto da tabela; custo_brl = custo_usd * 5.2
-- =================================================================
ctg_agg AS (
    SELECT
        data, fonte, gestor,
        CONCAT(
            UPPER(LEFT(LOWER(REGEXP_REPLACE(produto, '[^a-zA-Z0-9]', '')), 1)),
            SUBSTRING(LOWER(REGEXP_REPLACE(produto, '[^a-zA-Z0-9]', '')), 2)
        ) AS produto,
        SUM(custo_usd)              AS custo_usd,
        SUM(custo_usd) * 5.2        AS custo_brl
    FROM `instituto_experience`.`custos_trafego_gestores_diaria`
    GROUP BY data, fonte, `custos_trafego_gestores_diaria`.produto, gestor
),

-- ALTERAÇÃO: valores da tabela agora são USD; BRL = valor * 5.2
cca_agg AS (
    SELECT
        data, fonte, gestor,
        CONCAT(
            UPPER(LEFT(LOWER(REGEXP_REPLACE(produto, '[^a-zA-Z0-9]', '')), 1)),
            SUBSTRING(LOWER(REGEXP_REPLACE(produto, '[^a-zA-Z0-9]', '')), 2)
        ) AS produto,
        SUM(taxa)            AS taxa_usd,
        SUM(taxa) * 5.2      AS taxa,
        SUM(custo)           AS custo_usd,
        SUM(custo) * 5.2     AS custo,
        SUM(custo_real)      AS custo_real_usd,
        SUM(custo_real) * 5.2 AS custo_real
    FROM `instituto_experience`.`custos_conta_agencia_diaria`
    GROUP BY data, fonte, `custos_conta_agencia_diaria`.produto, gestor
),

-- =================================================================
-- CORREÇÃO: cg_agg — agrega por (data, fonte) apenas, sem produto/gestor.
-- O valor total por fonte/dia será distribuído proporcionalmente
-- por receita no SELECT FINAL, evitando duplicação por fan-out.
-- =================================================================
cg_agg AS (
    SELECT
        data,
        fonte,
        SUM(custo) AS custos_gerais
    FROM `instituto_experience`.`custos_gerais_diaria`
    GROUP BY data, fonte
),

-- =================================================================
-- RESULTADO ANTES DA REDISTRIBUIÇÃO
-- CORREÇÃO: removido o LEFT JOIN com cg_agg daqui.
-- O custo geral será aplicado somente no SELECT FINAL,
-- após o cálculo do peso proporcional por receita.
-- =================================================================
pre_final AS (
    SELECT
        u.created_at_date,
        COALESCE(u.resolved_product_name, 'Não encontrado') AS clean_product_name,
        COALESCE(u.gestor_trafego,  'Não encontrado') AS gestor_trafego,
        COALESCE(u.traffic_source,  'Não encontrado') AS traffic_source,
        u.coupon_code,
        COALESCE(u.niche,        'Não encontrado') AS niche,
        COALESCE(u.copywriter,   'Não encontrado') AS copywriter,
        COALESCE(u.funil_hippie, 'Não encontrado') AS funil_hippie,
        COALESCE(u.nome_squad,   'Não encontrado') AS nome_squad,
        COALESCE(u.lider_squad,  'Não encontrado') AS lider_squad,
        u.total_vendas,
        u.total_price,
        u.total_price_usd,
        u.commission,
        u.commission_usd,
        u.taxes,
        u.taxes_usd,
        u.total_refund,
        u.total_refund_usd,
        u.product_cost,
        u.product_cost_usd,
        u.imposto,
        u.`1_2_units_sales`,
        u.`3_4_units_sales`,
        u.`5_6_units_sales`,
        u.ob_count, u.ob_revenue, u.ob_revenue_usd,
        u.up1_count, u.up1_revenue, u.up1_revenue_usd,
        u.up2_count, u.up2_revenue, u.up2_revenue_usd,
        u.up3_count, u.up3_revenue, u.up3_revenue_usd,
        u.down1_count, u.down1_revenue, u.down1_revenue_usd,
        u.down2_count, u.down2_revenue, u.down2_revenue_usd,
        u.down3_count, u.down3_revenue, u.down3_revenue_usd,
        u.revenue_no_funnel,
        u.revenue_no_funnel_usd,
        u.amount_spent_brl,
        u.cartpanda_retry_count,
        u.cartpanda_retry_revenue,
        u.cartpanda_retry_revenue_usd,
        u.spent_taxes,
        u.amount_spent_total,
        u.revenue_afiliado,
        u.revenue_afiliado_usd,
        ctg.custo_brl        AS ctg_custo_brl,
        -- CORREÇÃO: ctg_custos_gerais removido daqui — será calculado no SELECT FINAL
        cca.taxa             AS cca_taxa,
        cca.custo            AS cca_custo,
        cca.custo_real       AS cca_custo_real,
        u.imposto_usd,
        ROUND(u.amount_spent_brl / 5.2, 2)      AS amount_spent_usd,
        ROUND(u.spent_taxes / 5.2, 2)           AS spent_taxes_usd,
        ROUND(u.amount_spent_total / 5.2, 2)    AS amount_spent_total_usd,
        u.imposto_afiliado,
        ROUND(u.revenue_afiliado_usd * 0.05, 2) AS imposto_afiliado_usd,
        ctg.custo_usd                           AS ctg_custo_usd,
        cca.taxa_usd                            AS cca_taxa_usd,
        cca.custo_usd                           AS cca_custo_usd,
        cca.custo_real_usd                      AS cca_custo_real_usd
    FROM ud_base u
    LEFT JOIN ctg_agg ctg
        ON  u.created_at_date        = ctg.data
        AND u.traffic_source         = ctg.fonte
        AND u.resolved_product_name <=> ctg.produto
        AND u.gestor_trafego        <=> ctg.gestor
        AND u.amount_spent_brl IS NULL
    LEFT JOIN cca_agg cca
        ON  u.created_at_date        = cca.data
        AND u.traffic_source         = cca.fonte
        AND u.resolved_product_name <=> cca.produto
        AND u.gestor_trafego        <=> cca.gestor
        AND u.amount_spent_brl IS NULL
    -- CORREÇÃO: LEFT JOIN cg_agg removido daqui

    UNION ALL
    SELECT
        ctg2.data,
        COALESCE(ctg2.produto, 'Não encontrado'),
        COALESCE(ctg2.gestor, 'Não encontrado'),
        'Não encontrado', NULL, 'Não encontrado',
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL, NULL,
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL,
        NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL,
        'Não encontrado', 'Não encontrado', 'Não encontrado', 'Não encontrado', 'Não encontrado',
        ROUND(ctg2.custo_usd * 5.2, 2),
        NULL, NULL, NULL,
        NULL, NULL, NULL, NULL, NULL,
        ctg2.custo_usd, NULL,
        NULL, NULL, NULL
    FROM ctg_agg ctg2
    WHERE NOT EXISTS (
        SELECT 1 FROM ud_base u2
        WHERE u2.created_at_date        = ctg2.data
          AND u2.traffic_source         = ctg2.fonte
          AND u2.resolved_product_name <=> ctg2.produto
          AND u2.gestor_trafego        <=> ctg2.gestor
    )

    UNION ALL
    SELECT
        cca2.data,
        COALESCE(cca2.produto, 'Não encontrado'),
        COALESCE(cca2.gestor, 'Não encontrado'),
        'Não encontrado', NULL, 'Não encontrado',
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL, NULL,
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL,
        NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL,
        'Não encontrado', 'Não encontrado', 'Não encontrado', 'Não encontrado', 'Não encontrado',
        NULL,
        -- CORREÇÃO: ctg_custos_gerais removido — posição suprimida
        -- ALTERAÇÃO: cca — BRL = valor * 5.2; USD = valor direto da tabela
        cca2.taxa, cca2.custo, cca2.custo_real,
        NULL, NULL, NULL, NULL, NULL, NULL,
        NULL,
        cca2.taxa_usd, cca2.custo_usd, cca2.custo_real_usd
    FROM cca_agg cca2
    WHERE NOT EXISTS (
        SELECT 1 FROM ud_base u3
        WHERE u3.created_at_date        = cca2.data
          AND u3.traffic_source         = cca2.fonte
          AND u3.resolved_product_name <=> cca2.produto
          AND u3.gestor_trafego        <=> cca2.gestor
    )

    -- =================================================================
    -- CORREÇÃO: orphan rows de custos_gerais_diaria.
    -- Garante que dias com custo geral mas sem vendas na ud_base
    -- não percam o valor no JOIN do SELECT FINAL.
    -- =================================================================
    UNION ALL
    SELECT
        cg3.data,
        'Não encontrado',
        'Não encontrado',
        cg3.fonte, NULL, 'Não encontrado',
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL, NULL,
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL,
        NULL, NULL, NULL, NULL, NULL, NULL,
        NULL, NULL,
        'Não encontrado', 'Não encontrado', 'Não encontrado', 'Não encontrado', 'Não encontrado',
        NULL,
        NULL, NULL, NULL,
        NULL, NULL, NULL, NULL, NULL,
        NULL, NULL,
        NULL, NULL, NULL
    FROM cg_agg cg3
    WHERE NOT EXISTS (
        SELECT 1 FROM ud_base u4
        WHERE u4.created_at_date = cg3.data
          AND u4.traffic_source  = cg3.fonte
    )
),

-- =================================================================
-- REDISTRIBUIÇÃO PROPORCIONAL — Back Redirect e Thumb Recuperação
-- =================================================================
sec AS (
    SELECT
        created_at_date,
        gestor_trafego,
        clean_product_name,
        SUM(total_vendas)               AS s_total_vendas,
        SUM(total_price)                AS s_total_price,
        SUM(total_price_usd)            AS s_total_price_usd,
        SUM(commission)                 AS s_commission,
        SUM(commission_usd)             AS s_commission_usd,
        SUM(taxes)                      AS s_taxes,
        SUM(taxes_usd)                  AS s_taxes_usd,
        SUM(total_refund)               AS s_total_refund,
        SUM(total_refund_usd)           AS s_total_refund_usd,
        SUM(product_cost)               AS s_product_cost,
        SUM(product_cost_usd)           AS s_product_cost_usd,
        SUM(imposto)                    AS s_imposto,
        SUM(`1_2_units_sales`)          AS s_1_2_units_sales,
        SUM(`3_4_units_sales`)          AS s_3_4_units_sales,
        SUM(`5_6_units_sales`)          AS s_5_6_units_sales,
        SUM(ob_count)                   AS s_ob_count,
        SUM(ob_revenue)                 AS s_ob_revenue,
        SUM(ob_revenue_usd)             AS s_ob_revenue_usd,
        SUM(up1_count)                  AS s_up1_count,
        SUM(up1_revenue)                AS s_up1_revenue,
        SUM(up1_revenue_usd)            AS s_up1_revenue_usd,
        SUM(up2_count)                  AS s_up2_count,
        SUM(up2_revenue)                AS s_up2_revenue,
        SUM(up2_revenue_usd)            AS s_up2_revenue_usd,
        SUM(up3_count)                  AS s_up3_count,
        SUM(up3_revenue)                AS s_up3_revenue,
        SUM(up3_revenue_usd)            AS s_up3_revenue_usd,
        SUM(down1_count)                AS s_down1_count,
        SUM(down1_revenue)              AS s_down1_revenue,
        SUM(down1_revenue_usd)          AS s_down1_revenue_usd,
        SUM(down2_count)                AS s_down2_count,
        SUM(down2_revenue)              AS s_down2_revenue,
        SUM(down2_revenue_usd)          AS s_down2_revenue_usd,
        SUM(down3_count)                AS s_down3_count,
        SUM(down3_revenue)              AS s_down3_revenue,
        SUM(down3_revenue_usd)          AS s_down3_revenue_usd,
        SUM(revenue_no_funnel)          AS s_revenue_no_funnel,
        SUM(revenue_no_funnel_usd)      AS s_revenue_no_funnel_usd,
        SUM(cartpanda_retry_count)      AS s_cartpanda_retry_count,
        SUM(cartpanda_retry_revenue)    AS s_cartpanda_retry_revenue,
        SUM(cartpanda_retry_revenue_usd) AS s_cartpanda_retry_revenue_usd,
        SUM(revenue_afiliado)           AS s_revenue_afiliado,
        SUM(revenue_afiliado_usd)       AS s_revenue_afiliado_usd,
        SUM(imposto_usd)                AS s_imposto_usd,
        SUM(imposto_afiliado)           AS s_imposto_afiliado,
        SUM(imposto_afiliado_usd)       AS s_imposto_afiliado_usd
    FROM pre_final
    WHERE traffic_source IN ('Thumb Recuperao', 'Back Redirect', 'Back Redireck')
    GROUP BY created_at_date, gestor_trafego, clean_product_name
),

pri AS (
    SELECT
        p.*,
        SUM(COALESCE(p.total_price, 0)) OVER (
            PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name
        ) AS total_price_primario,
        -- =================================================================
        -- CORREÇÃO: denominador para distribuição proporcional do custo geral.
        -- Particiona apenas por (data, traffic_source), que é a granularidade
        -- da cg_agg — assim o peso de cada linha reflete sua fatia de receita
        -- dentro da fonte naquele dia, sem duplicar o valor total.
        -- =================================================================
        SUM(COALESCE(p.total_price, 0)) OVER (
            PARTITION BY p.created_at_date, p.traffic_source
        ) AS total_price_por_fonte,
        ROW_NUMBER() OVER (
            PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name
            ORDER BY COALESCE(p.total_price, 0) DESC
        ) AS rn,
        COUNT(*) OVER (
            PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name
        ) AS cnt_fontes
    FROM pre_final p
    WHERE p.traffic_source NOT IN ('Thumb Recuperao', 'Back Redirect', 'Back Redireck')
)

-- =================================================================
-- SELECT FINAL — primárias com redistribuição + resíduo na maior
-- CORREÇÃO: ctg_custos_gerais calculado aqui via LEFT JOIN com cg_agg,
-- distribuído proporcionalmente por (total_price / total_price_por_fonte).
-- Isso garante que o total agregado por fonte/dia sempre bata com a fonte,
-- independente de quantas linhas de produto/gestor/funil existam.
-- =================================================================
SELECT
    p.created_at_date,
    p.clean_product_name,
    p.gestor_trafego,
    p.traffic_source,
    p.coupon_code,
    p.niche,
    p.copywriter,
    p.funil_hippie,
    p.nome_squad,
    p.lider_squad,

    COALESCE(p.total_vendas, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_total_vendas - SUM(FLOOR(s.s_total_vendas * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_total_vendas * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS total_vendas,

    ROUND(COALESCE(p.total_price, 0) + COALESCE(s.s_total_price * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS total_price,
    ROUND(COALESCE(p.total_price_usd, 0) + COALESCE(s.s_total_price_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS total_price_usd,
    ROUND(COALESCE(p.commission, 0) + COALESCE(s.s_commission * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS commission,
    ROUND(COALESCE(p.commission_usd, 0) + COALESCE(s.s_commission_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS commission_usd,
    ROUND(COALESCE(p.taxes, 0) + COALESCE(s.s_taxes * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS taxes,
    ROUND(COALESCE(p.taxes_usd, 0) + COALESCE(s.s_taxes_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS taxes_usd,
    ROUND(COALESCE(p.total_refund, 0) + COALESCE(s.s_total_refund * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS total_refund,
    ROUND(COALESCE(p.total_refund_usd, 0) + COALESCE(s.s_total_refund_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS total_refund_usd,
    ROUND(COALESCE(p.product_cost, 0) + COALESCE(s.s_product_cost * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS product_cost,
    ROUND(COALESCE(p.product_cost_usd, 0) + COALESCE(s.s_product_cost_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS product_cost_usd,
    ROUND(COALESCE(p.imposto, 0) + COALESCE(s.s_imposto * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS imposto,

    COALESCE(p.`1_2_units_sales`, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_1_2_units_sales - SUM(FLOOR(s.s_1_2_units_sales * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_1_2_units_sales * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS `1_2_units_sales`,

    COALESCE(p.`3_4_units_sales`, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_3_4_units_sales - SUM(FLOOR(s.s_3_4_units_sales * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_3_4_units_sales * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS `3_4_units_sales`,

    COALESCE(p.`5_6_units_sales`, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_5_6_units_sales - SUM(FLOOR(s.s_5_6_units_sales * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_5_6_units_sales * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS `5_6_units_sales`,

    COALESCE(p.ob_count, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_ob_count - SUM(FLOOR(s.s_ob_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_ob_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS ob_count,
    ROUND(COALESCE(p.ob_revenue, 0) + COALESCE(s.s_ob_revenue * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS ob_revenue,
    ROUND(COALESCE(p.ob_revenue_usd, 0) + COALESCE(s.s_ob_revenue_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS ob_revenue_usd,

    COALESCE(p.up1_count, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_up1_count - SUM(FLOOR(s.s_up1_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_up1_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS up1_count,
    ROUND(COALESCE(p.up1_revenue, 0) + COALESCE(s.s_up1_revenue * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS up1_revenue,
    ROUND(COALESCE(p.up1_revenue_usd, 0) + COALESCE(s.s_up1_revenue_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS up1_revenue_usd,

    COALESCE(p.up2_count, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_up2_count - SUM(FLOOR(s.s_up2_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_up2_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS up2_count,
    ROUND(COALESCE(p.up2_revenue, 0) + COALESCE(s.s_up2_revenue * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS up2_revenue,
    ROUND(COALESCE(p.up2_revenue_usd, 0) + COALESCE(s.s_up2_revenue_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS up2_revenue_usd,

    COALESCE(p.up3_count, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_up3_count - SUM(FLOOR(s.s_up3_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_up3_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS up3_count,
    ROUND(COALESCE(p.up3_revenue, 0) + COALESCE(s.s_up3_revenue * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS up3_revenue,
    ROUND(COALESCE(p.up3_revenue_usd, 0) + COALESCE(s.s_up3_revenue_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS up3_revenue_usd,

    COALESCE(p.down1_count, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_down1_count - SUM(FLOOR(s.s_down1_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_down1_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS down1_count,
    ROUND(COALESCE(p.down1_revenue, 0) + COALESCE(s.s_down1_revenue * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS down1_revenue,
    ROUND(COALESCE(p.down1_revenue_usd, 0) + COALESCE(s.s_down1_revenue_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS down1_revenue_usd,

    COALESCE(p.down2_count, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_down2_count - SUM(FLOOR(s.s_down2_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_down2_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS down2_count,
    ROUND(COALESCE(p.down2_revenue, 0) + COALESCE(s.s_down2_revenue * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS down2_revenue,
    ROUND(COALESCE(p.down2_revenue_usd, 0) + COALESCE(s.s_down2_revenue_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS down2_revenue_usd,

    COALESCE(p.down3_count, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_down3_count - SUM(FLOOR(s.s_down3_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_down3_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS down3_count,
    ROUND(COALESCE(p.down3_revenue, 0) + COALESCE(s.s_down3_revenue * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS down3_revenue,
    ROUND(COALESCE(p.down3_revenue_usd, 0) + COALESCE(s.s_down3_revenue_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS down3_revenue_usd,

    ROUND(COALESCE(p.revenue_no_funnel, 0) + COALESCE(s.s_revenue_no_funnel * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS revenue_no_funnel,
    ROUND(COALESCE(p.revenue_no_funnel_usd, 0) + COALESCE(s.s_revenue_no_funnel_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS revenue_no_funnel_usd,

    p.amount_spent_brl,

    COALESCE(p.cartpanda_retry_count, 0) + COALESCE(
        CASE WHEN p.rn = 1
            THEN s.s_cartpanda_retry_count - SUM(FLOOR(s.s_cartpanda_retry_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))) OVER (PARTITION BY p.created_at_date, p.gestor_trafego, p.clean_product_name)
            ELSE FLOOR(s.s_cartpanda_retry_count * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)))
        END, 0) AS cartpanda_retry_count,
    ROUND(COALESCE(p.cartpanda_retry_revenue, 0) + COALESCE(s.s_cartpanda_retry_revenue * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS cartpanda_retry_revenue,
    ROUND(COALESCE(p.cartpanda_retry_revenue_usd, 0) + COALESCE(s.s_cartpanda_retry_revenue_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS cartpanda_retry_revenue_usd,

    p.spent_taxes,
    p.amount_spent_total,

    ROUND(COALESCE(p.revenue_afiliado, 0) + COALESCE(s.s_revenue_afiliado * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS revenue_afiliado,
    ROUND(COALESCE(p.revenue_afiliado_usd, 0) + COALESCE(s.s_revenue_afiliado_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS revenue_afiliado_usd,

    p.ctg_custo_brl,

    -- =================================================================
    -- CORREÇÃO: ctg_custos_gerais distribuído proporcionalmente por receita.
    -- O JOIN é feito aqui no SELECT FINAL, após o cálculo do total_price_por_fonte.
    -- Peso = total_price da linha / total_price_por_fonte (soma da fonte no dia).
    -- Isso garante que SUM(ctg_custos_gerais) por (data, fonte) = valor exato da cg_agg,
    -- sem duplicações independente da granularidade de produto/gestor/funil.
    -- =================================================================
    CASE
        WHEN NULLIF(p.total_price_por_fonte, 0) IS NULL
            THEN cg.custos_gerais
        ELSE ROUND(cg.custos_gerais * (COALESCE(p.total_price, 0) / p.total_price_por_fonte), 2)
    END AS ctg_custos_gerais,

    p.cca_taxa,
    p.cca_custo,
    p.cca_custo_real,

    ROUND(COALESCE(p.imposto_usd, 0) + COALESCE(s.s_imposto_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS imposto_usd,
    ROUND(COALESCE(p.amount_spent_brl, 0) / 5.2, 2)      AS amount_spent_usd,
    ROUND(COALESCE(p.spent_taxes, 0) / 5.2, 2)           AS spent_taxes_usd,
    ROUND(COALESCE(p.amount_spent_total, 0) / 5.2, 2)    AS amount_spent_total_usd,
    ROUND(COALESCE(p.imposto_afiliado, 0) + COALESCE(s.s_imposto_afiliado * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 4) AS imposto_afiliado,
    ROUND(COALESCE(p.imposto_afiliado_usd, 0) + COALESCE(s.s_imposto_afiliado_usd * (COALESCE(p.total_price, 0) / NULLIF(p.total_price_primario, 0)), 0), 2) AS imposto_afiliado_usd,
    p.ctg_custo_usd,
    -- CORREÇÃO: ctg_custos_gerais_usd também distribuído proporcionalmente (BRL / 5.2)
    CASE
        WHEN NULLIF(p.total_price_por_fonte, 0) IS NULL
            THEN ROUND(cg.custos_gerais / 5.2, 2)
        ELSE ROUND(cg.custos_gerais * (COALESCE(p.total_price, 0) / p.total_price_por_fonte) / 5.2, 2)
    END AS ctg_custos_gerais_usd,
    p.cca_taxa_usd,
    p.cca_custo_usd,
    p.cca_custo_real_usd

FROM pri p
LEFT JOIN sec s
    ON  p.created_at_date    = s.created_at_date
    AND p.gestor_trafego     = s.gestor_trafego
    AND p.clean_product_name = s.clean_product_name
-- =================================================================
-- CORREÇÃO: JOIN com cg_agg movido para cá, após total_price_por_fonte
-- já estar calculado em pri. Granularidade do join: (data, fonte) apenas.
-- =================================================================
LEFT JOIN cg_agg cg
    ON  p.created_at_date = cg.data
    AND p.traffic_source  = cg.fonte;

    RENAME TABLE
        instituto_experience.dashboard_internal_sales_v2       TO instituto_experience.dashboard_internal_sales_v2_old,
        instituto_experience.dashboard_internal_sales_v2_stage TO instituto_experience.dashboard_internal_sales_v2,
        instituto_experience.dashboard_internal_sales_v2_old   TO instituto_experience.dashboard_internal_sales_v2_stage;

END
```
