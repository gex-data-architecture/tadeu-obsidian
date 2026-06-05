---
tipo: procedure
definer: "root@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-02-16 16:34:35"
alterada_em: "2026-02-16 16:34:35"
execucoes: ""
tags: [rotina, procedure]
---

# refresh_dashboard_internal_sales

## Dependências

- **Lê:** [[call_center_sales]], [[cartpanda_physical]], [[funil_produto_mapping]], [[google_ad_id]], [[meta_ad_id]], [[taboola_ad_id]]
- **Escreve:** [[dashboard_internal_sales]]
- **Cria:** —
- **Trunca:** [[dashboard_internal_sales]]
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN

    TRUNCATE TABLE `instituto_experience`.`dashboard_internal_sales`;

    INSERT INTO `instituto_experience`.`dashboard_internal_sales` (
        created_at_date,
        clean_product_name,
        platform,
        gestor_trafego,
        funil_id,
        traffic_source,
        coupon_code,
        niche,
        total_vendas,
        total_price,
        commission,
        taxes,
        total_refund,
        product_cost,
        imposto,
        `1_2_units_sales`,
        `3_4_units_sales`,
        `5_6_units_sales`,
        ob_count,
        ob_revenue,
        up1_count,
        up1_revenue,
        up2_count,
        up2_revenue,
        up3_count,
        up3_revenue,
        down1_count,
        down1_revenue,
        down2_count,
        down2_revenue,
        down3_count,
        down3_revenue,
        revenue_no_funnel,
        amount_spent_brl,
        cartpanda_retry_count,
        cartpanda_retry_revenue,
        spent_taxes,
        amount_spent_total
    )

    SELECT
        ud.created_at_date,

        COALESCE(
                ud.clean_product_name,
                CONCAT(
                        UPPER(LEFT(LOWER(REGEXP_REPLACE(fpm.clean_product_name, '[^a-zA-Z0-9]', '')), 1)),
                        SUBSTRING(LOWER(REGEXP_REPLACE(fpm.clean_product_name, '[^a-zA-Z0-9]', '')), 2)
                )
        ),

        ud.platform,
        ud.gestor_trafego,
        ud.funil_id,
        ud.traffic_source,
        ud.coupon_code,
        nl.niche,

        ud.total_vendas,
        ud.total_price,
        ud.commission,
        ud.taxes,
        ud.total_refund,
        ud.product_cost,
        ud.imposto,

        ud.`1_2_units_sales`,
        ud.`3_4_units_sales`,
        ud.`5_6_units_sales`,

        ud.ob_count,
        ud.ob_revenue,
        ud.up1_count,
        ud.up1_revenue,
        ud.up2_count,
        ud.up2_revenue,
        ud.up3_count,
        ud.up3_revenue,
        ud.down1_count,
        ud.down1_revenue,
        ud.down2_count,
        ud.down2_revenue,
        ud.down3_count,
        ud.down3_revenue,

        (ud.total_price - (
            ud.ob_revenue + ud.up1_revenue + ud.up2_revenue + ud.up3_revenue
                + ud.down1_revenue + ud.down2_revenue + ud.down3_revenue
            )),

        ud.amount_spent_brl,

        ud.cartpanda_retry_count,
        ud.cartpanda_retry_revenue,
        ud.spent_taxes,
        ud.amount_spent_total

    FROM (

             -- =================================================================
             -- 1) CARTPANDA
             -- =================================================================
             SELECT
                 cp.created_at_date,

                 LOWER(REGEXP_REPLACE(
                         TRIM(CASE
                                  WHEN cp.product_name LIKE '%-%'
                                      THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                  WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                      THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                  ELSE cp.product_name
                             END),
                         '[^a-zA-Z0-9]', ''
                       ))                                          AS `product_key`,

                 CONCAT(
                         UPPER(LEFT(
                                 LOWER(REGEXP_REPLACE(
                                         TRIM(CASE
                                                  WHEN cp.product_name LIKE '%-%'
                                                      THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                                  WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                                      THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                                  ELSE cp.product_name
                                             END),
                                         '[^a-zA-Z0-9]', ''
                                       )), 1
                               )),
                         SUBSTRING(
                                 LOWER(REGEXP_REPLACE(
                                         TRIM(CASE
                                                  WHEN cp.product_name LIKE '%-%'
                                                      THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                                  WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                                      THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                                  ELSE cp.product_name
                                             END),
                                         '[^a-zA-Z0-9]', ''
                                       )), 2
                         )
                 )                                           AS `clean_product_name`,

                 'cartpanda'                                 AS `platform`,

                 CASE
                     WHEN cp.offer_name LIKE '%[Gestor de Tr_fego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Tráfego:', -1), ']', 1))
                     WHEN cp.offer_name LIKE '%[Gestor de Trafego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Trafego:', -1), ']', 1))
                     ELSE NULL
                     END                                         AS `gestor_trafego`,

                 CASE
                     WHEN cp.offer_name LIKE '%Funil de Nova Ideia #%'
                         THEN CONCAT('Funil de Nova Ideia #',
                                     SUBSTRING_INDEX(
                                             REGEXP_SUBSTR(SUBSTRING_INDEX(cp.offer_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'),
                                             ' ', 1
                                     ))
                     ELSE NULL
                     END                                         AS `funil_id`,

                 CASE
                     WHEN cp.offer_name LIKE '%: [%]%'
                         THEN TRIM(REGEXP_REPLACE(
                             SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, ': [', -1), ']', 1),
                             '[^a-zA-Z0-9 ]', ''
                                   ))
                     ELSE NULL
                     END                                         AS `traffic_source`,

                 NULLIF(cp.coupon_code, '')                  AS `coupon_code`,

                 COUNT(*)                                    AS `total_vendas`,
                 COALESCE(SUM(cp.total_price), 0)            AS `total_price`,
                 COALESCE(SUM(cp.commission), 0)             AS `commission`,
                 COALESCE(SUM(cp.taxes), 0)                  AS `taxes`,
                 COALESCE(SUM(cp.total_refund), 0)           AS `total_refund`,
                 COALESCE(SUM(cp.product_cost), 0)           AS `product_cost`,

                 SUM(CASE
                         WHEN cp.payment_status IN ('approved', 'refunded_partial')
                             THEN cp.total_price * 0.03
                         ELSE 0
                     END)                                        AS `imposto`,

                 SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%1unit%' OR LOWER(cp.product_sku) LIKE '%2unit%' THEN 1 ELSE 0 END)
                                                                   AS `1_2_units_sales`,
                 SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%3unit%' OR LOWER(cp.product_sku) LIKE '%4unit%' THEN 1 ELSE 0 END)
                                                                   AS `3_4_units_sales`,
                 SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%5unit%' OR LOWER(cp.product_sku) LIKE '%6unit%' THEN 1 ELSE 0 END)
                                                                   AS `5_6_units_sales`,

                 COALESCE(SUM(cp.has_order_bump), 0)         AS `ob_count`,
                 COALESCE(SUM(cp.total_price_order_bump), 0) AS `ob_revenue`,
                 COALESCE(SUM(cp.has_upsell), 0)             AS `up1_count`,
                 COALESCE(SUM(cp.total_price_upsell), 0)     AS `up1_revenue`,
                 COALESCE(SUM(cp.has_upsell2), 0)            AS `up2_count`,
                 COALESCE(SUM(cp.total_price_upsell2), 0)    AS `up2_revenue`,
                 COALESCE(SUM(cp.has_upsell3), 0)            AS `up3_count`,
                 COALESCE(SUM(cp.total_price_upsell3), 0)    AS `up3_revenue`,
                 COALESCE(SUM(cp.has_downsell), 0)           AS `down1_count`,
                 COALESCE(SUM(cp.total_price_downsell), 0)   AS `down1_revenue`,
                 COALESCE(SUM(cp.has_downsell2), 0)          AS `down2_count`,
                 COALESCE(SUM(cp.total_price_downsell2), 0)  AS `down2_revenue`,
                 COALESCE(SUM(cp.has_downsell3), 0)          AS `down3_count`,
                 COALESCE(SUM(cp.total_price_downsell3), 0)  AS `down3_revenue`,

                 NULL                                        AS `amount_spent_brl`,

                 SUM(COALESCE(cp.cartpanda_retry, 0))        AS `cartpanda_retry_count`,
                 SUM(CASE
                         WHEN COALESCE(cp.cartpanda_retry, 0) = 1
                             THEN cp.total_price
                         ELSE 0
                     END)                                        AS `cartpanda_retry_revenue`,

                 NULL                                        AS `spent_taxes`,

                 NULL                                        AS `amount_spent_total`

             FROM `instituto_experience`.`cartpanda_physical` cp FORCE INDEX (`idx_cp_created_date`)
             WHERE cp.created_at_date >= '2025-09-01'
               AND cp.payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
               AND (cp.affiliate_name IS NULL OR cp.affiliate_name = '')
               AND cp.client_email NOT LIKE '%institutoexperience%'
               AND LOWER(cp.offer_name) NOT LIKE '%affiliate marketing%'
               AND cp.offer_name LIKE '%Nova Ideia%'
               AND cp.offer_name NOT LIKE '%Thales Pater%'
               AND cp.offer_name NOT LIKE '%SEO Marketing%'

             GROUP BY
                 cp.created_at_date,
                 `product_key`,
                 `clean_product_name`,
                 CASE
                     WHEN cp.offer_name LIKE '%[Gestor de Tr_fego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Tráfego:', -1), ']', 1))
                     WHEN cp.offer_name LIKE '%[Gestor de Trafego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Trafego:', -1), ']', 1))
                     ELSE NULL
                     END,
                 CASE
                     WHEN cp.offer_name LIKE '%Funil de Nova Ideia #%'
                         THEN CONCAT('Funil de Nova Ideia #',
                                     SUBSTRING_INDEX(
                                             REGEXP_SUBSTR(SUBSTRING_INDEX(cp.offer_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'),
                                             ' ', 1
                                     ))
                     ELSE NULL
                     END,
                 CASE
                     WHEN cp.offer_name LIKE '%: [%]%'
                         THEN TRIM(REGEXP_REPLACE(
                             SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, ': [', -1), ']', 1),
                             '[^a-zA-Z0-9 ]', ''
                                   ))
                     ELSE NULL
                     END,
                 NULLIF(cp.coupon_code, '')

             -- =================================================================
             -- 2) TABOOLA ADS
             -- =================================================================
             UNION ALL
             SELECT
                 tb.created_at_date,
                 NULL, NULL,
                 'taboola-ads',

                 CASE
                     WHEN tb.campaign_name LIKE '%[Gestor de Tr_fego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(tb.campaign_name, '[Gestor de Tráfego:', -1), ']', 1))
                     WHEN tb.campaign_name LIKE '%[Gestor de Trafego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(tb.campaign_name, '[Gestor de Trafego:', -1), ']', 1))
                     ELSE NULL
                     END,

                 CASE
                     WHEN tb.campaign_name LIKE '%Funil de Nova Ideia #%'
                         THEN CONCAT('Funil de Nova Ideia #',
                                     SUBSTRING_INDEX(
                                             REGEXP_SUBSTR(SUBSTRING_INDEX(tb.campaign_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'),
                                             ' ', 1
                                     ))
                     ELSE NULL
                     END,

                 'Taboola Ads',
                 NULL,

                 NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                 NULL, NULL, NULL,
                 NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                 NULL, NULL, NULL, NULL, NULL, NULL,

                 COALESCE(SUM(tb.amount_spent_brl), 0),

                 0, 0,

                 NULL,

                 COALESCE(SUM(tb.amount_spent_brl), 0)

             FROM `instituto_experience`.`taboola_ad_id` tb FORCE INDEX (`idx_taboola_ads_date`)
             WHERE tb.created_at_date >= '2025-09-01'
               AND tb.campaign_name LIKE '%Nova Ideia%'
               AND tb.campaign_name NOT LIKE '%Thales Pater%'

             GROUP BY
                 tb.created_at_date,
                 CASE
                     WHEN tb.campaign_name LIKE '%[Gestor de Tr_fego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(tb.campaign_name, '[Gestor de Tráfego:', -1), ']', 1))
                     WHEN tb.campaign_name LIKE '%[Gestor de Trafego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(tb.campaign_name, '[Gestor de Trafego:', -1), ']', 1))
                     ELSE NULL
                     END,
                 CASE
                     WHEN tb.campaign_name LIKE '%Funil de Nova Ideia #%'
                         THEN CONCAT('Funil de Nova Ideia #',
                                     SUBSTRING_INDEX(
                                             REGEXP_SUBSTR(SUBSTRING_INDEX(tb.campaign_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'),
                                             ' ', 1
                                     ))
                     ELSE NULL
                     END

             -- =================================================================
             -- 3) FACEBOOK ADS
             -- =================================================================
             UNION ALL
             SELECT
                 ma.created_at_date,
                 NULL, NULL,
                 'facebook-ads',

                 CASE
                     WHEN ma.campaign_name LIKE '%[Gestor de Tr_fego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Tráfego:', -1), ']', 1))
                     WHEN ma.campaign_name LIKE '%[Gestor de Trafego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Trafego:', -1), ']', 1))
                     ELSE NULL
                     END,

                 CASE
                     WHEN ma.campaign_name LIKE '%Funil de Nova Ideia #%'
                         THEN CONCAT('Funil de Nova Ideia #',
                                     SUBSTRING_INDEX(
                                             REGEXP_SUBSTR(SUBSTRING_INDEX(ma.campaign_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'),
                                             ' ', 1
                                     ))
                     ELSE NULL
                     END,

                 'Facebook Ads',
                 NULL,

                 NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                 NULL, NULL, NULL,
                 NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                 NULL, NULL, NULL, NULL, NULL, NULL,

                 COALESCE(SUM(ma.amount_spent_brl), 0),

                 0, 0,

                 COALESCE(SUM(ma.spent_taxes), 0),

                 COALESCE(SUM(ma.amount_spent_brl), 0) + COALESCE(SUM(ma.spent_taxes), 0)

             FROM `instituto_experience`.`meta_ad_id` ma FORCE INDEX (`idx_meta_ads_date`)
             WHERE ma.created_at_date >= '2025-09-01'
               AND ma.campaign_name LIKE '%Nova Ideia%'
               AND ma.campaign_name NOT LIKE '%Thales Pater%'

             GROUP BY
                 ma.created_at_date,
                 CASE
                     WHEN ma.campaign_name LIKE '%[Gestor de Tr_fego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Tráfego:', -1), ']', 1))
                     WHEN ma.campaign_name LIKE '%[Gestor de Trafego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Trafego:', -1), ']', 1))
                     ELSE NULL
                     END,
                 CASE
                     WHEN ma.campaign_name LIKE '%Funil de Nova Ideia #%'
                         THEN CONCAT('Funil de Nova Ideia #',
                                     SUBSTRING_INDEX(
                                             REGEXP_SUBSTR(SUBSTRING_INDEX(ma.campaign_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'),
                                             ' ', 1
                                     ))
                     ELSE NULL
                     END

             -- =================================================================
             -- 4) GOOGLE ADS
             -- =================================================================
             UNION ALL
             SELECT
                 ga.created_at_date,
                 NULL, NULL,
                 'google-ads',

                 CASE
                     WHEN ga.campaign_name LIKE '%[Gestor de Tr_fego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ga.campaign_name, '[Gestor de Tráfego:', -1), ']', 1))
                     WHEN ga.campaign_name LIKE '%[Gestor de Trafego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ga.campaign_name, '[Gestor de Trafego:', -1), ']', 1))
                     ELSE NULL
                     END,

                 CASE
                     WHEN ga.campaign_name LIKE '%Funil de Nova Ideia #%'
                         THEN CONCAT('Funil de Nova Ideia #',
                                     SUBSTRING_INDEX(
                                             REGEXP_SUBSTR(SUBSTRING_INDEX(ga.campaign_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'),
                                             ' ', 1
                                     ))
                     ELSE NULL
                     END,

                 'Google Ads',
                 NULL,

                 NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                 NULL, NULL, NULL,
                 NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                 NULL, NULL, NULL, NULL, NULL, NULL,

                 COALESCE(SUM(ga.amount_spent_brl), 0),

                 0, 0,

                 NULL,

                 COALESCE(SUM(ga.amount_spent_brl), 0)

             FROM `instituto_experience`.`google_ad_id` ga FORCE INDEX (`idx_google_ads_date`)
             WHERE ga.created_at_date >= '2025-09-01'
               AND ga.campaign_name LIKE '%Nova Ideia%'
               AND ga.campaign_name NOT LIKE '%Thales Pater%'

             GROUP BY
                 ga.created_at_date,
                 CASE
                     WHEN ga.campaign_name LIKE '%[Gestor de Tr_fego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ga.campaign_name, '[Gestor de Tráfego:', -1), ']', 1))
                     WHEN ga.campaign_name LIKE '%[Gestor de Trafego:%]%'
                         THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ga.campaign_name, '[Gestor de Trafego:', -1), ']', 1))
                     ELSE NULL
                     END,
                 CASE
                     WHEN ga.campaign_name LIKE '%Funil de Nova Ideia #%'
                         THEN CONCAT('Funil de Nova Ideia #',
                                     SUBSTRING_INDEX(
                                             REGEXP_SUBSTR(SUBSTRING_INDEX(ga.campaign_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'),
                                             ' ', 1
                                     ))
                     ELSE NULL
                     END

         ) ud

             LEFT JOIN `instituto_experience`.`funil_produto_mapping` fpm
                       ON ud.funil_id = fpm.funil_id

             LEFT JOIN (
        SELECT
            product_key,
            MAX(niche) AS niche
        FROM `instituto_experience`.`call_center_sales`
        WHERE nome_produto != 'Geral'
          AND nome_produto NOT LIKE '%Sem Nome%'
          AND nome_produto NOT LIKE '%Outros%'
        GROUP BY product_key
    ) nl
                       ON ud.product_key = nl.product_key;

END
```
