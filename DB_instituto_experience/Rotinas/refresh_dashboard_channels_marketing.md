---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-22 14:54:48"
alterada_em: "2026-05-22 14:54:48"
execucoes: 183
tags: [rotina, procedure]
---

# refresh_dashboard_channels_marketing

## Dependências

- **Lê:** [[call_center_sales]], [[cartpanda_physical]], [[dashboard_gold_clickbank_buygoods]], [[gross_recovery_target]], [[sms_costs]]
- **Escreve:** [[dashboard_channels_marketing_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_channels_marketing_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 183 |
| Tempo médio | 1m28s |
| Tempo máx | 2m4s |
| Tempo total | 4h27m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 14,668,767 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_channels_marketing_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_channels_marketing_stage;

    -- 2. Insere na stage (produção continua intacta)
    INSERT INTO instituto_experience.dashboard_channels_marketing_stage
WITH

/* =======================
   0) FONTE UNIFICADA
======================= */
combined_source AS (
    SELECT
        offer_name,
        product_name,
        product_sku,
        payment_status,
        total_price,
        product_cost,
        commission,
        taxes,
        total_refund,
        has_order_bump, total_price_order_bump,
        has_upsell, total_price_upsell,
        has_upsell2, total_price_upsell2,
        has_upsell3, total_price_upsell3,
        has_downsell, total_price_downsell,
        has_downsell2, total_price_downsell2,
        has_downsell3, total_price_downsell3,
        created_at_date,
        'cartpanda' AS origem
    FROM instituto_experience.cartpanda_physical
    WHERE created_at_date >= '2025-01-01'

    UNION ALL

    SELECT
        offer_name,
        product_name,
        CONCAT(quantity_principal, 'unit') AS product_sku,
        payment_status,
        total_price,
        product_cost,
        commission,
        taxes,
        total_refund,
        has_order_bump, total_price_order_bump,
        has_upsell, total_price_upsell,
        has_upsell2, total_price_upsell2,
        has_upsell3, total_price_upsell3,
        has_downsell, total_price_downsell,
        has_downsell2, total_price_downsell2,
        has_downsell3, total_price_downsell3,
        created_at_date,
        platform AS origem
    FROM instituto_experience.dashboard_gold_clickbank_buygoods
    WHERE created_at_date >= '2025-01-01'
),

/* =======================
   1) RAW BASE (SMS / EMAIL / WHATSAPP)
======================= */
raw_base AS (

    /* -------- SMS -------- */
    SELECT
        'sms' AS canal,
        cp.created_at_date,

        LOWER(
            REGEXP_REPLACE(
                TRIM(
                    CASE
                        WHEN cp.product_name LIKE '%-%'
                            THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                        WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                            THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                        ELSE cp.product_name
                    END
                ),
                '[^a-zA-Z0-9]',
                ''
            )
        ) AS product_key,

        CASE
            WHEN LOWER(cp.offer_name) LIKE '%sms%' AND LOWER(cp.offer_name) LIKE '%recup%'
                THEN 'Recuperação'
            WHEN LOWER(cp.offer_name) LIKE '%sms%' AND LOWER(cp.offer_name) LIKE '%mone%'
                THEN 'Monetização'
            WHEN LOWER(cp.offer_name) LIKE '%sms%' AND LOWER(cp.offer_name) LIKE '%broad%'
                THEN 'Broadcast'
            ELSE 'Non-SMS'
        END AS tipo_venda,

        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])1unit|(^|[^0-9])2unit' THEN 1 ELSE 0 END AS is_1_2,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])2unit|(^|[^0-9])3unit' THEN 1 ELSE 0 END AS is_2_3,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])3unit|(^|[^0-9])4unit' THEN 1 ELSE 0 END AS is_3_4,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])5unit|(^|[^0-9])6unit' THEN 1 ELSE 0 END AS is_5_6,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])4unit' THEN 1 ELSE 0 END AS is_4,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])5unit' THEN 1 ELSE 0 END AS is_5,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])3unit|(^|[^0-9])4unit|(^|[^0-9])5unit' THEN 1 ELSE 0 END AS is_3_5,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])6unit|(^|[^0-9])7unit|(^|[^0-9])8unit|(^|[^0-9])9unit|(^|[^0-9])10unit|(^|[^0-9])11unit|(^|[^0-9])12unit' THEN 1 ELSE 0 END AS is_6_plus,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])7unit|(^|[^0-9])8unit|(^|[^0-9])9unit|(^|[^0-9])10unit|(^|[^0-9])11unit|(^|[^0-9])12unit' THEN 1 ELSE 0 END AS is_7_plus,

        cp.payment_status,
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
        cp.has_downsell3, cp.total_price_downsell3,
        cp.origem

    FROM combined_source cp
    WHERE LOWER(cp.offer_name) LIKE '%sms%'
      AND LOWER(cp.offer_name) NOT LIKE '%parceiro%'
      AND UPPER(cp.offer_name) NOT LIKE '%DAMAS%'

    UNION ALL

    /* -------- EMAIL -------- */
    SELECT
        'email' AS canal,
        cp.created_at_date,

        LOWER(
            REGEXP_REPLACE(
                TRIM(
                    CASE
                        WHEN cp.product_name LIKE '%-%'
                            THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                        WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                            THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                        ELSE cp.product_name
                    END
                ),
                '[^a-zA-Z0-9]',
                ''
            )
        ) AS product_key,

        CASE
            WHEN LOWER(cp.offer_name) LIKE '%recup%' THEN 'Recuperação'
            WHEN LOWER(cp.offer_name) LIKE '%mone%' THEN 'Monetização'
            WHEN LOWER(cp.offer_name) LIKE '%broad%' THEN 'Broadcast'
            ELSE 'Non-SMS'
        END AS tipo_venda,

        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])1unit|(^|[^0-9])2unit' THEN 1 ELSE 0 END AS is_1_2,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])2unit|(^|[^0-9])3unit' THEN 1 ELSE 0 END AS is_2_3,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])3unit|(^|[^0-9])4unit' THEN 1 ELSE 0 END AS is_3_4,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])5unit|(^|[^0-9])6unit' THEN 1 ELSE 0 END AS is_5_6,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])4unit' THEN 1 ELSE 0 END AS is_4,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])5unit' THEN 1 ELSE 0 END AS is_5,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])3unit|(^|[^0-9])4unit|(^|[^0-9])5unit' THEN 1 ELSE 0 END AS is_3_5,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])6unit|(^|[^0-9])7unit|(^|[^0-9])8unit|(^|[^0-9])9unit|(^|[^0-9])10unit|(^|[^0-9])11unit|(^|[^0-9])12unit' THEN 1 ELSE 0 END AS is_6_plus,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])7unit|(^|[^0-9])8unit|(^|[^0-9])9unit|(^|[^0-9])10unit|(^|[^0-9])11unit|(^|[^0-9])12unit' THEN 1 ELSE 0 END AS is_7_plus,

        cp.payment_status,
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
        cp.has_downsell3, cp.total_price_downsell3,
        cp.origem

    FROM combined_source cp
    WHERE (LOWER(cp.offer_name) LIKE '%email%' OR LOWER(cp.offer_name) LIKE '%e-mail%')
      AND LOWER(cp.offer_name) NOT LIKE '%parceiro%'
      AND UPPER(cp.offer_name) NOT LIKE '%DAMAS%'

    UNION ALL

    /* -------- WHATSAPP -------- */
    SELECT
        'whatsapp' AS canal,
        cp.created_at_date,

        LOWER(
            REGEXP_REPLACE(
                TRIM(
                    CASE
                        WHEN cp.product_name LIKE '%-%'
                            THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                        WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                            THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                        ELSE cp.product_name
                    END
                ),
                '[^a-zA-Z0-9]',
                ''
            )
        ) AS product_key,

        CASE
            WHEN LOWER(cp.offer_name) LIKE '%recup%' THEN 'Recuperação'
            WHEN LOWER(cp.offer_name) LIKE '%mone%' THEN 'Monetização'
            WHEN LOWER(cp.offer_name) LIKE '%broad%' THEN 'Broadcast'
            ELSE 'Non-SMS'
        END AS tipo_venda,

        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])1unit|(^|[^0-9])2unit' THEN 1 ELSE 0 END AS is_1_2,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])2unit|(^|[^0-9])3unit' THEN 1 ELSE 0 END AS is_2_3,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])3unit|(^|[^0-9])4unit' THEN 1 ELSE 0 END AS is_3_4,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])5unit|(^|[^0-9])6unit' THEN 1 ELSE 0 END AS is_5_6,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])4unit' THEN 1 ELSE 0 END AS is_4,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])5unit' THEN 1 ELSE 0 END AS is_5,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])3unit|(^|[^0-9])4unit|(^|[^0-9])5unit' THEN 1 ELSE 0 END AS is_3_5,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])6unit|(^|[^0-9])7unit|(^|[^0-9])8unit|(^|[^0-9])9unit|(^|[^0-9])10unit|(^|[^0-9])11unit|(^|[^0-9])12unit' THEN 1 ELSE 0 END AS is_6_plus,
        CASE WHEN LOWER(cp.product_sku) REGEXP '(^|[^0-9])7unit|(^|[^0-9])8unit|(^|[^0-9])9unit|(^|[^0-9])10unit|(^|[^0-9])11unit|(^|[^0-9])12unit' THEN 1 ELSE 0 END AS is_7_plus,

        cp.payment_status,
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
        cp.has_downsell3, cp.total_price_downsell3,
        cp.origem

    FROM combined_source cp
    WHERE LOWER(cp.offer_name) LIKE '%whatsapp%'
      AND LOWER(cp.offer_name) NOT LIKE '%parceiro%'
      AND UPPER(cp.offer_name) NOT LIKE '%DAMAS%'
),

/* =======================
   2) AGGREGATED
======================= */
aggregated_sms AS (
    SELECT
        canal,
        created_at_date,
        product_key,
        tipo_venda,
        origem,

        SUM(is_1_2) AS sum_1_2,
        SUM(is_2_3) AS sum_2_3,
        SUM(is_3_4) AS sum_3_4,
        SUM(is_5_6) AS sum_5_6,
        SUM(is_4) AS sum_4,
        SUM(is_5) AS sum_5,
        SUM(is_3_5) AS sum_3_5,
        SUM(is_6_plus) AS sum_6_plus,
        SUM(is_7_plus) AS sum_7_plus,

        COUNT(CASE WHEN payment_status IS NOT NULL THEN 1 END) AS total_vendas,
        COALESCE(SUM(total_price), 0) AS rev,
        COALESCE(SUM(product_cost), 0) AS cost,
        COALESCE(SUM(commission), 0) AS comm,
        COALESCE(SUM(taxes), 0) AS tax,
        COALESCE(SUM(imposto_calc), 0) AS imp,
        COALESCE(SUM(total_refund), 0) AS ref,

        (
            COALESCE(SUM(commission), 0)
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

    FROM raw_base
    GROUP BY canal, created_at_date, product_key, tipo_venda, origem
),

/* =======================
   3) FRONTEND
======================= */
frontend AS (
    SELECT
        data,
        LOWER(REGEXP_REPLACE(nome_produto, '[^a-zA-Z0-9]', '')) AS join_key,
        MAX(niche) AS niche,
        COALESCE(SUM(frontend_sales * 5.4), 0) AS front_brl
    FROM call_center_sales
    WHERE nome_produto != 'Geral'
      AND nome_produto NOT LIKE '%Sem Nome%'
      AND nome_produto NOT LIKE '%Outros%'
    GROUP BY data, join_key
),

/* =======================
   4) UNIVERSE
======================= */
base_universe AS (
    SELECT DISTINCT canal, created_at_date AS dt, product_key AS pk, origem
    FROM aggregated_sms
    UNION
    SELECT DISTINCT 'sms', data, join_key, NULL FROM frontend
    UNION
    SELECT DISTINCT 'email', data, join_key, NULL FROM frontend
    UNION
    SELECT DISTINCT 'whatsapp', data, join_key, NULL FROM frontend
),

tipos AS (
    SELECT 'Recuperação' AS tipo_venda
    UNION ALL SELECT 'Monetização'
    UNION ALL SELECT 'Broadcast'
),

universe AS (
    SELECT bu.canal, bu.dt, bu.pk, bu.origem, t.tipo_venda
    FROM base_universe bu
    CROSS JOIN tipos t
),

/* =======================
   5) FINAL PREP
======================= */
final_prep AS (
    SELECT
        u.canal,
        u.dt,
        u.pk,
        fe.niche,
        u.tipo_venda,
        u.origem,

        COALESCE(asms.sum_1_2, 0) AS sum_1_2,
        COALESCE(asms.sum_2_3, 0) AS sum_2_3,
        COALESCE(asms.sum_3_4, 0) AS sum_3_4,
        COALESCE(asms.sum_5_6, 0) AS sum_5_6,
        COALESCE(asms.sum_4, 0) AS sum_4,
        COALESCE(asms.sum_5, 0) AS sum_5,
        COALESCE(asms.sum_3_5, 0) AS sum_3_5,
        COALESCE(asms.sum_6_plus, 0) AS sum_6_plus,
        COALESCE(asms.sum_7_plus, 0) AS sum_7_plus,
        COALESCE(asms.total_vendas, 0) AS total_vendas,
        COALESCE(asms.rev, 0) AS rev,
        COALESCE(asms.cost, 0) AS cost,
        COALESCE(asms.comm, 0) AS comm,
        COALESCE(asms.tax, 0) AS tax,
        COALESCE(asms.imp, 0) AS imp,
        COALESCE(asms.ref, 0) AS ref,
        COALESCE(asms.net_val, 0) AS net_val,

        COALESCE(asms.ob_c, 0) AS ob_c, COALESCE(asms.ob_r, 0) AS ob_r,
        COALESCE(asms.up1_c, 0) AS up1_c, COALESCE(asms.up1_r, 0) AS up1_r,
        COALESCE(asms.up2_c, 0) AS up2_c, COALESCE(asms.up2_r, 0) AS up2_r,
        COALESCE(asms.up3_c, 0) AS up3_c, COALESCE(asms.up3_r, 0) AS up3_r,
        COALESCE(asms.down1_c, 0) AS down1_c, COALESCE(asms.down1_r, 0) AS down1_r,
        COALESCE(asms.down2_c, 0) AS down2_c, COALESCE(asms.down2_r, 0) AS down2_r,
        COALESCE(asms.down3_c, 0) AS down3_c, COALESCE(asms.down3_r, 0) AS down3_r,

        COALESCE(fe.front_brl, 0) AS front_total_brl,

        ROW_NUMBER() OVER (
            PARTITION BY u.canal, u.dt, u.pk, u.tipo_venda
            ORDER BY COALESCE(asms.rev, 0) DESC
        ) AS row_rank,

        ROW_NUMBER() OVER (
            PARTITION BY u.canal, u.dt, u.pk
            ORDER BY COALESCE(asms.rev, 0) DESC, u.tipo_venda ASC
        ) AS global_row_rank

    FROM universe u
    LEFT JOIN aggregated_sms asms
      ON u.canal = asms.canal
     AND u.dt = asms.created_at_date
     AND u.pk = asms.product_key
     AND u.tipo_venda = asms.tipo_venda
     AND (u.origem = asms.origem OR (u.origem IS NULL AND asms.origem IS NULL))
    LEFT JOIN frontend fe
      ON u.dt = fe.data
     AND u.pk = fe.join_key
)

/* =======================
   6) SELECT FINAL
======================= */
SELECT
    fp.canal,
    fp.dt AS data_venda,
    fp.pk AS nome_produto,
    fp.niche,
    fp.tipo_venda,

    CASE WHEN fp.row_rank = 1 THEN 1 ELSE 0 END AS is_reference_row,
    CASE WHEN fp.global_row_rank = 1 THEN 1 ELSE 0 END AS is_global_reference_row,

    fp.sum_1_2 AS units_1_2,
    fp.sum_2_3 AS units_2_3,
    fp.sum_3_4 AS units_3_4,
    fp.sum_5_6 AS units_5_6,
    fp.sum_3_5 AS units_3_5,
    fp.sum_4 AS units_4,
    fp.sum_5 AS units_5,
    fp.sum_6_plus AS units_6_plus,
    fp.sum_7_plus AS units_7_plus,
    fp.total_vendas,
    fp.rev AS revenue,
    fp.cost AS product_cost,
    fp.comm AS commission,
    fp.tax AS taxes,
    fp.imp AS imposto,
    fp.ref AS total_refund,

    CAST(
        fp.comm
      - fp.cost
      - fp.imp
      - (
            CASE
                WHEN fp.canal = 'sms' AND fp.tipo_venda = 'Recuperação' THEN sc.sms_recup_cost
                WHEN fp.canal = 'sms' AND fp.tipo_venda = 'Monetização' THEN sc.sms_monet_cost
                WHEN fp.canal = 'email' AND fp.tipo_venda = 'Recuperação' THEN sc.email_recup_cost
                WHEN fp.canal = 'email' AND fp.tipo_venda = 'Monetização' THEN sc.email_monet_cost
                WHEN fp.canal = 'whatsapp' AND fp.tipo_venda = 'Recuperação' THEN sc.whatsapp_recup_cost
                WHEN fp.canal = 'whatsapp' AND fp.tipo_venda = 'Monetização' THEN sc.whatsapp_monet_cost
                ELSE 0
            END
            *
            CASE
                WHEN SUM(fp.rev) OVER (PARTITION BY fp.canal, fp.dt, fp.tipo_venda) = 0 THEN 0
                ELSE fp.rev * 1.0 /
                     SUM(fp.rev) OVER (PARTITION BY fp.canal, fp.dt, fp.tipo_venda)
            END
        )
    AS DECIMAL(18,6)) AS net_sales_value,

    (
        fp.rev
      - (fp.ob_r + fp.up1_r + fp.up2_r + fp.up3_r
         + fp.down1_r + fp.down2_r + fp.down3_r)
    ) AS revenue_no_funnel,

    fp.ob_c AS ob_count, fp.ob_r AS ob_revenue,
    fp.up1_c AS up1_count, fp.up1_r AS up1_revenue,
    fp.up2_c AS up2_count, fp.up2_r AS up2_revenue,
    fp.up3_c AS up3_count, fp.up3_r AS up3_revenue,
    fp.down1_c AS down1_count, fp.down1_r AS down1_revenue,
    fp.down2_c AS down2_count, fp.down2_r AS down2_revenue,
    fp.down3_c AS down3_count, fp.down3_r AS down3_revenue,

    fp.front_total_brl AS company_frontend_sales_brl,

    CAST(
        CASE
            WHEN SUM(fp.rev) OVER (PARTITION BY fp.canal, fp.dt, fp.tipo_venda) = 0 THEN 0
            ELSE fp.rev * 1.0 /
                 SUM(fp.rev) OVER (PARTITION BY fp.canal, fp.dt, fp.tipo_venda)
        END
    AS DECIMAL(12,8)) AS cost_sms_pct,

    COALESCE(grt.sms_recuperacao, 0) AS recup_target,
    COALESCE(grt.sms_monetizacao, 0) AS monet_target,
    COALESCE(grt.sms_geral, 0) AS geral_target,

    COALESCE(grt.email_recuperacao, 0) AS email_recup_target,
    COALESCE(grt.email_monetizacao, 0) AS email_monet_target,
    COALESCE(grt.email_geral, 0) AS email_geral_target,

    COALESCE(grt.whatsapp_recuperacao, 0) AS whats_recup_target,
    COALESCE(grt.whatsapp_monetizacao, 0) AS whats_monet_target,
    COALESCE(grt.whatsapp_geral, 0) AS whats_geral_target,

    COALESCE(sc.sms_recup_cost, 0) AS cost_sms,

    CASE
        WHEN fp.tipo_venda IN ('Recuperação', 'Monetização') THEN
            (
                CASE
                    WHEN fp.canal = 'sms' AND fp.tipo_venda = 'Recuperação' THEN sc.sms_recup_cost
                    WHEN fp.canal = 'sms' AND fp.tipo_venda = 'Monetização' THEN sc.sms_monet_cost
                    WHEN fp.canal = 'email' AND fp.tipo_venda = 'Recuperação' THEN sc.email_recup_cost
                    WHEN fp.canal = 'email' AND fp.tipo_venda = 'Monetização' THEN sc.email_monet_cost
                    WHEN fp.canal = 'whatsapp' AND fp.tipo_venda = 'Recuperação' THEN sc.whatsapp_recup_cost
                    WHEN fp.canal = 'whatsapp' AND fp.tipo_venda = 'Monetização' THEN sc.whatsapp_monet_cost
                    ELSE NULL
                END
                *
                CAST(
                    CASE
                        WHEN SUM(fp.rev) OVER (PARTITION BY fp.canal, fp.dt, fp.tipo_venda) = 0 THEN 0
                        ELSE fp.rev * 1.0 /
                             SUM(fp.rev) OVER (PARTITION BY fp.canal, fp.dt, fp.tipo_venda)
                    END
                AS DECIMAL(12,8))
            )
        ELSE NULL
    END AS cost_sms_allocated,

    fp.origem AS origem

FROM final_prep fp
LEFT JOIN instituto_experience.gross_recovery_target grt
  ON grt.yearmonth = DATE_SUB(fp.dt, INTERVAL DAYOFMONTH(fp.dt) - 1 DAY)
LEFT JOIN instituto_experience.sms_costs sc
  ON sc.data = fp.dt;

    -- 3. Troca atômica: usuário nunca vê tabela vazia
    RENAME TABLE
        instituto_experience.dashboard_channels_marketing       TO instituto_experience.dashboard_channels_marketing_old,
        instituto_experience.dashboard_channels_marketing_stage TO instituto_experience.dashboard_channels_marketing,
        instituto_experience.dashboard_channels_marketing_old   TO instituto_experience.dashboard_channels_marketing_stage;

END
```
