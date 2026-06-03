---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-03-08 12:23:56"
alterada_em: "2026-03-08 12:23:56"
execucoes: ""
tags: [rotina, procedure]
---

# refresh_dashboard_janela_recup

## Dependências

- **Lê:** [[cartpanda_physical]], [[unified_lead_events_new]]
- **Escreve:** [[dashboard_janela_recup_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_janela_recup_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_janela_recup_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_janela_recup_stage;

    -- 2. Insere na stage (produção continua intacta)
    INSERT INTO instituto_experience.dashboard_janela_recup_stage

WITH cartpanda_tratado AS (
    SELECT
        cp.*,
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
        ) AS product_name_tratado
    FROM instituto_experience.cartpanda_physical cp
),

base_raw AS (
    SELECT 
        a.order_id,
        a.event_type,
        a.platform,
        a.shop_id,
        a.client_email,
        a.client_phone,
        a.product_name,
        a.order_date,
        a.order_time,

        a.data_insercao_slicktext,
        a.data_insercao_activecampaign,
        a.data_insercao_reportana,

        DATE(a.data_insercao_slicktext) AS data_insercao_slicktext_date,
        TIME(a.data_insercao_slicktext) AS data_insercao_slicktext_time,

        COALESCE(be.created_at_date, bp.created_at_date) AS created_at_date,
        COALESCE(be.created_at_hour, bp.created_at_hour) AS created_at_hour,
        COALESCE(be.product_sku, bp.product_sku) AS product_sku,
        COALESCE(be.offer_name, bp.offer_name) AS offer_name,
        COALESCE(be.payment_status, bp.payment_status) AS payment_status,
        COALESCE(be.total_price, bp.total_price) AS total_price,

        STR_TO_DATE(
            CONCAT(
                COALESCE(be.created_at_date, bp.created_at_date),
                ' ',
                COALESCE(be.created_at_hour, bp.created_at_hour)
            ),
            '%Y-%m-%d %H:%i:%s'
        ) AS created_at_datetime,

        -- CHAVE ÚNICA DE CLIENTE (EMAIL > TELEFONE)
        COALESCE(
            NULLIF(LOWER(a.client_email), ''),
            CONCAT('tel_', a.client_phone)
        ) AS client_key

    FROM instituto_experience.unified_lead_events_new a

    -- JOIN PRINCIPAL (EMAIL)
    LEFT JOIN cartpanda_tratado be
        ON LOWER(a.client_email) = LOWER(be.client_email)
       AND LOWER(a.product_name) = be.product_name_tratado

    -- JOIN FALLBACK (TELEFONE)
    LEFT JOIN cartpanda_tratado bp
        ON be.client_email IS NULL
       AND a.client_phone = bp.client_phone
       AND LOWER(a.product_name) = bp.product_name_tratado

    WHERE a.platform IN ('cartpanda', 'clickbank')
      AND a.event_type IN ('lost_cart','lost_cart_fast','purchase_approved')
      AND a.order_date >= '2026-01-01'
      AND (
            a.data_insercao_slicktext IS NOT NULL
         OR a.data_insercao_activecampaign IS NOT NULL
         OR a.data_insercao_reportana IS NOT NULL
      )
      AND COALESCE(be.created_at_date, bp.created_at_date) IS NOT NULL
),

base_com_canal AS (
    -- SMS
    SELECT
        br.*,
        'sms' AS canal,
        br.data_insercao_slicktext AS data_insercao_canal
    FROM base_raw br
    WHERE (
            (
                br.event_type = 'purchase_approved'
                AND LOWER(br.offer_name) LIKE '%sms%'
                AND LOWER(br.offer_name) LIKE '%mone%'
            )
            OR
            (
                br.event_type IN ('lost_cart','lost_cart_fast')
                AND LOWER(br.offer_name) LIKE '%sms%'
                AND LOWER(br.offer_name) LIKE '%recup%'
            )
    )
      AND br.data_insercao_slicktext IS NOT NULL

    UNION ALL

    -- EMAIL
    SELECT
        br.*,
        'email' AS canal,
        br.data_insercao_activecampaign AS data_insercao_canal
    FROM base_raw br
    WHERE (
            (
                br.event_type = 'purchase_approved'
                AND (LOWER(br.offer_name) LIKE '%e-mail%' OR LOWER(br.offer_name) LIKE '%email%')
                AND LOWER(br.offer_name) LIKE '%mone%'
            )
            OR
            (
                br.event_type IN ('lost_cart','lost_cart_fast')
                AND (LOWER(br.offer_name) LIKE '%e-mail%' OR LOWER(br.offer_name) LIKE '%email%')
                AND LOWER(br.offer_name) LIKE '%recup%'
            )
    )
      AND br.data_insercao_activecampaign IS NOT NULL

    UNION ALL

    -- WHATSAPP (AJUSTE AQUI)
    SELECT
        br.*,
        'whatsapp' AS canal,
        br.data_insercao_reportana AS data_insercao_canal
    FROM base_raw br
    WHERE (
            (
                br.event_type = 'purchase_approved'
                AND LOWER(br.offer_name) LIKE '%whatsapp%'
                AND LOWER(br.offer_name) LIKE '%mone%'
            )
            OR
            (
                br.event_type IN ('lost_cart','lost_cart_fast')
                AND LOWER(br.offer_name) LIKE '%whatsapp%'
                AND LOWER(br.offer_name) LIKE '%recup%'
            )
    )
      AND br.data_insercao_reportana IS NOT NULL
),

calculo AS (
    SELECT
        b.*,
        TIMESTAMPDIFF(
            SECOND,
            b.data_insercao_canal,
            b.created_at_datetime
        ) AS tempo_demora_segundos
    FROM base_com_canal b
)

SELECT *
FROM (
    SELECT
        calculo.*,

        CAST(calculo.tempo_demora_segundos / 60.0    AS DECIMAL(10,2)) AS tempo_demora_minutos,
        CAST(calculo.tempo_demora_segundos / 3600.0  AS DECIMAL(12,4)) AS tempo_demora_horas,
        CAST(calculo.tempo_demora_segundos / 86400.0 AS DECIMAL(14,6)) AS tempo_demora_dias,

        SEC_TO_TIME(
            LEAST(
                GREATEST(calculo.tempo_demora_segundos, -3020399),
                3020399
            )
        ) AS tempo_demora_hhmmss,

        ROW_NUMBER() OVER (
            PARTITION BY
                calculo.canal,
                calculo.client_key,
                calculo.product_name,
                calculo.created_at_date,
                CASE
                    WHEN calculo.event_type = 'purchase_approved' THEN 'purchase'
                    ELSE 'lost'
                END
            ORDER BY calculo.data_insercao_canal
        ) AS ordem_sms

    FROM calculo
) t
WHERE t.ordem_sms = 1;

    -- 3. Troca atômica: usuário nunca vê tabela vazia
    RENAME TABLE
        instituto_experience.dashboard_janela_recup       TO instituto_experience.dashboard_janela_recup_old,
        instituto_experience.dashboard_janela_recup_stage TO instituto_experience.dashboard_janela_recup,
        instituto_experience.dashboard_janela_recup_old   TO instituto_experience.dashboard_janela_recup_stage;

END
```
