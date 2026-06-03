---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-06-01 17:56:15"
alterada_em: "2026-06-01 17:56:15"
execucoes: 215
tags: [rotina, procedure]
---

# refresh_dashboard_affiliate_nutra

## Dependências

- **Lê:** [[call_center_sales]], [[cartpanda_physical]], [[dashboard_gold_clickbank_buygoods]]
- **Escreve:** [[dashboard_affiliate_nutra_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_affiliate_nutra_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 215 |
| Tempo médio | 16.3 s |
| Tempo máx | 59.1 s |
| Tempo total | 58m33s |
| Erros | 0 |
| Warnings | 66,866,267 |
| Linhas afetadas (total) | 17,095,767 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_affiliate_nutra_stage;
        RESIGNAL;
    END;

    TRUNCATE TABLE instituto_experience.dashboard_affiliate_nutra_stage;

    INSERT INTO instituto_experience.dashboard_affiliate_nutra_stage (
        created_at_date,
        clean_product_name,
        platform,
        affiliate_name,
        affiliate_id,
        payment_status,
        funil_id,
        coupon_code,
        niche,
        total_vendas,
        total_price,
        commission,
        taxes,
        total_refund,
        product_cost,
        affiliate_amount,
        imposto,
        `1_2_units_sales`,
        `3_4_units_sales`,
        `5_6_units_sales`,
        faixa_potes,
        ob_count, ob_revenue,
        up1_count, up1_revenue,
        up2_count, up2_revenue,
        up3_count, up3_revenue,
        down1_count, down1_revenue,
        down2_count, down2_revenue,
        down3_count, down3_revenue,
        revenue_no_funnel
    )
    SELECT
        ud.created_at_date,
        ud.clean_product_name,
        ud.platform,
        ud.affiliate_name,
        ud.affiliate_id,
        ud.payment_status,
        ud.funil_id,
        ud.coupon_code,
        nl.niche,
        ud.total_vendas,
        ud.total_price,
        ud.commission,
        ud.taxes,
        ud.total_refund,
        ud.product_cost,
        ud.affiliate_amount,
        ud.imposto,
        ud.`1_2_units_sales`,
        ud.`3_4_units_sales`,
        ud.`5_6_units_sales`,
        ud.faixa_potes,
        ud.ob_count, ud.ob_revenue,
        ud.up1_count, ud.up1_revenue,
        ud.up2_count, ud.up2_revenue,
        ud.up3_count, ud.up3_revenue,
        ud.down1_count, ud.down1_revenue,
        ud.down2_count, ud.down2_revenue,
        ud.down3_count, ud.down3_revenue,
        (ud.total_price - (
            ud.ob_revenue + ud.up1_revenue + ud.up2_revenue + ud.up3_revenue
                + ud.down1_revenue + ud.down2_revenue + ud.down3_revenue
            )) AS revenue_no_funnel
    FROM (

             -- ===================== 1) CARTPANDA =====================
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
                       )) AS product_key,

                 CONCAT(
                         UPPER(LEFT(LOWER(REGEXP_REPLACE(
                                 TRIM(CASE
                                          WHEN cp.product_name LIKE '%-%'
                                              THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                          WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                              THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                          ELSE cp.product_name
                                     END),
                                 '[^a-zA-Z0-9]', ''
                                          )), 1)),
                         SUBSTRING(LOWER(REGEXP_REPLACE(
                                 TRIM(CASE
                                          WHEN cp.product_name LIKE '%-%'
                                              THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                          WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                              THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                          ELSE cp.product_name
                                     END),
                                 '[^a-zA-Z0-9]', ''
                                         )), 2)
                 ) AS clean_product_name,

                 'cartpanda' AS platform,
                 cp.affiliate_name,
                 cp.affiliate_id,
                 cp.payment_status,

                 CASE
                     WHEN cp.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                         THEN TRIM(REGEXP_SUBSTR(cp.offer_name, 'Funil [^#]*#[0-9]+'))
                     ELSE NULL
                     END AS funil_id,

                 NULLIF(cp.coupon_code, '') AS coupon_code,

                 -- Faixa de potes (Cartpanda via product_sku)
                 CASE
                     WHEN LOWER(cp.product_sku) LIKE '%1unit%'
                       OR LOWER(cp.product_sku) LIKE '%2unit%' THEN '1 a 2 Potes'
                     WHEN LOWER(cp.product_sku) LIKE '%3unit%'
                       OR LOWER(cp.product_sku) LIKE '%4unit%' THEN '3 a 4 Potes'
                     WHEN LOWER(cp.product_sku) LIKE '%5unit%'
                       OR LOWER(cp.product_sku) LIKE '%6unit%' THEN '5+ Potes'
                     ELSE 'Não Encontrado'
                 END AS faixa_potes,

                 COUNT(*) AS total_vendas,
                 COALESCE(SUM(cp.total_price), 0) AS total_price,
                 COALESCE(SUM(cp.commission), 0) AS commission,
                 COALESCE(SUM(cp.taxes), 0) AS taxes,
                 COALESCE(SUM(cp.total_refund), 0) AS total_refund,
                 COALESCE(SUM(cp.affiliate_amount), 0) AS affiliate_amount,

                 COALESCE(SUM(CASE
                                  WHEN cp.payment_status IN ('approved', 'refunded_partial')
                                      THEN cp.product_cost
                                  ELSE 0
                     END), 0) AS product_cost,

                 SUM(CASE
                         WHEN cp.payment_status IN ('approved', 'refunded_partial')
                             THEN
                             CASE
                                 WHEN cp.created_at_date BETWEEN '2026-01-01' AND '2026-03-31' THEN
                                     CASE
                                         WHEN LOWER(REGEXP_REPLACE(
                                                 TRIM(CASE
                                                          WHEN cp.product_name LIKE '%-%'
                                                              THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                                          WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                                              THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                                          ELSE cp.product_name
                                                     END),
                                                 '[^a-zA-Z0-9]', ''
                                                    )) IN ('glycopezil', 'sugarcontrol')
                                             THEN cp.total_price * 0.017
                                         ELSE cp.total_price * 0
                                         END
                                 ELSE cp.total_price * 0.01
                                 END
                         ELSE 0
                     END) AS imposto,

                 -- Como o grão já é por faixa, apenas UMA das 3 colunas será > 0 em cada linha
                 SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%1unit%'
                     OR LOWER(cp.product_sku) LIKE '%2unit%' THEN 1 ELSE 0 END) AS `1_2_units_sales`,
                 SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%3unit%'
                     OR LOWER(cp.product_sku) LIKE '%4unit%' THEN 1 ELSE 0 END) AS `3_4_units_sales`,
                 SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%5unit%'
                     OR LOWER(cp.product_sku) LIKE '%6unit%' THEN 1 ELSE 0 END) AS `5_6_units_sales`,

                 COALESCE(SUM(cp.has_order_bump), 0) AS ob_count,
                 COALESCE(SUM(cp.total_price_order_bump), 0) AS ob_revenue,
                 COALESCE(SUM(cp.has_upsell), 0) AS up1_count,
                 COALESCE(SUM(cp.total_price_upsell), 0) AS up1_revenue,
                 COALESCE(SUM(cp.has_upsell2), 0) AS up2_count,
                 COALESCE(SUM(cp.total_price_upsell2), 0) AS up2_revenue,
                 COALESCE(SUM(cp.has_upsell3), 0) AS up3_count,
                 COALESCE(SUM(cp.total_price_upsell3), 0) AS up3_revenue,
                 COALESCE(SUM(cp.has_downsell), 0) AS down1_count,
                 COALESCE(SUM(cp.total_price_downsell), 0) AS down1_revenue,
                 COALESCE(SUM(cp.has_downsell2), 0) AS down2_count,
                 COALESCE(SUM(cp.total_price_downsell2), 0) AS down2_revenue,
                 COALESCE(SUM(cp.has_downsell3), 0) AS down3_count,
                 COALESCE(SUM(cp.total_price_downsell3), 0) AS down3_revenue

             FROM instituto_experience.cartpanda_physical cp FORCE INDEX (idx_cp_created_date)
             WHERE cp.created_at_date >= '2026-01-01'
               AND cp.payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
               AND cp.affiliate_name IS NOT NULL
               AND cp.affiliate_name <> ''
             GROUP BY
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
                       )),
                 CONCAT(
                         UPPER(LEFT(LOWER(REGEXP_REPLACE(
                                 TRIM(CASE
                                          WHEN cp.product_name LIKE '%-%'
                                              THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                          WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                              THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                          ELSE cp.product_name
                                     END),
                                 '[^a-zA-Z0-9]', ''
                                          )), 1)),
                         SUBSTRING(LOWER(REGEXP_REPLACE(
                                 TRIM(CASE
                                          WHEN cp.product_name LIKE '%-%'
                                              THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                          WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                              THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                          ELSE cp.product_name
                                     END),
                                 '[^a-zA-Z0-9]', ''
                                         )), 2)
                 ),
                 cp.affiliate_name,
                 cp.affiliate_id,
                 cp.payment_status,
                 CASE
                     WHEN cp.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                         THEN TRIM(REGEXP_SUBSTR(cp.offer_name, 'Funil [^#]*#[0-9]+'))
                     ELSE NULL
                     END,
                 NULLIF(cp.coupon_code, ''),
                 -- Faixa de potes adicionada ao GROUP BY
                 CASE
                     WHEN LOWER(cp.product_sku) LIKE '%1unit%'
                       OR LOWER(cp.product_sku) LIKE '%2unit%' THEN '1 a 2 Potes'
                     WHEN LOWER(cp.product_sku) LIKE '%3unit%'
                       OR LOWER(cp.product_sku) LIKE '%4unit%' THEN '3 a 4 Potes'
                     WHEN LOWER(cp.product_sku) LIKE '%5unit%'
                       OR LOWER(cp.product_sku) LIKE '%6unit%' THEN '5+ Potes'
                     ELSE 'Não Encontrado'
                 END

             UNION ALL

             -- ===================== 2) GOLD CLICKBANK + BUYGOODS =====================
             SELECT
                 cbg.created_at_date,

                 LOWER(REGEXP_REPLACE(
                         TRIM(CASE
                                  WHEN cbg.product_name LIKE '%-%'
                                      THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                  WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                      THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                  ELSE cbg.product_name
                             END),
                         '[^a-zA-Z0-9]', ''
                       )) AS product_key,

                 CONCAT(
                         UPPER(LEFT(LOWER(REGEXP_REPLACE(
                                 TRIM(CASE
                                          WHEN cbg.product_name LIKE '%-%'
                                              THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                          WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                              THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                          ELSE cbg.product_name
                                     END),
                                 '[^a-zA-Z0-9]', ''
                                          )), 1)),
                         SUBSTRING(LOWER(REGEXP_REPLACE(
                                 TRIM(CASE
                                          WHEN cbg.product_name LIKE '%-%'
                                              THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                          WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                              THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                          ELSE cbg.product_name
                                     END),
                                 '[^a-zA-Z0-9]', ''
                                         )), 2)
                 ) AS clean_product_name,

                 cbg.platform AS platform,
                 cbg.affiliate_name,
                 NULL AS affiliate_id,
                 cbg.payment_status,

                 CASE
                     WHEN cbg.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                         THEN TRIM(REGEXP_SUBSTR(cbg.offer_name, 'Funil [^#]*#[0-9]+'))
                     ELSE NULL
                     END AS funil_id,

                 NULL AS coupon_code,

                 -- Faixa de potes (ClickBank/BuyGoods via quantity_principal)
                 CASE
                     WHEN cbg.quantity_principal IN (1, 2) THEN '1 a 2 Potes'
                     WHEN cbg.quantity_principal IN (3, 4) THEN '3 a 4 Potes'
                     WHEN cbg.quantity_principal >= 5     THEN '5+ Potes'
                     ELSE 'Não Encontrado'
                 END AS faixa_potes,

                 COUNT(*) AS total_vendas,
                 COALESCE(SUM(cbg.total_price), 0) AS total_price,
                 COALESCE(SUM(cbg.commission), 0) AS commission,
                 COALESCE(SUM(cbg.taxes), 0) AS taxes,
                 COALESCE(SUM(cbg.total_refund), 0) AS total_refund,
                 COALESCE(SUM(cbg.affiliate_amount), 0) AS affiliate_amount,

                 COALESCE(SUM(CASE
                                  WHEN cbg.payment_status IN ('approved', 'refunded_partial')
                                      THEN cbg.product_cost
                                  ELSE 0
                     END), 0) AS product_cost,

                 SUM(CASE
                         WHEN cbg.payment_status IN ('approved', 'refunded_partial')
                             THEN
                             CASE
                                 WHEN cbg.created_at_date BETWEEN '2026-01-01' AND '2026-03-31' THEN
                                     CASE
                                         WHEN LOWER(REGEXP_REPLACE(
                                                 TRIM(CASE
                                                          WHEN cbg.product_name LIKE '%-%'
                                                              THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                                          WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                                              THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                                          ELSE cbg.product_name
                                                     END),
                                                 '[^a-zA-Z0-9]', ''
                                                    )) IN ('glycopezil', 'sugarcontrol')
                                             THEN cbg.total_price * 0.017
                                         ELSE cbg.total_price * 0
                                         END
                                 ELSE cbg.total_price * 0.01
                                 END
                         ELSE 0
                     END) AS imposto,

                 -- Como o grão já é por faixa, apenas UMA das 3 colunas será > 0 em cada linha
                 SUM(CASE WHEN cbg.quantity_principal IN (1, 2) THEN 1 ELSE 0 END) AS `1_2_units_sales`,
                 SUM(CASE WHEN cbg.quantity_principal IN (3, 4) THEN 1 ELSE 0 END) AS `3_4_units_sales`,
                 SUM(CASE WHEN cbg.quantity_principal >= 5     THEN 1 ELSE 0 END) AS `5_6_units_sales`,

                 COALESCE(SUM(cbg.has_order_bump), 0) AS ob_count,
                 COALESCE(SUM(cbg.total_price_order_bump), 0) AS ob_revenue,
                 COALESCE(SUM(cbg.has_upsell), 0) AS up1_count,
                 COALESCE(SUM(cbg.total_price_upsell), 0) AS up1_revenue,
                 COALESCE(SUM(cbg.has_upsell2), 0) AS up2_count,
                 COALESCE(SUM(cbg.total_price_upsell2), 0) AS up2_revenue,
                 COALESCE(SUM(cbg.has_upsell3), 0) AS up3_count,
                 COALESCE(SUM(cbg.total_price_upsell3), 0) AS up3_revenue,
                 COALESCE(SUM(cbg.has_downsell), 0) AS down1_count,
                 COALESCE(SUM(cbg.total_price_downsell), 0) AS down1_revenue,
                 COALESCE(SUM(cbg.has_downsell2), 0) AS down2_count,
                 COALESCE(SUM(cbg.total_price_downsell2), 0) AS down2_revenue,
                 COALESCE(SUM(cbg.has_downsell3), 0) AS down3_count,
                 COALESCE(SUM(cbg.total_price_downsell3), 0) AS down3_revenue

             FROM instituto_experience.dashboard_gold_clickbank_buygoods cbg
             WHERE cbg.created_at_date >= '2026-01-01'
               AND cbg.payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
               AND cbg.affiliate_name IS NOT NULL
               AND cbg.affiliate_name <> ''
               AND (cbg.is_house_traffic = 0 OR cbg.is_house_traffic IS NULL)
             GROUP BY
                 cbg.created_at_date,
                 LOWER(REGEXP_REPLACE(
                         TRIM(CASE
                                  WHEN cbg.product_name LIKE '%-%'
                                      THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                  WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                      THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                  ELSE cbg.product_name
                             END),
                         '[^a-zA-Z0-9]', ''
                       )),
                 CONCAT(
                         UPPER(LEFT(LOWER(REGEXP_REPLACE(
                                 TRIM(CASE
                                          WHEN cbg.product_name LIKE '%-%'
                                              THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                          WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                              THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                          ELSE cbg.product_name
                                     END),
                                 '[^a-zA-Z0-9]', ''
                                          )), 1)),
                         SUBSTRING(LOWER(REGEXP_REPLACE(
                                 TRIM(CASE
                                          WHEN cbg.product_name LIKE '%-%'
                                              THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                          WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                              THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                          ELSE cbg.product_name
                                     END),
                                 '[^a-zA-Z0-9]', ''
                                         )), 2)
                 ),
                 cbg.platform,
                 cbg.affiliate_name,
                 cbg.payment_status,
                 CASE
                     WHEN cbg.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                         THEN TRIM(REGEXP_SUBSTR(cbg.offer_name, 'Funil [^#]*#[0-9]+'))
                     ELSE NULL
                     END,
                 -- Faixa de potes adicionada ao GROUP BY
                 CASE
                     WHEN cbg.quantity_principal IN (1, 2) THEN '1 a 2 Potes'
                     WHEN cbg.quantity_principal IN (3, 4) THEN '3 a 4 Potes'
                     WHEN cbg.quantity_principal >= 5     THEN '5+ Potes'
                     ELSE 'Não Encontrado'
                 END

         ) ud

    LEFT JOIN (
        SELECT product_key, MAX(niche) AS niche
        FROM instituto_experience.call_center_sales
        WHERE nome_produto != 'Geral'
          AND nome_produto NOT LIKE '%Sem Nome%'
          AND nome_produto NOT LIKE '%Outros%'
        GROUP BY product_key
    ) nl ON ud.product_key = nl.product_key;

    RENAME TABLE
        instituto_experience.dashboard_affiliate_nutra       TO instituto_experience.dashboard_affiliate_nutra_old,
        instituto_experience.dashboard_affiliate_nutra_stage TO instituto_experience.dashboard_affiliate_nutra,
        instituto_experience.dashboard_affiliate_nutra_old   TO instituto_experience.dashboard_affiliate_nutra_stage;

END
```
