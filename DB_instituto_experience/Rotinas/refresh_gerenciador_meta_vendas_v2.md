---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-22 17:17:10"
alterada_em: "2026-05-22 17:17:10"
execucoes: 182
tags: [rotina, procedure]
---

# refresh_gerenciador_meta_vendas_v2

## Dependências

- **Lê:** [[cartpanda_physical]], [[custos_conta_agencia_diaria]], [[custos_gerais_diaria]], [[custos_trafego_gestores_diaria]], [[dashboard_gold_clickbank_buygoods]]
- **Escreve:** [[gerenciador_meta_vendas_v2_stage]]
- **Cria:** —
- **Trunca:** [[gerenciador_meta_vendas_v2_stage]]
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
| Tempo máx | 5.7 s |
| Tempo total | 5m51s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 3,357,789 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.gerenciador_meta_vendas_v2_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.gerenciador_meta_vendas_v2_stage;

    -- 2. Insere na stage (produção continua intacta)
    INSERT INTO instituto_experience.gerenciador_meta_vendas_v2_stage
    WITH vendas AS (
        SELECT
            cp.utm_content,
            cp.created_at_date,
            CASE
                WHEN cp.offer_name LIKE '%[Gestor de Tr_fego:%]%'
                    THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Tráfego:', -1), ']', 1))
                WHEN cp.offer_name LIKE '%[Gestor de Trafego:%]%'
                    THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, '[Gestor de Trafego:', -1), ']', 1))
                ELSE 'Não Encontrado'
            END AS gestor_trafego,
            CASE
                WHEN cp.offer_name LIKE '%Funil de Nova Ideia #%'
                    THEN CONCAT('Funil de Nova Ideia #',
                                REGEXP_SUBSTR(
                                    SUBSTRING_INDEX(cp.offer_name, 'Funil de Nova Ideia #', -1),
                                    '^[0-9]+'
                                ))
                ELSE 'Não Encontrado'
            END AS funil_id,
            CASE
                WHEN cp.offer_name LIKE '%: [%]%'
                    THEN TRIM(REGEXP_REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(cp.offer_name, ': [', -1), ']', 1), '[^a-zA-Z0-9 ]', ''))
                ELSE 'Não Encontrado'
            END AS traffic_source,
            CONCAT(
                UPPER(LEFT(LOWER(REGEXP_REPLACE(TRIM(CASE
                    WHEN cp.product_name LIKE '%-%'            THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                    WHEN REGEXP_LIKE(cp.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                    ELSE cp.product_name
                END), '[^a-zA-Z0-9]', '')), 1)),
                SUBSTRING(LOWER(REGEXP_REPLACE(TRIM(CASE
                    WHEN cp.product_name LIKE '%-%'            THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                    WHEN REGEXP_LIKE(cp.product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                    ELSE cp.product_name
                END), '[^a-zA-Z0-9]', '')), 2)
            ) AS clean_product_name,
            COUNT(DISTINCT cp.transaction_id)                    AS total_transactions,
            COALESCE(SUM(cp.total_price), 0)                     AS total_price,
            COALESCE(SUM(cp.commission), 0)                      AS commission,
            COALESCE(SUM(cp.taxes), 0)                           AS taxes,
            COALESCE(SUM(cp.total_refund), 0)                    AS total_refund,
            COALESCE(SUM(cp.product_cost), 0)                    AS product_cost,
            COALESCE(SUM(cp.total_price_usd), 0)                 AS total_price_usd,
            COALESCE(SUM(cp.commission_usd), 0)                  AS commission_usd,
            COALESCE(SUM(cp.taxes_usd), 0)                       AS taxes_usd,
            COALESCE(SUM(cp.total_refund_usd), 0)                AS total_refund_usd,
            COALESCE(SUM(cp.product_cost_usd), 0)                AS product_cost_usd,
            SUM(CASE WHEN cp.payment_status IN ('approved','refunded_partial')
                     THEN cp.total_price * 0.03 ELSE 0 END)      AS imposto,
            SUM(CASE WHEN cp.payment_status IN ('approved','refunded_partial')
                     THEN cp.total_price_usd * 0.03 ELSE 0 END)  AS imposto_usd,
            COALESCE(SUM(cp.revenue_afiliado), 0)                AS revenue_afiliado,
            COALESCE(SUM(cp.revenue_afiliado_usd), 0)            AS revenue_afiliado_usd
        FROM (
            -- CARTPANDA
            SELECT
                transaction_id, payment_status, offer_name, utm_content,
                created_at_date, affiliate_name, client_email,
                product_name,
                total_price,      ROUND(total_price   / 5.2, 2) AS total_price_usd,
                commission,       ROUND(commission    / 5.2, 2) AS commission_usd,
                taxes,            ROUND(taxes         / 5.2, 2) AS taxes_usd,
                total_refund,     ROUND(total_refund  / 5.2, 2) AS total_refund_usd,
                product_cost,     ROUND(product_cost  / 5.2, 2) AS product_cost_usd,
                NULL AS revenue_afiliado, NULL AS revenue_afiliado_usd
            FROM instituto_experience.cartpanda_physical
            WHERE created_at_date >= '2026-01-01'
              AND (affiliate_name IS NULL OR affiliate_name = '')
              AND client_email NOT LIKE '%institutoexperience%'
              AND LOWER(offer_name) NOT LIKE '%affiliate marketing%'
              AND offer_name LIKE '%Nova Ideia%'
              AND offer_name NOT LIKE '%Thales Pater%'
              AND offer_name NOT LIKE '%SEO Marketing%'

            UNION ALL

            -- CLICKBANK + BUYGOODS (somente house traffic)
            SELECT
                transaction_id, payment_status, offer_name, utm_content,
                created_at_date, affiliate_name, client_email,
                product_name,
                total_price, total_price_usd,
                commission, commission_usd,
                taxes, taxes_usd,
                total_refund, total_refund_usd,
                product_cost, product_cost_usd,
                revenue_afiliado, revenue_afiliado_usd
            FROM instituto_experience.dashboard_gold_clickbank_buygoods
            WHERE created_at_date >= '2026-01-01'
              AND is_house_traffic = 1
        ) cp
        WHERE cp.payment_status IN ('approved','refunded','chargeback','refunded_partial')
          AND cp.utm_content IS NOT NULL
          AND cp.utm_content != ''
        GROUP BY
            cp.utm_content,
            cp.created_at_date,
            gestor_trafego,
            funil_id,
            traffic_source,
            clean_product_name
    ),

    ctg_agg AS (
        SELECT
            data, fonte, gestor,
            CONCAT(
                UPPER(LEFT(LOWER(REGEXP_REPLACE(produto, '[^a-zA-Z0-9]', '')), 1)),
                SUBSTRING(LOWER(REGEXP_REPLACE(produto, '[^a-zA-Z0-9]', '')), 2)
            ) AS produto,
            SUM(custo_usd)       AS custo_usd,
            SUM(custo_usd) * 5.2 AS custo_brl
        FROM instituto_experience.custos_trafego_gestores_diaria
        GROUP BY data, fonte, custos_trafego_gestores_diaria.produto, gestor
    ),

    cca_agg AS (
        SELECT
            data, fonte, gestor,
            CONCAT(
                UPPER(LEFT(LOWER(REGEXP_REPLACE(produto, '[^a-zA-Z0-9]', '')), 1)),
                SUBSTRING(LOWER(REGEXP_REPLACE(produto, '[^a-zA-Z0-9]', '')), 2)
            ) AS produto,
            SUM(taxa)             AS taxa_usd,
            SUM(taxa) * 5.2       AS taxa,
            SUM(custo)            AS custo_usd,
            SUM(custo) * 5.2      AS custo,
            SUM(custo_real)       AS custo_real_usd,
            SUM(custo_real) * 5.2 AS custo_real
        FROM instituto_experience.custos_conta_agencia_diaria
        GROUP BY data, fonte, custos_conta_agencia_diaria.produto, gestor
    ),

    cg_agg AS (
        SELECT
            data, fonte, gestor,
            SUM(custo) AS custos_gerais
        FROM instituto_experience.custos_gerais_diaria
        GROUP BY data, fonte, gestor
    ),

    -- =================================================================
    -- CORREÇÃO: vendas_custo agrega por (data, fonte, produto, gestor)
    -- sem utm_content, para que o join com ctg_agg, cca_agg e cg_agg
    -- produza exatamente 1 linha de custo por combinação — evitando
    -- duplicação quando existem múltiplos utm_content no mesmo grupo.
    -- =================================================================
    vendas_custo AS (
        SELECT
            v.created_at_date,
            v.gestor_trafego,
            v.traffic_source,
            v.clean_product_name,
            -- total de receita do grupo para distribuição proporcional por utm_content
            SUM(v.total_price)                        AS total_price_grupo,
            ctg.custo_brl                             AS ctg_custo_brl,
            ctg.custo_usd                             AS ctg_custo_usd,
            cg.custos_gerais                          AS ctg_custos_gerais,
            ROUND(cg.custos_gerais / 5.2, 2)          AS ctg_custos_gerais_usd,
            cca.taxa                                  AS cca_taxa,
            cca.custo                                 AS cca_custo,
            cca.custo_real                            AS cca_custo_real,
            cca.taxa_usd                              AS cca_taxa_usd,
            cca.custo_usd                             AS cca_custo_usd,
            cca.custo_real_usd                        AS cca_custo_real_usd
        FROM (
            SELECT
                created_at_date, gestor_trafego, traffic_source, clean_product_name,
                SUM(total_price) AS total_price
            FROM vendas
            GROUP BY created_at_date, gestor_trafego, traffic_source, clean_product_name
        ) v
        LEFT JOIN ctg_agg ctg
            ON  v.created_at_date    = ctg.data
            AND v.traffic_source     = ctg.fonte
            AND v.clean_product_name <=> ctg.produto
            AND v.gestor_trafego     <=> ctg.gestor
        LEFT JOIN cca_agg cca
            ON  v.created_at_date    = cca.data
            AND v.traffic_source     = cca.fonte
            AND v.clean_product_name <=> cca.produto
            AND v.gestor_trafego     <=> cca.gestor
        LEFT JOIN cg_agg cg
            ON  v.created_at_date    = cg.data
            AND v.traffic_source     = cg.fonte
            AND v.gestor_trafego    <=> cg.gestor
        GROUP BY
            v.created_at_date, v.gestor_trafego, v.traffic_source, v.clean_product_name,
            ctg.custo_brl, ctg.custo_usd,
            cg.custos_gerais,
            cca.taxa, cca.custo, cca.custo_real,
            cca.taxa_usd, cca.custo_usd, cca.custo_real_usd
    ),

    pre_final AS (
        -- PARTE 1: linhas de vendas com custos via vendas_custo (sem duplicação)
        SELECT
            v.utm_content,
            v.created_at_date,
            v.gestor_trafego,
            v.funil_id,
            v.traffic_source,
            v.clean_product_name,
            v.total_transactions,
            v.total_price,
            v.commission,
            v.taxes,
            v.total_refund,
            v.product_cost,
            v.imposto,
            v.revenue_afiliado,
            vc.ctg_custo_brl,
            vc.ctg_custos_gerais,
            vc.cca_taxa,
            vc.cca_custo,
            vc.cca_custo_real,
            v.imposto_usd,
            v.total_price_usd,
            v.commission_usd,
            v.taxes_usd,
            v.total_refund_usd,
            v.product_cost_usd,
            v.revenue_afiliado_usd,
            ROUND(v.revenue_afiliado * 0.05, 4)       AS imposto_afiliado,
            ROUND(v.revenue_afiliado_usd * 0.05, 2)   AS imposto_afiliado_usd,
            vc.ctg_custo_usd,
            vc.ctg_custos_gerais_usd,
            vc.cca_taxa_usd,
            vc.cca_custo_usd,
            vc.cca_custo_real_usd
        FROM vendas v
        LEFT JOIN vendas_custo vc
            ON  v.created_at_date    = vc.created_at_date
            AND v.gestor_trafego     = vc.gestor_trafego
            AND v.traffic_source     = vc.traffic_source
            AND v.clean_product_name = vc.clean_product_name

        UNION ALL

        -- PARTE 2: custos ctg sem venda correspondente
        SELECT
            NULL, ctg2.data,
            COALESCE(ctg2.gestor, 'Não Encontrado'),
            'Não Encontrado', ctg2.fonte,
            COALESCE(ctg2.produto, 'Não Encontrado'),
            0, 0, 0, 0, 0, 0, 0, 0,
            ctg2.custo_brl, NULL, NULL, NULL, NULL,
            0, 0, 0, 0, 0, 0, 0, 0, 0,
            ctg2.custo_usd, NULL, NULL, NULL, NULL
        FROM ctg_agg ctg2
        WHERE NOT EXISTS (
            SELECT 1 FROM vendas v2
            WHERE v2.created_at_date    = ctg2.data
              AND v2.traffic_source     = ctg2.fonte
              AND v2.clean_product_name <=> ctg2.produto
              AND v2.gestor_trafego     <=> ctg2.gestor
        )

        UNION ALL

        -- PARTE 3: custos cca sem venda correspondente
        SELECT
            NULL, cca2.data,
            COALESCE(cca2.gestor, 'Não Encontrado'),
            'Não Encontrado', cca2.fonte,
            COALESCE(cca2.produto, 'Não Encontrado'),
            0, 0, 0, 0, 0, 0, 0, 0,
            NULL, NULL, cca2.taxa, cca2.custo, cca2.custo_real,
            0, 0, 0, 0, 0, 0, 0, 0, 0,
            NULL, NULL,
            cca2.taxa_usd, cca2.custo_usd, cca2.custo_real_usd
        FROM cca_agg cca2
        WHERE NOT EXISTS (
            SELECT 1 FROM vendas v3
            WHERE v3.created_at_date    = cca2.data
              AND v3.traffic_source     = cca2.fonte
              AND v3.clean_product_name <=> cca2.produto
              AND v3.gestor_trafego     <=> cca2.gestor
        )
    )

    -- =================================================================
    -- SELECT FINAL sem redistribuição
    -- =================================================================
    SELECT
        p.utm_content,
        p.created_at_date,
        p.gestor_trafego,
        p.funil_id,
        p.traffic_source,
        p.clean_product_name,
        p.total_transactions,
        ROUND(p.total_price, 2)           AS total_price,
        ROUND(p.commission, 2)            AS commission,
        ROUND(p.taxes, 2)                 AS taxes,
        ROUND(p.total_refund, 2)          AS total_refund,
        ROUND(p.product_cost, 2)          AS product_cost,
        ROUND(p.imposto, 2)               AS imposto,
        ROUND(p.revenue_afiliado, 2)      AS revenue_afiliado,
        p.ctg_custo_brl,
        p.ctg_custos_gerais,
        p.cca_taxa,
        p.cca_custo,
        p.cca_custo_real,
        ROUND(p.imposto_usd, 2)           AS imposto_usd,
        ROUND(p.total_price_usd, 2)       AS total_price_usd,
        ROUND(p.commission_usd, 2)        AS commission_usd,
        ROUND(p.taxes_usd, 2)             AS taxes_usd,
        ROUND(p.total_refund_usd, 2)      AS total_refund_usd,
        ROUND(p.product_cost_usd, 2)      AS product_cost_usd,
        ROUND(p.revenue_afiliado_usd, 2)  AS revenue_afiliado_usd,
        ROUND(p.imposto_afiliado, 4)      AS imposto_afiliado,
        ROUND(p.imposto_afiliado_usd, 2)  AS imposto_afiliado_usd,
        p.ctg_custo_usd,
        p.ctg_custos_gerais_usd,
        p.cca_taxa_usd,
        p.cca_custo_usd,
        p.cca_custo_real_usd

    FROM pre_final p
    WHERE p.traffic_source NOT IN ('Thumb Recuperao', 'Back Redirect');

    -- 3. Troca atômica: usuário nunca vê tabela vazia
    RENAME TABLE
        instituto_experience.gerenciador_meta_vendas_v2       TO instituto_experience.gerenciador_meta_vendas_v2_old,
        instituto_experience.gerenciador_meta_vendas_v2_stage TO instituto_experience.gerenciador_meta_vendas_v2,
        instituto_experience.gerenciador_meta_vendas_v2_old   TO instituto_experience.gerenciador_meta_vendas_v2_stage;

END
```
