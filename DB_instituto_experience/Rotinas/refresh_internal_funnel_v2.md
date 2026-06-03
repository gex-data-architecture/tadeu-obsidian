---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-22 16:27:39"
alterada_em: "2026-05-22 16:27:39"
execucoes: 182
tags: [rotina, procedure]
---

# refresh_internal_funnel_v2

## Dependências

- **Lê:** [[cartpanda_physical]], [[dashboard_gold_clickbank_buygoods]]
- **Escreve:** [[internal_funnel_v2_stage]]
- **Cria:** —
- **Trunca:** [[internal_funnel_v2_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 2.6 s |
| Tempo máx | 2m5s |
| Tempo total | 7m49s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 4,680,699 |

## Corpo SQL

```sql
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.internal_funnel_v2_stage;
        RESIGNAL;
    END;

    TRUNCATE TABLE instituto_experience.internal_funnel_v2_stage;

    INSERT INTO instituto_experience.internal_funnel_v2_stage
    WITH cp_base AS (
        SELECT
            cp.transaction_id, cp.client_email, cp.created_at_date,
            cp.affiliate_name, cp.affiliate_id, cp.payment_status,
            'cartpanda' AS platform,
            TRIM(CASE
                WHEN cp.product_name LIKE '%-%' THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                WHEN REGEXP_LIKE(cp.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                ELSE cp.product_name
            END) AS clean_product_name,
            CASE WHEN cp.offer_name LIKE '%Funil de Nova Ideia #%'
                THEN CONCAT('Funil de Nova Ideia #', SUBSTRING_INDEX(REGEXP_SUBSTR(SUBSTRING_INDEX(cp.offer_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'), ' ', 1))
                ELSE NULL END AS funil_id,
            CASE
                WHEN cp.offer_name LIKE '%[Gestor de Tr_fego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Tráfego:', -1), ']', 1))
                WHEN cp.offer_name LIKE '%[Gestor de Trafego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Trafego:', -1), ']', 1))
                ELSE NULL END AS gestor_trafego,
            CASE WHEN cp.offer_name LIKE '%: [%]%'
                THEN TRIM(REGEXP_REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, ': [', -1), ']', 1), '[^a-zA-Z0-9 ]', ''))
                ELSE NULL END AS traffic_source,
            cp.has_upsell, cp.has_upsell2, cp.has_upsell3,
            cp.has_downsell, cp.has_downsell2, cp.has_downsell3
        FROM instituto_experience.cartpanda_physical cp
        WHERE cp.payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
          AND (cp.affiliate_name IS NULL OR cp.affiliate_name = '')
          AND cp.client_email NOT LIKE '%institutoexperience%'
          AND LOWER(cp.offer_name) NOT LIKE '%affiliate marketing%'
          AND cp.offer_name LIKE '%Nova Ideia%'
          AND cp.created_at_date >= '2026-01-01'
    ),
    cbg_base AS (
        SELECT
            cbg.transaction_id, cbg.client_email, cbg.created_at_date,
            cbg.affiliate_name, NULL AS affiliate_id, cbg.payment_status,
            cbg.platform AS platform,
            TRIM(CASE
                WHEN cbg.product_name LIKE '%-%' THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                WHEN REGEXP_LIKE(cbg.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                ELSE cbg.product_name
            END) AS clean_product_name,
            CASE WHEN cbg.offer_name LIKE '%Funil de Nova Ideia #%'
                THEN CONCAT('Funil de Nova Ideia #', SUBSTRING_INDEX(REGEXP_SUBSTR(SUBSTRING_INDEX(cbg.offer_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'), ' ', 1))
                ELSE NULL END AS funil_id,
            CASE
                WHEN cbg.offer_name LIKE '%[Gestor de Tr_fego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cbg.offer_name, '[Gestor de Tráfego:', -1), ']', 1))
                WHEN cbg.offer_name LIKE '%[Gestor de Trafego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cbg.offer_name, '[Gestor de Trafego:', -1), ']', 1))
                ELSE NULL END AS gestor_trafego,
            CASE WHEN cbg.offer_name LIKE '%: [%]%'
                THEN TRIM(REGEXP_REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(cbg.offer_name, ': [', -1), ']', 1), '[^a-zA-Z0-9 ]', ''))
                ELSE NULL END AS traffic_source,
            cbg.has_upsell, cbg.has_upsell2, cbg.has_upsell3,
            cbg.has_downsell, cbg.has_downsell2, cbg.has_downsell3
        FROM instituto_experience.dashboard_gold_clickbank_buygoods cbg
        WHERE cbg.payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
          AND (cbg.affiliate_name IS NULL OR cbg.affiliate_name = '')
          AND cbg.client_email NOT LIKE '%institutoexperience%'
          AND LOWER(cbg.offer_name) NOT LIKE '%affiliate marketing%'
          AND cbg.offer_name LIKE '%Nova Ideia%'
          AND cbg.created_at_date >= '2026-01-01'
    ),
    combined AS (
        SELECT * FROM cp_base
        UNION ALL
        SELECT * FROM cbg_base
    )

    SELECT DISTINCT
        transaction_id, client_email, created_at_date,
        affiliate_name, affiliate_id, payment_status, platform,
        '1 - Venda Inicial' AS funnel_stage, 1 AS funnel_order,
        funil_id, gestor_trafego, clean_product_name, traffic_source
    FROM combined

    UNION ALL

    SELECT DISTINCT
        transaction_id, client_email, created_at_date,
        affiliate_name, affiliate_id, payment_status, platform,
        '2 - Upsell 1' AS funnel_stage, 2 AS funnel_order,
        funil_id, gestor_trafego, clean_product_name, traffic_source
    FROM combined WHERE has_upsell = 1

    UNION ALL

    SELECT DISTINCT
        transaction_id, client_email, created_at_date,
        affiliate_name, affiliate_id, payment_status, platform,
        '3 - Downsell 1' AS funnel_stage, 3 AS funnel_order,
        funil_id, gestor_trafego, clean_product_name, traffic_source
    FROM combined WHERE has_downsell = 1

    UNION ALL

    SELECT DISTINCT
        transaction_id, client_email, created_at_date,
        affiliate_name, affiliate_id, payment_status, platform,
        '4 - Upsell 2' AS funnel_stage, 4 AS funnel_order,
        funil_id, gestor_trafego, clean_product_name, traffic_source
    FROM combined WHERE has_upsell2 = 1

    UNION ALL

    SELECT DISTINCT
        transaction_id, client_email, created_at_date,
        affiliate_name, affiliate_id, payment_status, platform,
        '5 - Downsell 2' AS funnel_stage, 5 AS funnel_order,
        funil_id, gestor_trafego, clean_product_name, traffic_source
    FROM combined WHERE has_downsell2 = 1

    UNION ALL

    SELECT DISTINCT
        transaction_id, client_email, created_at_date,
        affiliate_name, affiliate_id, payment_status, platform,
        '6 - Upsell 3' AS funnel_stage, 6 AS funnel_order,
        funil_id, gestor_trafego, clean_product_name, traffic_source
    FROM combined WHERE has_upsell3 = 1

    UNION ALL

    SELECT DISTINCT
        transaction_id, client_email, created_at_date,
        affiliate_name, affiliate_id, payment_status, platform,
        '7 - Downsell 3' AS funnel_stage, 7 AS funnel_order,
        funil_id, gestor_trafego, clean_product_name, traffic_source
    FROM combined WHERE has_downsell3 = 1;

    RENAME TABLE
        instituto_experience.internal_funnel_v2       TO instituto_experience.internal_funnel_v2_old,
        instituto_experience.internal_funnel_v2_stage TO instituto_experience.internal_funnel_v2,
        instituto_experience.internal_funnel_v2_old   TO instituto_experience.internal_funnel_v2_stage;

END
```
