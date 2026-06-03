---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-22 16:32:12"
alterada_em: "2026-05-22 16:32:12"
execucoes: 182
tags: [rotina, procedure]
---

# refresh_internal_product_v2

## Dependências

- **Lê:** [[cartpanda_physical]], [[dashboard_gold_clickbank_buygoods]], [[digistore_physical]]
- **Escreve:** [[internal_product_v2_stage]]
- **Cria:** —
- **Trunca:** [[internal_product_v2_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 1.9 s |
| Tempo máx | 30.2 s |
| Tempo total | 5m55s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 6,366,516 |

## Corpo SQL

```sql
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.internal_product_v2_stage;
        RESIGNAL;
    END;

    TRUNCATE TABLE instituto_experience.internal_product_v2_stage;

    INSERT INTO instituto_experience.internal_product_v2_stage
    WITH cp_base AS (
        SELECT
            cp.transaction_id, cp.client_email, cp.product_name, cp.created_at_date,
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
            LOWER(cp.product_sku) AS product_sku,
            NULL AS quantity
        FROM instituto_experience.cartpanda_physical cp
        WHERE cp.payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
          AND (cp.affiliate_name IS NULL OR cp.affiliate_name = '')
          AND cp.client_email NOT LIKE '%institutoexperience%'
          AND LOWER(cp.offer_name) NOT LIKE '%affiliate marketing%'
          AND cp.offer_name LIKE '%Nova Ideia%'
          AND cp.created_at_date >= '2026-01-01'
    ),
    ds_base AS (
        SELECT
            ds.transaction_id, ds.client_email, ds.product_name, ds.created_at_date,
            ds.affiliate_name, ds.affiliate_id, ds.payment_status,
            'digistore' AS platform,
            TRIM(CASE
                WHEN ds.product_name LIKE '%-%' THEN TRIM(SUBSTRING_INDEX(ds.product_name, '-', 1))
                WHEN REGEXP_LIKE(ds.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(ds.product_name, '^[^0-9]+'))
                ELSE ds.product_name
            END) AS clean_product_name,
            CASE WHEN ds.offer_name LIKE '%Funil de Nova Ideia #%'
                THEN CONCAT('Funil de Nova Ideia #', SUBSTRING_INDEX(REGEXP_SUBSTR(SUBSTRING_INDEX(ds.offer_name, 'Funil de Nova Ideia #', -1), '^[0-9]+'), ' ', 1))
                ELSE NULL END AS funil_id,
            CASE
                WHEN ds.offer_name LIKE '%[Gestor de Tr_fego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ds.offer_name, '[Gestor de Tráfego:', -1), ']', 1))
                WHEN ds.offer_name LIKE '%[Gestor de Trafego:%]%' THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ds.offer_name, '[Gestor de Trafego:', -1), ']', 1))
                ELSE NULL END AS gestor_trafego,
            CASE WHEN ds.offer_name LIKE '%: [%]%'
                THEN TRIM(REGEXP_REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(ds.offer_name, ': [', -1), ']', 1), '[^a-zA-Z0-9 ]', ''))
                ELSE NULL END AS traffic_source,
            LOWER(ds.product_sku) AS product_sku,
            NULL AS quantity
        FROM instituto_experience.digistore_physical ds
        WHERE ds.payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
          AND (ds.affiliate_name IS NULL OR ds.affiliate_name = '')
          AND ds.client_email NOT LIKE '%institutoexperience%'
          AND LOWER(ds.offer_name) NOT LIKE '%affiliate marketing%'
          AND ds.offer_name LIKE '%Nova Ideia%'
          AND ds.created_at_date >= '2026-01-01'
    ),
    cbg_base AS (
        SELECT
            cbg.transaction_id, cbg.client_email, cbg.product_name, cbg.created_at_date,
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
            NULL AS product_sku,
            cbg.quantity
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
        SELECT * FROM ds_base
        UNION ALL
        SELECT * FROM cbg_base
    )
    SELECT DISTINCT
        transaction_id, client_email, product_name, created_at_date,
        affiliate_name, affiliate_id, payment_status, platform,
        '1 - Vendas Totais' AS funnel_stage, 1 AS funnel_order,
        funil_id, gestor_trafego, clean_product_name, traffic_source
    FROM combined

    UNION ALL

    SELECT DISTINCT
        transaction_id, client_email, product_name, created_at_date,
        affiliate_name, affiliate_id, payment_status, platform,
        '2 - Vendas de 1/2 Bottles' AS funnel_stage, 2 AS funnel_order,
        funil_id, gestor_trafego, clean_product_name, traffic_source
    FROM combined
    WHERE (product_sku LIKE '%1unit%' OR product_sku LIKE '%2unit%')
       OR (platform IN ('clickbank', 'buygoods') AND quantity IN (1, 2))

    UNION ALL

    SELECT DISTINCT
        transaction_id, client_email, product_name, created_at_date,
        affiliate_name, affiliate_id, payment_status, platform,
        '3 - Vendas de 3/4 Bottles' AS funnel_stage, 3 AS funnel_order,
        funil_id, gestor_trafego, clean_product_name, traffic_source
    FROM combined
    WHERE (product_sku LIKE '%3unit%' OR product_sku LIKE '%4unit%')
       OR (platform IN ('clickbank', 'buygoods') AND quantity IN (3, 4))

    UNION ALL

    SELECT DISTINCT
        transaction_id, client_email, product_name, created_at_date,
        affiliate_name, affiliate_id, payment_status, platform,
        '4 - Vendas de 5/6 Bottles' AS funnel_stage, 4 AS funnel_order,
        funil_id, gestor_trafego, clean_product_name, traffic_source
    FROM combined
    WHERE (product_sku LIKE '%5unit%' OR product_sku LIKE '%6unit%')
       OR (platform IN ('clickbank', 'buygoods') AND quantity IN (5, 6));

    RENAME TABLE
        instituto_experience.internal_product_v2       TO instituto_experience.internal_product_v2_old,
        instituto_experience.internal_product_v2_stage TO instituto_experience.internal_product_v2,
        instituto_experience.internal_product_v2_old   TO instituto_experience.internal_product_v2_stage;

END
```
