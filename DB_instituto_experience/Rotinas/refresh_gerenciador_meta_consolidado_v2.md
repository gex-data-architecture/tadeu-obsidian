---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-04-02 22:29:55"
alterada_em: "2026-04-02 22:29:55"
execucoes: 182
tags: [rotina, procedure]
---

# refresh_gerenciador_meta_consolidado_v2

## Dependências

- **Lê:** [[gerenciador_meta_ads_v2]], [[gerenciador_meta_vendas_v2]]
- **Escreve:** [[gerenciador_meta_consolidado_v2_stage]]
- **Cria:** —
- **Trunca:** [[gerenciador_meta_consolidado_v2_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 56.7 s |
| Tempo máx | 3m45s |
| Tempo total | 2h52m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 223,291,248 |

## Corpo SQL

```sql
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.gerenciador_meta_consolidado_v2_stage;
        RESIGNAL;
    END;

    TRUNCATE TABLE instituto_experience.gerenciador_meta_consolidado_v2_stage;

    INSERT INTO instituto_experience.gerenciador_meta_consolidado_v2_stage
    WITH
    v AS (
        SELECT * FROM instituto_experience.gerenciador_meta_vendas_v2
        WHERE created_at_date >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
    ),
    a AS (
        SELECT * FROM instituto_experience.gerenciador_meta_ads_v2
        WHERE created_at_date >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
    )

    SELECT
        COALESCE(v.utm_content, a.ad_id)               AS utm_content,
        COALESCE(v.created_at_date, a.created_at_date) AS created_at_date,
        COALESCE(v.gestor_trafego, a.gestor_trafego)   AS gestor_trafego,
        COALESCE(v.funil_id,       a.funil_id)          AS funil_id,
        COALESCE(v.traffic_source, a.produto)           AS traffic_source,
        COALESCE(v.clean_product_name, a.produto)       AS produto,
        a.ad_id,
        a.ad_name,
        a.account_name,
        a.campaign_name,
        a.adset_name,
        v.total_transactions,
        v.total_price,
        v.commission,
        v.taxes,
        v.total_refund,
        v.product_cost,
        v.imposto,
        v.revenue_afiliado,
        v.imposto_afiliado,
        v.total_price_usd,
        v.commission_usd,
        v.taxes_usd,
        v.total_refund_usd,
        v.product_cost_usd,
        v.imposto_usd,
        v.revenue_afiliado_usd,
        v.imposto_afiliado_usd,
        v.ctg_custo_brl,
        v.ctg_custos_gerais,
        v.ctg_custo_usd,
        v.ctg_custos_gerais_usd,
        v.cca_taxa,
        v.cca_custo,
        v.cca_custo_real,
        v.cca_taxa_usd,
        v.cca_custo_usd,
        v.cca_custo_real_usd,
        a.amount_spent_brl,
        a.spent_taxes,
        a.amount_spent_total,
        a.amount_spent_total_usd,
        a.impressions,
        a.reach,
        a.link_clicks,
        CASE
            WHEN v.utm_content IS NOT NULL AND a.ad_id IS NOT NULL THEN 'match'
            WHEN v.utm_content IS NOT NULL                         THEN 'somente_venda'
            ELSE                                                        'somente_ad'
        END AS origem

    FROM v
    LEFT JOIN a
        ON  v.utm_content     = a.ad_id
        AND v.created_at_date = a.created_at_date

    UNION ALL

    SELECT
        a.ad_id,
        a.created_at_date,
        a.gestor_trafego,
        a.funil_id,
        a.produto,
        a.produto,
        a.ad_id,
        a.ad_name,
        a.account_name,
        a.campaign_name,
        a.adset_name,
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,        -- 9 métricas vendas BRL
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,              -- 8 métricas vendas USD
        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,  -- 10 custos
        a.amount_spent_brl,
        a.spent_taxes,
        a.amount_spent_total,
        a.amount_spent_total_usd,
        a.impressions,
        a.reach,
        a.link_clicks,
        'somente_ad'

    FROM (
        SELECT * FROM instituto_experience.gerenciador_meta_ads_v2
        WHERE created_at_date >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
    ) a
    LEFT JOIN (
        SELECT utm_content, created_at_date
        FROM instituto_experience.gerenciador_meta_vendas_v2
        WHERE created_at_date >= DATE_SUB(CURDATE(), INTERVAL 60 DAY)
    ) v
        ON  v.utm_content     = a.ad_id
        AND v.created_at_date = a.created_at_date
    WHERE v.utm_content IS NULL;

    -- Swap atômico
    RENAME TABLE
        instituto_experience.gerenciador_meta_consolidado_v2       TO instituto_experience.gerenciador_meta_consolidado_v2_old,
        instituto_experience.gerenciador_meta_consolidado_v2_stage TO instituto_experience.gerenciador_meta_consolidado_v2,
        instituto_experience.gerenciador_meta_consolidado_v2_old   TO instituto_experience.gerenciador_meta_consolidado_v2_stage;

END
```
