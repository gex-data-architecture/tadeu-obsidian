---
tipo: procedure
definer: "root@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-01-21 18:53:31"
alterada_em: "2026-01-21 18:53:31"
execucoes: ""
tags: [rotina, procedure]
---

# sp_refresh_internal_gerenciador_meta

## Dependências

- **Lê:** [[cartpanda_physical]], [[funil_produto_mapping]], [[meta_ad_id]]
- **Escreve:** [[internal_gerenciador_meta]]
- **Cria:** —
- **Trunca:** —
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN

    /* ============================
       1. Limpa tabela destino
       ============================ */
    REPLACE INTO instituto_experience.internal_gerenciador_meta (
    ad_name, created_at_date,
    account_id, account_name, campaign_name, adset_name, 
    product_name, clean_product_name, gestor_trafego, funil_id,
    total_transactions, total_price, approved_revenue, commission, taxes, total_refund, product_cost, imposto, net_sales,
    amount_spent_brl, impressions, reach, link_clicks
)
WITH vendas AS (
    SELECT 
        cp.utm_content AS ad_id,
        cp.created_at_date,
        MAX(cp.product_name) AS product_name,
        MAX(TRIM(
            CASE
                WHEN cp.product_name LIKE '%-%'
                    THEN SUBSTRING_INDEX(cp.product_name, '-', 1)
                WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                    THEN REGEXP_SUBSTR(cp.product_name, '^[^0-9]+')
                ELSE cp.product_name
            END
        )) AS clean_product_name,
        MAX(
            CASE
                WHEN cp.offer_name LIKE '%[Gestor de Tr_fego:%]%'
                    THEN SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Tráfego:', -1), ']', 1)
                WHEN cp.offer_name LIKE '%[Gestor de Trafego:%]%'
                    THEN SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Trafego:', -1), ']', 1)
            END
        ) AS gestor_trafego,
        MAX(
            CASE
                WHEN cp.offer_name LIKE '%Funil de Nova Ideia #%'
                    THEN CONCAT(
                        'Funil de Nova Ideia #',
                        REGEXP_SUBSTR(
                            SUBSTRING_INDEX(cp.offer_name, 'Funil de Nova Ideia #', -1),
                            '^[0-9]+'
                        )
                    )
            END
        ) AS funil_id,
        COUNT(DISTINCT cp.transaction_id) AS total_transactions,
        SUM(cp.total_price) AS total_price,
        SUM(IF(cp.payment_status IN ('approved','refunded_partial'), cp.total_price, 0)) AS approved_revenue,
        SUM(cp.commission) AS commission,
        SUM(cp.taxes) AS taxes,
        SUM(cp.total_refund) AS total_refund,
        SUM(cp.product_cost) AS product_cost,
        SUM(IF(cp.payment_status IN ('approved','refunded_partial'), cp.total_price * 0.05, 0)) AS imposto
    FROM cartpanda_physical cp
    WHERE cp.created_at_date >= '2025-11-01'
        AND cp.payment_status IN ('approved','refunded','chargeback','refunded_partial')
        AND (cp.affiliate_name IS NULL OR cp.affiliate_name = '')
        AND cp.client_email NOT LIKE '%institutoexperience%'
        AND cp.offer_name LIKE '%Nova Ideia%'
        AND cp.offer_name NOT LIKE '%Thales Pater%'
        AND LOWER(cp.offer_name) NOT LIKE '%affiliate marketing%'
        AND cp.utm_content IS NOT NULL
        AND cp.utm_content != ''
    GROUP BY cp.utm_content, cp.created_at_date
),
fpm_product AS (
    SELECT funil_id, clean_product_name 
    FROM funil_produto_mapping
)
SELECT
    ma.ad_name,
    ma.created_at_date,
    MAX(ma.account_id) AS account_id,
    MAX(ma.account_name) AS account_name,
    MAX(ma.campaign_name) AS campaign_name,
    MAX(ma.adset_name) AS adset_name,
    v.product_name AS product_name,
    MAX(COALESCE(
        v.clean_product_name, 
        fpm.clean_product_name,
        CASE
            WHEN ma.campaign_name LIKE '%:%'
                THEN SUBSTRING_INDEX(ma.campaign_name, ':', 1)
            ELSE NULL
        END
    )) AS clean_product_name,
    MAX(COALESCE(
        v.gestor_trafego,
        CASE
            WHEN ma.campaign_name LIKE '%[Gestor de Tr_fego:%]%'
                THEN SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Tráfego:', -1), ']', 1)
            WHEN ma.campaign_name LIKE '%[Gestor de Trafego:%]%'
                THEN SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Trafego:', -1), ']', 1)
            ELSE NULL
        END
    )) AS gestor_trafego,
    MAX(COALESCE(
        v.funil_id,
        CASE
            WHEN ma.campaign_name LIKE '%Funil de Nova Ideia #%'
                THEN CONCAT(
                    'Funil de Nova Ideia #',
                    REGEXP_SUBSTR(
                        SUBSTRING_INDEX(ma.campaign_name, 'Funil de Nova Ideia #', -1),
                        '^[0-9]+'
                    )
                )
            ELSE NULL
        END
    )) AS funil_id,
    SUM(COALESCE(v.total_transactions, 0)) AS total_transactions,
    SUM(COALESCE(v.total_price, 0)) AS total_price,
    SUM(COALESCE(v.approved_revenue, 0)) AS approved_revenue,
    SUM(COALESCE(v.commission, 0)) AS commission,
    SUM(COALESCE(v.taxes, 0)) AS taxes,
    SUM(COALESCE(v.total_refund, 0)) AS total_refund,
    SUM(COALESCE(v.product_cost, 0)) AS product_cost,
    SUM(COALESCE(v.imposto, 0)) AS imposto,
    SUM(COALESCE(v.approved_revenue, 0) - COALESCE(v.commission, 0) - COALESCE(v.taxes, 0) - COALESCE(v.total_refund, 0) - COALESCE(v.imposto, 0)) AS net_sales,
    SUM(ma.amount_spent_brl) AS amount_spent_brl,
    SUM(ma.impressions) AS impressions,
    SUM(ma.reach) AS reach,
    SUM(ma.link_clicks) AS link_clicks
FROM meta_ad_id ma
LEFT JOIN vendas v
    ON v.ad_id = ma.ad_id
    AND v.created_at_date = ma.created_at_date
LEFT JOIN fpm_product fpm
    ON COALESCE(v.funil_id, 
        CASE
            WHEN ma.campaign_name LIKE '%Funil de Nova Ideia #%'
                THEN CONCAT(
                    'Funil de Nova Ideia #',
                    REGEXP_SUBSTR(
                        SUBSTRING_INDEX(ma.campaign_name, 'Funil de Nova Ideia #', -1),
                        '^[0-9]+'
                    )
                )
        END
    ) = fpm.funil_id
WHERE 
    ma.created_at_date >= '2025-11-01'
    AND ma.ad_name IS NOT NULL
GROUP BY ma.ad_name, ma.created_at_date
ORDER BY ma.ad_name;

END
```
