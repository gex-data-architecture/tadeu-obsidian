---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-22 15:22:35"
alterada_em: "2026-05-22 15:22:35"
execucoes: 182
tags: [rotina, procedure]
---

# refresh_dashboard_anomalia_diaria

## Dependências

- **Lê:** [[cartpanda_physical]], [[dashboard_gold_clickbank_buygoods]]
- **Escreve:** [[dashboard_anomalia_diaria_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_anomalia_diaria_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 1m52s |
| Tempo máx | 3m59s |
| Tempo total | 5h40m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 59,546,880 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_anomalia_diaria_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_anomalia_diaria_stage;

    -- 2. Insere na stage (produção continua intacta)
    INSERT INTO instituto_experience.dashboard_anomalia_diaria_stage
WITH RECURSIVE

params AS (
    SELECT
        DATE(CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')) AS hoje_br,
        DATE(CONVERT_TZ(UTC_TIMESTAMP(), 'UTC', 'America/Sao_Paulo')) - INTERVAL 22 DAY AS inicio_br
),

datas AS (
    SELECT p.inicio_br AS data
    FROM params p
    UNION ALL
    SELECT d.data + INTERVAL 1 DAY
    FROM datas d
    CROSS JOIN params p
    WHERE d.data < p.hoje_br
),

horas AS (
    SELECT 0 AS hora
    UNION ALL
    SELECT hora + 1
    FROM horas
    WHERE hora < 23
),

/* =======================
   0) FONTE UNIFICADA
======================= */
combined_source AS (
    SELECT
        transaction_id,
        product_name,
        offer_name,
        total_price,
        created_at_date,
        created_at_hour,
        'cartpanda' AS origem
    FROM instituto_experience.cartpanda_physical

    UNION ALL

    SELECT
        transaction_id,
        product_name,
        offer_name,
        total_price,
        created_at_date,
        created_at_hour,
        platform AS origem
    FROM instituto_experience.dashboard_gold_clickbank_buygoods
),

produtos AS (
    SELECT DISTINCT
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
        ) AS product_key
    FROM combined_source cp
    CROSS JOIN params p
    WHERE cp.created_at_date >= p.inicio_br
),

origens AS (
    SELECT DISTINCT origem
    FROM combined_source cp
    CROSS JOIN params p
    WHERE cp.created_at_date >= p.inicio_br
),

/* =======================
   VENDAS FRONT (REPLICADO POR CANAL)
======================= */
vendas_front_sms AS (
    SELECT
        cp.created_at_date AS data,
        HOUR(cp.created_at_hour) AS hora,
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
        COUNT(cp.transaction_id) AS vendas,
        SUM(cp.total_price) AS valor,
        'Front-End' AS tipo_calculo,
        'sms' AS canal,
        cp.origem
    FROM combined_source cp
    CROSS JOIN params p
    WHERE cp.created_at_date >= p.inicio_br
    GROUP BY data, hora, product_key, cp.origem
),

vendas_front_email AS (
    SELECT
        cp.created_at_date AS data,
        HOUR(cp.created_at_hour) AS hora,
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
        COUNT(cp.transaction_id) AS vendas,
        SUM(cp.total_price) AS valor,
        'Front-End' AS tipo_calculo,
        'email' AS canal,
        cp.origem
    FROM combined_source cp
    CROSS JOIN params p
    WHERE cp.created_at_date >= p.inicio_br
    GROUP BY data, hora, product_key, cp.origem
),

vendas_front_whatsapp AS (
    SELECT
        cp.created_at_date AS data,
        HOUR(cp.created_at_hour) AS hora,
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
        COUNT(cp.transaction_id) AS vendas,
        SUM(cp.total_price) AS valor,
        'Front-End' AS tipo_calculo,
        'whatsapp' AS canal,
        cp.origem
    FROM combined_source cp
    CROSS JOIN params p
    WHERE cp.created_at_date >= p.inicio_br
    GROUP BY data, hora, product_key, cp.origem
),

/* =======================
   VENDAS RECUP (REPLICADO POR CANAL)
======================= */
vendas_recup_sms AS (
    SELECT
        cp.created_at_date AS data,
        HOUR(cp.created_at_hour) AS hora,
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
        COUNT(cp.transaction_id) AS vendas,
        SUM(cp.total_price) AS valor,
        'Recuperação' AS tipo_calculo,
        'sms' AS canal,
        cp.origem
    FROM combined_source cp
    CROSS JOIN params p
    WHERE cp.created_at_date >= p.inicio_br
      AND LOWER(cp.offer_name) LIKE '%sms%'
      AND LOWER(cp.offer_name) LIKE '%recup%'
    GROUP BY data, hora, product_key, cp.origem
),

vendas_recup_email AS (
    SELECT
        cp.created_at_date AS data,
        HOUR(cp.created_at_hour) AS hora,
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
        COUNT(cp.transaction_id) AS vendas,
        SUM(cp.total_price) AS valor,
        'Recuperação' AS tipo_calculo,
        'email' AS canal,
        cp.origem
    FROM combined_source cp
    CROSS JOIN params p
    WHERE cp.created_at_date >= p.inicio_br
      AND (LOWER(cp.offer_name) LIKE '%e-mail%' OR LOWER(cp.offer_name) LIKE '%email%')
      AND LOWER(cp.offer_name) LIKE '%recup%'
    GROUP BY data, hora, product_key, cp.origem
),

vendas_recup_whatsapp AS (
    SELECT
        cp.created_at_date AS data,
        HOUR(cp.created_at_hour) AS hora,
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
        COUNT(cp.transaction_id) AS vendas,
        SUM(cp.total_price) AS valor,
        'Recuperação' AS tipo_calculo,
        'whatsapp' AS canal,
        cp.origem
    FROM combined_source cp
    CROSS JOIN params p
    WHERE cp.created_at_date >= p.inicio_br
      AND LOWER(cp.offer_name) LIKE '%whatsapp%'
      AND LOWER(cp.offer_name) LIKE '%recup%'
    GROUP BY data, hora, product_key, cp.origem
),

/* =======================
   VENDAS MONETIZAÇÃO (REPLICADO POR CANAL)
======================= */
vendas_monetizacao_sms AS (
    SELECT
        cp.created_at_date AS data,
        HOUR(cp.created_at_hour) AS hora,
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
        COUNT(cp.transaction_id) AS vendas,
        SUM(cp.total_price) AS valor,
        'Monetização' AS tipo_calculo,
        'sms' AS canal,
        cp.origem
    FROM combined_source cp
    CROSS JOIN params p
    WHERE cp.created_at_date >= p.inicio_br
      AND LOWER(cp.offer_name) LIKE '%sms%'
      AND LOWER(cp.offer_name) LIKE '%mone%'
    GROUP BY data, hora, product_key, cp.origem
),

vendas_monetizacao_email AS (
    SELECT
        cp.created_at_date AS data,
        HOUR(cp.created_at_hour) AS hora,
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
        COUNT(cp.transaction_id) AS vendas,
        SUM(cp.total_price) AS valor,
        'Monetização' AS tipo_calculo,
        'email' AS canal,
        cp.origem
    FROM combined_source cp
    CROSS JOIN params p
    WHERE cp.created_at_date >= p.inicio_br
      AND (LOWER(cp.offer_name) LIKE '%e-mail%' OR LOWER(cp.offer_name) LIKE '%email%')
      AND LOWER(cp.offer_name) LIKE '%mone%'
    GROUP BY data, hora, product_key, cp.origem
),

vendas_monetizacao_whatsapp AS (
    SELECT
        cp.created_at_date AS data,
        HOUR(cp.created_at_hour) AS hora,
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
        COUNT(cp.transaction_id) AS vendas,
        SUM(cp.total_price) AS valor,
        'Monetização' AS tipo_calculo,
        'whatsapp' AS canal,
        cp.origem
    FROM combined_source cp
    CROSS JOIN params p
    WHERE cp.created_at_date >= p.inicio_br
      AND LOWER(cp.offer_name) LIKE '%whatsapp%'
      AND LOWER(cp.offer_name) LIKE '%mone%'
    GROUP BY data, hora, product_key, cp.origem
),

/* =======================
   UNION - VENDAS REAIS
======================= */
vendas_reais AS (
    SELECT * FROM vendas_front_sms
    UNION ALL
    SELECT * FROM vendas_front_email
    UNION ALL
    SELECT * FROM vendas_front_whatsapp

    UNION ALL
    SELECT * FROM vendas_recup_sms
    UNION ALL
    SELECT * FROM vendas_recup_email
    UNION ALL
    SELECT * FROM vendas_recup_whatsapp

    UNION ALL
    SELECT * FROM vendas_monetizacao_sms
    UNION ALL
    SELECT * FROM vendas_monetizacao_email
    UNION ALL
    SELECT * FROM vendas_monetizacao_whatsapp
),

/* =======================
   GRADE (AGORA COM CANAL E ORIGEM)
======================= */
grade AS (
    SELECT
        d.data,
        h.hora,
        p.product_key,
        t.tipo_calculo,
        c.canal,
        o.origem
    FROM datas d
    CROSS JOIN horas h
    CROSS JOIN produtos p
    CROSS JOIN (
        SELECT 'Front-End' AS tipo_calculo
        UNION ALL
        SELECT 'Recuperação'
        UNION ALL
        SELECT 'Monetização'
    ) t
    CROSS JOIN (
        SELECT 'sms' AS canal
        UNION ALL SELECT 'email'
        UNION ALL SELECT 'whatsapp'
    ) c
    CROSS JOIN origens o
),

base_preenchida AS (
    SELECT
        g.data,
        g.hora,
        g.product_key,
        g.tipo_calculo,
        g.canal,
        g.origem,
        COALESCE(v.vendas, 0) AS vendas_hoje,
        COALESCE(v.valor, 0) AS valor_hoje
    FROM grade g
    LEFT JOIN vendas_reais v
        ON v.data = g.data
       AND v.hora = g.hora
       AND v.product_key = g.product_key
       AND v.tipo_calculo = g.tipo_calculo
       AND v.canal = g.canal
       AND v.origem = g.origem
),

calc AS (
    SELECT
        data,
        hora,
        product_key,
        tipo_calculo,
        canal,
        origem,

        vendas_hoje,
        valor_hoje,

        LAG(vendas_hoje, 1) OVER (
            PARTITION BY product_key, hora, tipo_calculo, canal, origem
            ORDER BY data
        ) AS vendas_ontem,

        LAG(valor_hoje, 1) OVER (
            PARTITION BY product_key, hora, tipo_calculo, canal, origem
            ORDER BY data
        ) AS valor_ontem,

        AVG(vendas_hoje) OVER (
            PARTITION BY product_key, hora, tipo_calculo, canal, origem
            ORDER BY data
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS media_7d_qtd,

        MIN(vendas_hoje) OVER (
            PARTITION BY product_key, hora, tipo_calculo, canal, origem
            ORDER BY data
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS min_7d_qtd,

        MAX(vendas_hoje) OVER (
            PARTITION BY product_key, hora, tipo_calculo, canal, origem
            ORDER BY data
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS max_7d_qtd,

        AVG(vendas_hoje) OVER (
            PARTITION BY product_key, hora, tipo_calculo, canal, origem
            ORDER BY data
            ROWS BETWEEN 14 PRECEDING AND 8 PRECEDING
        ) AS media_8a14_qtd,

        AVG(valor_hoje) OVER (
            PARTITION BY product_key, hora, tipo_calculo, canal, origem
            ORDER BY data
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS media_7d_valor,

        MIN(valor_hoje) OVER (
            PARTITION BY product_key, hora, tipo_calculo, canal, origem
            ORDER BY data
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS min_7d_valor,

        MAX(valor_hoje) OVER (
            PARTITION BY product_key, hora, tipo_calculo, canal, origem
            ORDER BY data
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS max_7d_valor,

        AVG(valor_hoje) OVER (
            PARTITION BY product_key, hora, tipo_calculo, canal, origem
            ORDER BY data
            ROWS BETWEEN 14 PRECEDING AND 8 PRECEDING
        ) AS media_8a14_valor
    FROM base_preenchida
)

SELECT
    c.canal,
    c.data,
    DATEDIFF(p.hoje_br, c.data) + 1 AS indice,
    c.hora AS Hora,
    c.product_key AS Product,
    c.tipo_calculo AS Front_Recup,
    c.origem AS origem,

    c.vendas_hoje AS Sales,
    c.vendas_ontem AS Sales_d1,
    c.media_7d_qtd AS AVG_Sales_d7,
    c.media_8a14_qtd AS AVG_Sales_d8_d14,
    c.min_7d_qtd AS MIN_Sales_d7,
    c.max_7d_qtd AS MAX_Sales_d7,

    c.vendas_hoje - c.media_7d_qtd AS Delta_Sales_AVG_d7,
    ROUND((c.vendas_hoje - c.media_7d_qtd) / NULLIF(c.media_7d_qtd, 0), 4) AS Pct_Delta_Sales_AVG_d7,

    c.valor_hoje AS Revenue,
    c.valor_ontem AS Revenue_d1,
    c.media_7d_valor AS AVG_Revenue_d7,
    c.media_8a14_valor AS AVG_Revenue_d8_d14,
    c.min_7d_valor AS MIN_Revenue_d7,
    c.max_7d_valor AS MAX_Revenue_d7,

    c.valor_hoje - c.media_7d_valor AS Delta_Revenue_AVG_d7,
    ROUND((c.valor_hoje - c.media_7d_valor) / NULLIF(c.media_7d_valor, 0), 4) AS Pct_Delta_Revenue_AVG_d7,

    CASE
        WHEN c.media_7d_qtd IS NULL THEN 'Sem histórico'
        WHEN c.vendas_hoje < c.min_7d_qtd THEN 'Crítico'
        WHEN c.vendas_hoje > c.max_7d_qtd THEN 'Atenção'
        ELSE 'OK'
    END AS Status

FROM calc c
CROSS JOIN params p
WHERE c.data >= p.hoje_br - INTERVAL 15 DAY
ORDER BY indice, canal, origem, Front_Recup, Product, Hora;
    -- 3. Troca atômica: usuário nunca vê tabela vazia
    RENAME TABLE
        instituto_experience.dashboard_anomalia_diaria       TO instituto_experience.dashboard_anomalia_diaria_old,
        instituto_experience.dashboard_anomalia_diaria_stage TO instituto_experience.dashboard_anomalia_diaria,
        instituto_experience.dashboard_anomalia_diaria_old   TO instituto_experience.dashboard_anomalia_diaria_stage;

END
```
