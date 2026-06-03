---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-26 20:57:33"
alterada_em: "2026-05-26 20:57:33"
execucoes: 1
tags: [rotina, procedure]
---

# refresh_dashboard_gold_buygoods_teste

## Dependências

- **Lê:** [[tb_gex_buygoods_physical_new]]
- **Escreve:** [[dashboard_gold_buygoods_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_gold_buygoods_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 1 |
| Tempo médio | 78 ms |
| Tempo máx | 78 ms |
| Tempo total | 78 ms |
| Erros | 2 |
| Warnings | 0 |
| Linhas afetadas (total) | 0 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_gold_buygoods_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_gold_buygoods_stage;

    -- 2. Insere na stage (producao continua intacta)
    INSERT INTO instituto_experience.dashboard_gold_buygoods_stage
WITH base AS (
    SELECT
        *,

        CASE
            WHEN sales_type = 'Order Bump' THEN 'order_bump'
            WHEN product_codename LIKE '%UP1%' THEN 'upsell1'
            WHEN product_codename LIKE '%UP2%' THEN 'upsell2'
            WHEN product_codename LIKE '%UP3%' THEN 'upsell3'
            WHEN product_codename LIKE '%DW1%' THEN 'downsell1'
            WHEN product_codename LIKE '%DW2%' THEN 'downsell2'
            WHEN product_codename LIKE '%DW3%' THEN 'downsell3'
            ELSE 'main'
        END AS funnel_type

    FROM instituto_experience.tb_gex_buygoods_physical_new
    WHERE created_at_date >= '2026-01-01'
),

ordenado AS (
    SELECT
        *,
        CASE
            WHEN LAG(created_at_ts) OVER (
                PARTITION BY client_email, account_id
                ORDER BY created_at_ts, transaction_id
            ) IS NULL THEN 1

            WHEN TIMESTAMPDIFF(
                MINUTE,
                LAG(created_at_ts) OVER (
                    PARTITION BY client_email, account_id
                    ORDER BY created_at_ts, transaction_id
                ),
                created_at_ts
            ) > 240 THEN 1

            ELSE 0
        END AS new_group
    FROM base
),

grupo_final AS (
    SELECT
        *,
        SUM(new_group) OVER (
            PARTITION BY client_email, account_id
            ORDER BY created_at_ts, transaction_id
        ) AS purchase_group_id_final
    FROM ordenado
),

main_group AS (
    SELECT
        client_email,
        account_id,
        purchase_group_id_final,

        MAX(
            CASE WHEN funnel_type = 'main'
            THEN product_name END
        ) AS main_product_name,

        MAX(
            CASE WHEN funnel_type = 'main'
            THEN offer_name END
        ) AS main_offer_name,

        MAX(
            CASE WHEN funnel_type = 'main'
            THEN product_sku END
        ) AS main_product_sku

    FROM grupo_final
    GROUP BY 1,2,3
)

SELECT
    g.client_email,
    g.account_id,
    g.purchase_group_id_final,

    COALESCE(m.main_product_name, MAX(g.product_name)) AS product_name,
    COALESCE(m.main_offer_name, MAX(g.offer_name)) AS offer_name,
    COALESCE(m.main_product_sku, MAX(g.product_sku)) AS product_sku,

    ROUND(SUM(g.total_price),2) AS total_price,

    SUM(g.funnel_type='upsell1') AS has_upsell,
    SUM(g.funnel_type='upsell2') AS has_upsell2,
    SUM(g.funnel_type='upsell3') AS has_upsell3,

    ROUND(SUM(
        CASE WHEN g.funnel_type='upsell1'
        THEN g.total_price
        ELSE 0 END
    ),2) AS total_price_upsell

FROM grupo_final g

LEFT JOIN main_group m
    ON m.client_email = g.client_email
   AND m.account_id = g.account_id
   AND m.purchase_group_id_final = g.purchase_group_id_final

GROUP BY
    g.client_email,
    g.account_id,
    g.purchase_group_id_final;

    -- 3. Troca atomica: usuario nunca ve tabela vazia
    RENAME TABLE
        instituto_experience.dashboard_gold_buygoods       TO instituto_experience.dashboard_gold_buygoods_old,
        instituto_experience.dashboard_gold_buygoods_stage TO instituto_experience.dashboard_gold_buygoods,
        instituto_experience.dashboard_gold_buygoods_old   TO instituto_experience.dashboard_gold_buygoods_stage;

END
```
