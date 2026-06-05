---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-22 15:05:07"
alterada_em: "2026-05-22 15:05:07"
execucoes: 181
tags: [rotina, procedure]
---

# refresh_dashboard_channels_country_daily

## Dependências

- **Lê:** [[cartpanda_physical]], [[dashboard_gold_clickbank_buygoods]], [[gross_recovery_target]]
- **Escreve:** [[dashboard_channels_country_daily_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_channels_country_daily_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 181 |
| Tempo médio | 16.9 s |
| Tempo máx | 27.9 s |
| Tempo total | 51m2s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 1,500,420 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_channels_country_daily_stage;
        RESIGNAL;
    END;

    TRUNCATE TABLE instituto_experience.dashboard_channels_country_daily_stage;

    INSERT INTO instituto_experience.dashboard_channels_country_daily_stage
    WITH

    combined_source AS (
        SELECT
            offer_name,
            product_name,
            product_sku,
            payment_status,
            total_price,
            client_country,
            created_at_date,
            LOWER(
                REGEXP_REPLACE(
                    TRIM(
                        CASE
                            WHEN product_name LIKE '%-%' THEN TRIM(SUBSTRING_INDEX(product_name, '-', 1))
                            WHEN REGEXP_LIKE(product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(product_name, '^[^0-9]+'))
                            ELSE product_name
                        END
                    ),
                    '[^a-zA-Z0-9]',
                    ''
                )
            ) AS product_key,
            'cartpanda' AS origem
        FROM instituto_experience.cartpanda_physical
        WHERE created_at_date >= '2025-01-01'

        UNION ALL

        SELECT
            offer_name,
            product_name,
            CONCAT(quantity, 'unit') AS product_sku,
            payment_status,
            total_price,
            client_country,
            created_at_date,
            LOWER(
                REGEXP_REPLACE(
                    TRIM(
                        CASE
                            WHEN product_name LIKE '%-%' THEN TRIM(SUBSTRING_INDEX(product_name, '-', 1))
                            WHEN REGEXP_LIKE(product_name, '[0-9]') THEN TRIM(REGEXP_SUBSTR(product_name, '^[^0-9]+'))
                            ELSE product_name
                        END
                    ),
                    '[^a-zA-Z0-9]',
                    ''
                )
            ) AS product_key,
            platform AS origem
        FROM instituto_experience.dashboard_gold_clickbank_buygoods
        WHERE created_at_date >= '2025-01-01'
    ),

    total_geral AS (
        SELECT
            created_at_date,
            client_country,
            product_key,
            origem,
            SUM(total_price) AS total_price_all
        FROM combined_source
        GROUP BY created_at_date, client_country, product_key, origem
    ),

    vendas_6m_sms AS (
        SELECT client_country, origem, COUNT(*) AS vendas_rec_6m
        FROM combined_source
        WHERE created_at_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
          AND LOWER(offer_name) LIKE '%recup%'
          AND LOWER(offer_name) LIKE '%sms%'
          AND payment_status IS NOT NULL
          AND LOWER(offer_name) NOT LIKE '%parceiro%'
          AND UPPER(offer_name) NOT LIKE '%DAMAS%'
        GROUP BY client_country, origem
    ),
    vendas_6m_monet_sms AS (
        SELECT client_country, origem, COUNT(*) AS vendas_monet_6m
        FROM combined_source
        WHERE created_at_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
          AND LOWER(offer_name) LIKE '%mone%'
          AND LOWER(offer_name) LIKE '%sms%'
          AND payment_status IS NOT NULL
          AND LOWER(offer_name) NOT LIKE '%parceiro%'
          AND UPPER(offer_name) NOT LIKE '%DAMAS%'
        GROUP BY client_country, origem
    ),

    vendas_6m_email AS (
        SELECT client_country, origem, COUNT(*) AS vendas_rec_6m
        FROM combined_source
        WHERE created_at_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
          AND LOWER(offer_name) LIKE '%recup%'
          AND (LOWER(offer_name) LIKE '%email%' OR LOWER(offer_name) LIKE '%e-mail%')
          AND payment_status IS NOT NULL
          AND LOWER(offer_name) NOT LIKE '%parceiro%'
          AND UPPER(offer_name) NOT LIKE '%DAMAS%'
        GROUP BY client_country, origem
    ),
    vendas_6m_monet_email AS (
        SELECT client_country, origem, COUNT(*) AS vendas_monet_6m
        FROM combined_source
        WHERE created_at_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
          AND LOWER(offer_name) LIKE '%mone%'
          AND (LOWER(offer_name) LIKE '%email%' OR LOWER(offer_name) LIKE '%e-mail%')
          AND payment_status IS NOT NULL
          AND LOWER(offer_name) NOT LIKE '%parceiro%'
          AND UPPER(offer_name) NOT LIKE '%DAMAS%'
        GROUP BY client_country, origem
    ),

    vendas_6m_whatsapp AS (
        SELECT client_country, origem, COUNT(*) AS vendas_rec_6m
        FROM combined_source
        WHERE created_at_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
          AND LOWER(offer_name) LIKE '%recup%'
          AND LOWER(offer_name) LIKE '%whatsapp%'
          AND payment_status IS NOT NULL
          AND LOWER(offer_name) NOT LIKE '%parceiro%'
          AND UPPER(offer_name) NOT LIKE '%DAMAS%'
        GROUP BY client_country, origem
    ),
    vendas_6m_monet_whatsapp AS (
        SELECT client_country, origem, COUNT(*) AS vendas_monet_6m
        FROM combined_source
        WHERE created_at_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
          AND LOWER(offer_name) LIKE '%mone%'
          AND LOWER(offer_name) LIKE '%whatsapp%'
          AND payment_status IS NOT NULL
          AND LOWER(offer_name) NOT LIKE '%parceiro%'
          AND UPPER(offer_name) NOT LIKE '%DAMAS%'
        GROUP BY client_country, origem
    )

    SELECT
        'sms' AS canal,
        a.created_at_date,
        a.client_country,
        a.product_key,

        SUM(CASE WHEN LOWER(a.offer_name) LIKE '%recup%' AND LOWER(a.offer_name) LIKE '%sms%' THEN a.total_price ELSE 0 END) AS total_price_recuperacao,
        SUM(CASE WHEN LOWER(a.offer_name) LIKE '%mone%'  AND LOWER(a.offer_name) LIKE '%sms%' THEN a.total_price ELSE 0 END) AS total_price_monetizacao,
        SUM(CASE WHEN LOWER(a.offer_name) LIKE '%broad%' AND LOWER(a.offer_name) LIKE '%sms%' THEN a.total_price ELSE 0 END) AS total_price_broadcast,

        SUM(
            CASE
                WHEN NOT (
                    (LOWER(a.offer_name) LIKE '%recup%' AND LOWER(a.offer_name) LIKE '%sms%')
                 OR (LOWER(a.offer_name) LIKE '%mone%'  AND LOWER(a.offer_name) LIKE '%sms%')
                 OR (LOWER(a.offer_name) LIKE '%broad%' AND LOWER(a.offer_name) LIKE '%sms%')
                )
                THEN a.total_price ELSE 0
            END
        ) AS total_price_outros,

        MAX(tg.total_price_all) AS total_price_total,

        COUNT(CASE WHEN LOWER(a.offer_name) LIKE '%recup%' AND LOWER(a.offer_name) LIKE '%sms%' AND a.payment_status IS NOT NULL THEN 1 END) AS total_vendas_recuperacao,
        COUNT(CASE WHEN LOWER(a.offer_name) LIKE '%mone%'  AND LOWER(a.offer_name) LIKE '%sms%' AND a.payment_status IS NOT NULL THEN 1 END) AS total_vendas_monetizacao,
        COUNT(CASE WHEN LOWER(a.offer_name) LIKE '%broad%' AND LOWER(a.offer_name) LIKE '%sms%' AND a.payment_status IS NOT NULL THEN 1 END) AS total_vendas_broadcast,

        COUNT(
            CASE
                WHEN NOT (
                    (LOWER(a.offer_name) LIKE '%recup%' AND LOWER(a.offer_name) LIKE '%sms%')
                 OR (LOWER(a.offer_name) LIKE '%mone%'  AND LOWER(a.offer_name) LIKE '%sms%')
                 OR (LOWER(a.offer_name) LIKE '%broad%' AND LOWER(a.offer_name) LIKE '%sms%')
                )
                AND a.payment_status IS NOT NULL
                THEN 1
            END
        ) AS total_vendas_outros,

        COUNT(CASE WHEN a.payment_status IS NOT NULL THEN 1 END) AS total_vendas_total,

        CASE WHEN b.vendas_rec_6m > 10 THEN 1 ELSE 0 END AS flag_sms_pais,
        CASE WHEN bm.vendas_monet_6m > 10 THEN 1 ELSE 0 END AS flag_sms_pais_monet,

        MAX(COALESCE(grt.sms_recuperacao, 0)) AS recup_target,
        MAX(COALESCE(grt.sms_monetizacao, 0)) AS monet_target,
        MAX(COALESCE(grt.sms_geral, 0)) AS geral_target,

        a.origem AS origem

    FROM combined_source a
    LEFT JOIN total_geral tg
        ON a.created_at_date = tg.created_at_date
        AND a.client_country = tg.client_country
        AND a.product_key = tg.product_key
        AND a.origem = tg.origem
    LEFT JOIN vendas_6m_sms b
        ON a.client_country = b.client_country
       AND a.origem = b.origem
    LEFT JOIN vendas_6m_monet_sms bm
        ON a.client_country = bm.client_country
       AND a.origem = bm.origem
    LEFT JOIN instituto_experience.gross_recovery_target grt
      ON grt.yearmonth = DATE_SUB(a.created_at_date, INTERVAL DAYOFMONTH(a.created_at_date) - 1 DAY)

    WHERE LOWER(a.offer_name) LIKE '%sms%'
      AND LOWER(a.offer_name) NOT LIKE '%parceiro%'
      AND UPPER(a.offer_name) NOT LIKE '%DAMAS%'

    GROUP BY
        a.created_at_date,
        a.client_country,
        a.product_key,
        a.origem,
        CASE WHEN b.vendas_rec_6m > 10 THEN 1 ELSE 0 END,
        CASE WHEN bm.vendas_monet_6m > 10 THEN 1 ELSE 0 END

    UNION ALL

    SELECT
        'email' AS canal,
        a.created_at_date,
        a.client_country,
        a.product_key,

        SUM(CASE WHEN LOWER(a.offer_name) LIKE '%recup%' AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%') THEN a.total_price ELSE 0 END),
        SUM(CASE WHEN LOWER(a.offer_name) LIKE '%mone%'  AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%') THEN a.total_price ELSE 0 END),
        SUM(CASE WHEN LOWER(a.offer_name) LIKE '%broad%' AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%') THEN a.total_price ELSE 0 END),

        SUM(
            CASE
                WHEN NOT (
                    (LOWER(a.offer_name) LIKE '%recup%' AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%'))
                 OR (LOWER(a.offer_name) LIKE '%mone%'  AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%'))
                 OR (LOWER(a.offer_name) LIKE '%broad%' AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%'))
                )
                THEN a.total_price ELSE 0
            END
        ),

        MAX(tg.total_price_all),

        COUNT(CASE WHEN LOWER(a.offer_name) LIKE '%recup%' AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%') AND a.payment_status IS NOT NULL THEN 1 END),
        COUNT(CASE WHEN LOWER(a.offer_name) LIKE '%mone%'  AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%') AND a.payment_status IS NOT NULL THEN 1 END),
        COUNT(CASE WHEN LOWER(a.offer_name) LIKE '%broad%' AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%') AND a.payment_status IS NOT NULL THEN 1 END),

        COUNT(
            CASE
                WHEN NOT (
                    (LOWER(a.offer_name) LIKE '%recup%' AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%'))
                 OR (LOWER(a.offer_name) LIKE '%mone%'  AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%'))
                 OR (LOWER(a.offer_name) LIKE '%broad%' AND (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%'))
                )
                AND a.payment_status IS NOT NULL
                THEN 1
            END
        ),
        COUNT(CASE WHEN a.payment_status IS NOT NULL THEN 1 END),

        CASE WHEN b.vendas_rec_6m > 10 THEN 1 ELSE 0 END,
        CASE WHEN bm.vendas_monet_6m > 10 THEN 1 ELSE 0 END,

        MAX(COALESCE(grt.email_recuperacao, 0)),
        MAX(COALESCE(grt.email_monetizacao, 0)),
        MAX(COALESCE(grt.email_geral, 0)),

        a.origem AS origem

    FROM combined_source a
    LEFT JOIN total_geral tg
        ON a.created_at_date = tg.created_at_date
        AND a.client_country = tg.client_country
        AND a.product_key = tg.product_key
        AND a.origem = tg.origem
    LEFT JOIN vendas_6m_email b
        ON a.client_country = b.client_country
       AND a.origem = b.origem
    LEFT JOIN vendas_6m_monet_email bm
        ON a.client_country = bm.client_country
       AND a.origem = bm.origem
    LEFT JOIN instituto_experience.gross_recovery_target grt
      ON grt.yearmonth = DATE_SUB(a.created_at_date, INTERVAL DAYOFMONTH(a.created_at_date) - 1 DAY)

    WHERE (LOWER(a.offer_name) LIKE '%email%' OR LOWER(a.offer_name) LIKE '%e-mail%')
      AND LOWER(a.offer_name) NOT LIKE '%parceiro%'
      AND UPPER(a.offer_name) NOT LIKE '%DAMAS%'

    GROUP BY
        a.created_at_date,
        a.client_country,
        a.product_key,
        a.origem,
        CASE WHEN b.vendas_rec_6m > 10 THEN 1 ELSE 0 END,
        CASE WHEN bm.vendas_monet_6m > 10 THEN 1 ELSE 0 END

    UNION ALL

    SELECT
        'whatsapp' AS canal,
        a.created_at_date,
        a.client_country,
        a.product_key,

        SUM(CASE WHEN LOWER(a.offer_name) LIKE '%recup%' AND LOWER(a.offer_name) LIKE '%whatsapp%' THEN a.total_price ELSE 0 END),
        SUM(CASE WHEN LOWER(a.offer_name) LIKE '%mone%'  AND LOWER(a.offer_name) LIKE '%whatsapp%' THEN a.total_price ELSE 0 END),
        SUM(CASE WHEN LOWER(a.offer_name) LIKE '%broad%' AND LOWER(a.offer_name) LIKE '%whatsapp%' THEN a.total_price ELSE 0 END),

        SUM(
            CASE
                WHEN NOT (
                    (LOWER(a.offer_name) LIKE '%recup%' AND LOWER(a.offer_name) LIKE '%whatsapp%')
                 OR (LOWER(a.offer_name) LIKE '%mone%'  AND LOWER(a.offer_name) LIKE '%whatsapp%')
                 OR (LOWER(a.offer_name) LIKE '%broad%' AND LOWER(a.offer_name) LIKE '%whatsapp%')
                )
                THEN a.total_price ELSE 0
            END
        ),

        MAX(tg.total_price_all),

        COUNT(CASE WHEN LOWER(a.offer_name) LIKE '%recup%' AND LOWER(a.offer_name) LIKE '%whatsapp%' AND a.payment_status IS NOT NULL THEN 1 END),
        COUNT(CASE WHEN LOWER(a.offer_name) LIKE '%mone%'  AND LOWER(a.offer_name) LIKE '%whatsapp%' AND a.payment_status IS NOT NULL THEN 1 END),
        COUNT(CASE WHEN LOWER(a.offer_name) LIKE '%broad%' AND LOWER(a.offer_name) LIKE '%whatsapp%' AND a.payment_status IS NOT NULL THEN 1 END),

        COUNT(
            CASE
                WHEN NOT (
                    (LOWER(a.offer_name) LIKE '%recup%' AND LOWER(a.offer_name) LIKE '%whatsapp%')
                 OR (LOWER(a.offer_name) LIKE '%mone%'  AND LOWER(a.offer_name) LIKE '%whatsapp%')
                 OR (LOWER(a.offer_name) LIKE '%broad%' AND LOWER(a.offer_name) LIKE '%whatsapp%')
                )
                AND a.payment_status IS NOT NULL
                THEN 1
            END
        ),
        COUNT(CASE WHEN a.payment_status IS NOT NULL THEN 1 END),

        CASE WHEN b.vendas_rec_6m > 10 THEN 1 ELSE 0 END,
        CASE WHEN bm.vendas_monet_6m > 10 THEN 1 ELSE 0 END,

        MAX(COALESCE(grt.whatsapp_recuperacao, 0)),
        MAX(COALESCE(grt.whatsapp_monetizacao, 0)),
        MAX(COALESCE(grt.whatsapp_geral, 0)),

        a.origem AS origem

    FROM combined_source a
    LEFT JOIN total_geral tg
        ON a.created_at_date = tg.created_at_date
        AND a.client_country = tg.client_country
        AND a.product_key = tg.product_key
        AND a.origem = tg.origem
    LEFT JOIN vendas_6m_whatsapp b
        ON a.client_country = b.client_country
       AND a.origem = b.origem
    LEFT JOIN vendas_6m_monet_whatsapp bm
        ON a.client_country = bm.client_country
       AND a.origem = bm.origem
    LEFT JOIN instituto_experience.gross_recovery_target grt
      ON grt.yearmonth = DATE_SUB(a.created_at_date, INTERVAL DAYOFMONTH(a.created_at_date) - 1 DAY)

    WHERE LOWER(a.offer_name) LIKE '%whatsapp%'
      AND LOWER(a.offer_name) NOT LIKE '%parceiro%'
      AND UPPER(a.offer_name) NOT LIKE '%DAMAS%'

    GROUP BY
        a.created_at_date,
        a.client_country,
        a.product_key,
        a.origem,
        CASE WHEN b.vendas_rec_6m > 10 THEN 1 ELSE 0 END,
        CASE WHEN bm.vendas_monet_6m > 10 THEN 1 ELSE 0 END;

    -- 3. Troca atômica
    RENAME TABLE
        instituto_experience.dashboard_channels_country_daily       TO instituto_experience.dashboard_channels_country_daily_old,
        instituto_experience.dashboard_channels_country_daily_stage TO instituto_experience.dashboard_channels_country_daily,
        instituto_experience.dashboard_channels_country_daily_old   TO instituto_experience.dashboard_channels_country_daily_stage;

END
```
