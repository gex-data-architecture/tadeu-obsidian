---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-05 11:20:01"
alterada_em: "2026-05-05 11:20:01"
execucoes: 179
tags: [rotina, procedure]
---

# refresh_dashboard_reembolso

## Dependências

- **Lê:** [[cb_tickets]], [[clickbank_physical_new_aws]], [[cw_refund_classifier]]
- **Escreve:** [[dashboard_reembolso_stage]]
- **Cria:** `tmp_refund_classifier`, `tmp_ticket_agent`, `tmp_ticket_dedup`
- **Trunca:** [[dashboard_reembolso_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 179 |
| Tempo médio | 1m40s |
| Tempo máx | 2m23s |
| Tempo total | 4h59m |
| Erros | 2 |
| Warnings | 537 |
| Linhas afetadas (total) | 75,421,798 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_reembolso_stage;
        RESIGNAL;
    END;

    -- 1. Tabelas temporárias auxiliares

    DROP TEMPORARY TABLE IF EXISTS tmp_ticket_dedup;
    CREATE TEMPORARY TABLE tmp_ticket_dedup AS
    SELECT t.*
    FROM instituto_experience.cb_tickets t
    INNER JOIN (
        SELECT receipt, MAX(opened_date) AS max_opened_date, MAX(cb_ticket_id) AS max_ticket_id
        FROM instituto_experience.cb_tickets
        GROUP BY receipt
    ) latest
        ON t.receipt       = latest.receipt
       AND t.opened_date   = latest.max_opened_date
       AND t.cb_ticket_id  = latest.max_ticket_id;

    DROP TEMPORARY TABLE IF EXISTS tmp_ticket_agent;
    CREATE TEMPORARY TABLE tmp_ticket_agent AS
    SELECT DISTINCT receipt
    FROM instituto_experience.cb_tickets
    WHERE note LIKE '%Agent:%';

    DROP TEMPORARY TABLE IF EXISTS tmp_refund_classifier;
    CREATE TEMPORARY TABLE tmp_refund_classifier AS
    SELECT cb_ticket_id, refund_reason, refund_reason_detail, sentiment
    FROM (
        SELECT
            cb_ticket_id,
            refund_reason,
            refund_reason_detail,
            sentiment,
            ROW_NUMBER() OVER (PARTITION BY cb_ticket_id ORDER BY cb_ticket_id) AS rn
        FROM instituto_experience.cw_refund_classifier
    ) x
    WHERE rn = 1;

    -- 2. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_reembolso_stage;

    -- 3. Insere na stage
    INSERT INTO instituto_experience.dashboard_reembolso_stage
    SELECT
        *,
        COALESCE(NULLIF(TRIM(refund_reason), ''), categoria) AS categoria_final,
        CASE WHEN refund_reason IS NOT NULL THEN 'Sim' ELSE 'Não' END AS is_ia
    FROM (
        WITH nome_limpo AS (
            SELECT
                c.*,
                REGEXP_REPLACE(
                    TRIM(
                        CASE
                            WHEN c.product_name LIKE '%-%'
                                THEN TRIM(SUBSTRING_INDEX(c.product_name, '-', 1))
                            WHEN REGEXP_LIKE(c.product_name, '[0-9]')
                                THEN TRIM(REGEXP_REPLACE(c.product_name, '^[0-9s]+', ''))
                            ELSE c.product_name
                        END
                    ),
                    '[^a-zA-Z0-9]', ''
                ) AS product_name_clean
            FROM instituto_experience.clickbank_physical_new_aws c
            WHERE c.created_at_date >= '2026-02-01'
        )
        SELECT
            n.transaction_id,
            n.created_at_date,
            n.date_refunded,
            n.payment_status,
            COALESCE(
                NULLIF(CONCAT(UPPER(LEFT(n.product_name_clean, 1)), LOWER(SUBSTRING(n.product_name_clean, 2))), ''),
                'Não identificado'
            ) AS product_name,
            n.product_sku,
            n.sales_type,
            CASE
                WHEN n.sales_type IN ('Order Bump', 'Venda de Funil') THEN 'Venda de Funil'
                ELSE n.sales_type
            END AS sales_type_unificado,
            n.affiliate_name,
            n.is_house_traffic,
            n.utm_source,
            n.utm_medium,
            n.utm_campaign,
            n.utm_content,
            n.utm_term,
            n.total_price_usd,
            n.total_refund_usd,
            DATEDIFF(n.date_refunded, n.created_at_date)              AS dias_ate_reembolso,
            CASE
                WHEN DATEDIFF(n.date_refunded, n.created_at_date) = 0               THEN '1 | 0-24h'
                WHEN DATEDIFF(n.date_refunded, n.created_at_date) BETWEEN 1 AND 3   THEN '2 | 1-3 dias'
                WHEN DATEDIFF(n.date_refunded, n.created_at_date) BETWEEN 3 AND 7   THEN '3 | 3-7 dias'
                WHEN DATEDIFF(n.date_refunded, n.created_at_date) BETWEEN 7 AND 14  THEN '4 | 7-14 dias'
                WHEN DATEDIFF(n.date_refunded, n.created_at_date) BETWEEN 14 AND 30 THEN '5 | 14-30 dias'
                WHEN DATEDIFF(n.date_refunded, n.created_at_date) BETWEEN 30 AND 60 THEN '6 | 30-60 dias'
                WHEN DATEDIFF(n.date_refunded, n.created_at_date) BETWEEN 60 AND 90 THEN '7 | 60-90 dias'
                WHEN DATEDIFF(n.date_refunded, n.created_at_date) > 90              THEN '8 | +90 dias'
                ELSE NULL
            END                                                       AS faixa_reembolso,
            CASE WHEN n.payment_status = 'approved'
                 THEN 1 ELSE 0 END                                    AS is_venda,
            CASE WHEN n.payment_status IN ('refunded','refunded_partial')
                 THEN 1 ELSE 0 END                                    AS is_refund,
            CASE WHEN n.payment_status = 'chargeback'
                 THEN 1 ELSE 0 END                                    AS is_chargeback,
            CASE WHEN n.payment_status IN ('refunded','refunded_partial','chargeback')
                 THEN 1 ELSE 0 END                                    AS is_devolvido,
            CASE WHEN n.payment_status IN ('refunded','refunded_partial')
                      AND DATEDIFF(n.date_refunded, n.created_at_date) > 60
                 THEN 1 ELSE 0 END                                    AS is_fora_garantia,
            CASE WHEN ta.receipt IS NOT NULL
                 THEN 1 ELSE 0 END                                    AS absorvido_gex,
            CASE WHEN n.payment_status = 'approved'
                 THEN n.total_price_usd ELSE 0 END                    AS valor_venda_usd,
            CASE WHEN n.payment_status IN ('refunded','refunded_partial')
                 THEN n.total_refund_usd ELSE 0 END                   AS valor_refund_usd,
            CASE WHEN n.payment_status = 'chargeback'
                 THEN n.total_refund_usd ELSE 0 END                   AS valor_chargeback_usd,
            CASE WHEN n.payment_status IN ('refunded','refunded_partial')
                      AND ta.receipt IS NOT NULL
                 THEN n.total_refund_usd ELSE 0 END                   AS valor_refund_absorvido_usd,
            CASE WHEN n.payment_status IN ('refunded','refunded_partial')
                      AND ta.receipt IS NULL
                 THEN n.total_refund_usd ELSE 0 END                   AS valor_refund_sem_atendimento_usd,
            t.cb_ticket_id,
            t.receipt,
            t.status                                                  AS ticket_status,
            t.type                                                    AS ticket_type,
            t.expiration_date,
            COALESCE(t.cw_conversation_id_email, t.cw_conversation_id_sms) AS cw_conversation_id,
            CASE
                WHEN COALESCE(t.cw_conversation_id_email, t.cw_conversation_id_sms) IS NOT NULL
                THEN CONCAT(
                    'https://chat.institutoexperience.com/app/accounts/1/conversations/',
                    COALESCE(t.cw_conversation_id_email, t.cw_conversation_id_sms)
                )
                ELSE NULL
            END                                                       AS url_conversa,
            t.cw_contact_id,
            t.backoffice_agent_name                                   AS assigned_agent,
            t.current_priority,
            t.sale_amount                                             AS refund_amount_actual,
            t.refund_negotiated,
            t.product_name                                            AS ticket_product_name,
            t.product_item_no,
            t.opened_date,
            t.closed_date,
            COALESCE(NULLIF(TRIM(t.description), ''), 'Sem descrição') AS description,
            t.note,
            CASE
                WHEN REGEXP_LIKE(LOWER(t.note), 'accepted.*discount|discount.*avoid|25%.*refund|20%.*discount|partial refund.*agreed|agreed.*partial|please process the refund|process.*refund.*agreed|agent.*aline|agent.*raíssa|agent.*mesel|agent:.*gabriela|agent:.*flavia|agent:.*lucas|agent:.*ariane|agent:.*susana|agent:.*beatriz|agent:.*mariana|agent:.*igor|agent:.*daniel|agent:.*julia|please process the refund.*amount|refund.*as agreed with the client|refund.*as agreed with the customer|refund.*as per the.*return|customer returned|customer requests cancellation|refused delivery.*refund') THEN 'Solicitação de cancelamento'
                WHEN REGEXP_LIKE(LOWER(t.note), 'allergic|adverse.*event|\bAER\b|reaction.*product|side.*effect|heart.*race|palpitat|nausea.*product|vomit.*product|diarrhea|hives|rash.*product|stomach.*ache|cannot.*take.*doctor|advised.*not.*use|advised.*not.*take|doctor.*not.*recommend|cardiologist|nephrologist|oncologist|endocrinologist|medical.*condition.*cannot|chronic.*kidney|contraindicated|chemotherapy.*cannot|bariatric.*surgery.*cannot|doctor.*not.*let|physician.*not|doctor.*said.*no|doctor.*recommended.*not|md.*not.*let|my.*doctor|checked with my doctor|primary care|prescription|health issue|health concern|doctor.*told|doctor.*said|physician|unapproved by doctor|doctor disapproved|my dr said i can.?t do this|my drs said i can.?t use|cannot use with current medication|blood thinners|heart medications|wegovy|insulin pump|medical reason|medical issues|health professional|neurologist.*advised|advised.*neurologist|spoke to.*neurologist|spoke to.*cardiologist') THEN 'Restrição médica'
                WHEN REGEXP_LIKE(LOWER(t.note), 'scam|fake|fraud|not authorize|compromised|ai-generated|kelly clarkson|dr oz|lied|endorse|did not authorize|unauthorized|fraudulent|card.*compromised|threatened.*chargeback|threaten|file.*chargeback|false advertising|misinformation|bait.*switch|not legit|don.?t trust|not trusting this site|dishonest representation|not supported by dr\. oz|not promoted by dr\. oz|consumer complaints') THEN 'Fraude ou golpe'
                WHEN REGEXP_LIKE(LOWER(t.note), 'duplicate|already have|already got|already purchased|double|duplication|two order|both order|ordered twice|upgrade|upgraded|1st order|charged for|instead of|switched|accident|mistake|mistakenly|by mistake|did not finish|not intend|clicked|order error|ordered in error|ordered too many|only wanted the 12 bottles|only wanted 12 bottles|not the amount i ordered|replace the 6 quantity|remove the 6 bottle order|didn.?t mean to buy another 12|did not mean to order this product|billed for 2 orders|too many uncertainties and 2 orders placed|just wanted 2 bottles|ordered 12 bottles instead|wrong product.*cancel|cancel.*wrong product|not what i ordered|this is not what i ordered') THEN 'Compra duplicada'
                WHEN REGEXP_LIKE(LOWER(t.note), 'financial difficult|financial reason|afford|budget|priorit.*cost|wife.*medication|social security|can.*afford|too costly|too expensive|cheaper|less price|lower price|too much|price|insufficient funds|limited funds|no money|need the money for rent|fixed income|money at this time|more expensive than advertised|misrepresentation of costs|too much money|bills to pay') THEN 'Reclamação de preço'
                WHEN REGEXP_LIKE(LOWER(t.note), 'subscription.*cancel|cancel.*subscription|recurring.*cancel|changed my mind|change.*mind|decided|don.*want|do not want|not for me|no longer|not need|don.*need|more research|not ready|not interested|cancel|want.*refund|want a refund|please refund|want to cancel|decided against|not comfortable|not within my budget|i am male|wanted to do additional research before buying product|i do not wish to purchase this item|i did not want this product|not what i wanted|moment of insanity|wasn.?t thinking|stop order|refund this purchase|slow shipping.*changed mind|taking.*long.*cancel|don.?t want.*taking.*long|cancel.*taking too long') THEN 'Solicitação de cancelamento'
                WHEN REGEXP_LIKE(LOWER(t.note), 'dissatisfaction|dissatisfied|not satisfied|doesn.?t work|didn.?t work|did not work|don.?t think it will work|researched that it doesn.?t work|not happy|horrible reviews|not what you advertised|reviews.*aren.?t.*claimed|reviews.*don.?t back|claims are inconsistent') THEN 'Sem resultados'
                WHEN REGEXP_LIKE(LOWER(t.note), 'return tracking|tracking.*return|has provided.*return|postmarked|return.*address|send.*back.*address|please return|must be returned|return.*bottle') THEN 'Problema na entrega'
                WHEN REGEXP_LIKE(LOWER(t.note), 'damaged|missing item|broken|arrived.*damage|damage.*arriv|missing.*product|only got.*bottle|missing part|wrong product.*received|received.*wrong.*product|got.*wrong.*product|no packing slip') THEN 'Problema na entrega'
                WHEN REGEXP_LIKE(LOWER(t.note), 'not.*received|haven.*received|never received|where is my order|not here yet|not arrived|hasn.*arrive|not yet.*received|supposed to be here|shipment has not happened|awaiting fulfillment|shipping verification|delay in delivery|waiting.*10 days|waiting.*30 days|still hasn.*shipped|hasn.*even shipped|not even shipped|never got.*order|non-delivery') THEN 'Problema na entrega'
                WHEN REGEXP_LIKE(t.description, 'Compra nao autorizada|Compra fraudulenta|nao reconhecida na fatura') THEN 'Fraude ou golpe'
                WHEN REGEXP_LIKE(t.description, 'Compra duplicada|ja realizada') THEN 'Compra duplicada'
                WHEN REGEXP_LIKE(t.description, 'Insatisfeito|Produto nao funciona|Produto errado') THEN 'Sem resultados'
                WHEN REGEXP_LIKE(t.description, 'Produto nao recebido|Produto fisico devolvido') THEN 'Problema na entrega'
                WHEN REGEXP_LIKE(t.description, 'Nao pode continuar pagando|Nao sabia que havia cobranca|Nao ve mais valor') THEN 'Reclamação de preço'
                WHEN REGEXP_LIKE(t.description, 'Nao conseguiu suporte') THEN 'Sem resultados'
                ELSE 'Motivo não identificado'
            END                                                       AS categoria,
            rc.refund_reason,
            rc.refund_reason_detail,
            rc.sentiment
        FROM nome_limpo n
        LEFT JOIN tmp_ticket_dedup t
            ON n.transaction_id = t.receipt COLLATE utf8mb4_unicode_ci
        LEFT JOIN tmp_ticket_agent ta
            ON n.transaction_id = ta.receipt COLLATE utf8mb4_unicode_ci
        LEFT JOIN tmp_refund_classifier rc
            ON t.cb_ticket_id = rc.cb_ticket_id
    ) sub;

    -- 4. Troca atômica
    RENAME TABLE
        instituto_experience.dashboard_reembolso       TO instituto_experience.dashboard_reembolso_old,
        instituto_experience.dashboard_reembolso_stage TO instituto_experience.dashboard_reembolso,
        instituto_experience.dashboard_reembolso_old   TO instituto_experience.dashboard_reembolso_stage;

    -- 5. Limpa temporárias
    DROP TEMPORARY TABLE IF EXISTS tmp_ticket_dedup;
    DROP TEMPORARY TABLE IF EXISTS tmp_ticket_agent;
    DROP TEMPORARY TABLE IF EXISTS tmp_refund_classifier;

END
```
