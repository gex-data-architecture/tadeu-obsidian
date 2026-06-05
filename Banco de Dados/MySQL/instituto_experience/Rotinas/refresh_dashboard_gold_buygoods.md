---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-06-01 22:04:03"
alterada_em: "2026-06-01 22:04:03"
execucoes: 40
tags: [rotina, procedure]
---

# refresh_dashboard_gold_buygoods

## Dependências

- **Lê:** [[tb_gex_buygoods_unified]]
- **Escreve:** [[dashboard_gold_buygoods_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_gold_buygoods_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 40 |
| Tempo médio | 8m45s |
| Tempo máx | 11m38s |
| Tempo total | 5h49m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 8,822,011 |

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
        cb.*,
        TIMESTAMP(CONCAT(cb.created_at_date, ' ', cb.created_at_hour)) AS created_at_ts,
        UPPER(COALESCE(cb.product_codename, '')) AS _codename_upper
    FROM instituto_experience.tb_gex_buygoods_unified cb
    WHERE (cb.created_at_date >= '2026-01-01' OR cb.created_at_date IS NULL)
),
ordenado AS (
    SELECT *,
        LAG(created_at_ts) OVER (
            PARTITION BY client_email, account_id
            ORDER BY created_at_ts, transaction_id
        ) AS prev_ts
    FROM base
),
flag_grupo AS (
    SELECT *,
        CASE
            WHEN prev_ts IS NULL THEN 1
            WHEN TIMESTAMPDIFF(MINUTE, prev_ts, created_at_ts) > 240 THEN 1
            ELSE 0
        END AS new_group
    FROM ordenado
),
grupo_id AS (
    SELECT *,
        SUM(new_group) OVER (
            PARTITION BY client_email, account_id
            ORDER BY created_at_ts, transaction_id
            ROWS UNBOUNDED PRECEDING
        ) AS purchase_group_id_final
    FROM flag_grupo
),
classificado AS (
    SELECT *,
        CASE
            -- 1) PRIMEIRA REGRA: offer_name (canonico, sera a fonte definitiva)
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%upsell 1%'   THEN 'upsell1'
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%upsell 2%'   THEN 'upsell2'
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%upsell 3%'   THEN 'upsell3'
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%downsell 1%' THEN 'downsell1'
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%downsell 2%' THEN 'downsell2'
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%downsell 3%' THEN 'downsell3'
            WHEN LOWER(sales_type) = 'order bump'                                                THEN 'order_bump'

            -- 2) SEGUNDA REGRA: fallback via product_codename
            WHEN _codename_upper REGEXP '(^|[_-])UP1([_-]|$)' OR _codename_upper REGEXP 'UP1[0-9]' THEN 'upsell1'
            WHEN _codename_upper REGEXP '(^|[_-])UP2([_-]|$)' OR _codename_upper REGEXP 'UP2[0-9]' THEN 'upsell2'
            WHEN _codename_upper REGEXP '(^|[_-])UP3([_-]|$)' OR _codename_upper REGEXP 'UP3[0-9]' THEN 'upsell3'
            WHEN _codename_upper REGEXP '(^|[_-])DW1([_-]|$)' OR _codename_upper REGEXP 'DW1[0-9]' THEN 'downsell1'
            WHEN _codename_upper REGEXP '(^|[_-])DW2([_-]|$)' OR _codename_upper REGEXP 'DW2[0-9]' THEN 'downsell2'
            WHEN _codename_upper REGEXP '(^|[_-])DW3([_-]|$)' OR _codename_upper REGEXP 'DW3[0-9]' THEN 'downsell3'
            WHEN _codename_upper REGEXP '(^|[_-])PP([_-]|$)'  OR _codename_upper REGEXP 'PP[0-9]'  THEN 'main'

            -- 3) TERCEIRA REGRA: fallback final pelo sales_type
            WHEN TRIM(LOWER(sales_type)) LIKE 'produto principal%'                                  THEN 'main'
            WHEN LOWER(sales_type) = 'venda de funil' AND (offer_name IS NULL OR TRIM(offer_name) = '') THEN 'funil_sem_offer'
            WHEN LOWER(sales_type) = 'venda de funil'                                                THEN 'funil_sem_offer'
            ELSE 'other'
        END AS funnel_type
    FROM grupo_id
),
main_por_grupo AS (
    SELECT
        client_email,
        account_id,
        purchase_group_id_final,
        MAX(CASE WHEN funnel_type = 'main' THEN product_name END) AS main_product_name,
        MAX(CASE WHEN funnel_type = 'main' THEN offer_name   END) AS main_offer_name,
        MAX(CASE WHEN funnel_type = 'main' THEN product_sku  END) AS main_product_sku,
        MIN(created_at_ts)                                        AS grupo_ts
    FROM classificado
    GROUP BY client_email, account_id, purchase_group_id_final
)
SELECT
    MIN(c.transaction_id)                                                       AS transaction_id,                  -- 1
    CASE
        WHEN COUNT(DISTINCT c.payment_status) = 1
            THEN MAX(c.payment_status)
        WHEN MAX(CASE WHEN c.payment_status = 'chargeback' THEN 1 ELSE 0 END) = 1
            THEN 'chargeback'
        ELSE 'refunded_partial'
    END                                                                         AS payment_status,                  -- 2
    MAX(c.client_name)                                                          AS client_name,                     -- 3
    c.client_email                                                              AS client_email,                    -- 4
    MAX(c.client_phone)                                                         AS client_phone,                    -- 5
    MAX(c.client_zip)                                                           AS client_zip,                      -- 6
    CASE MAX(c.client_country)
        WHEN 'AD' THEN 'Andorra'              WHEN 'AE' THEN 'United Arab Emirates'
        WHEN 'AF' THEN 'Afghanistan'          WHEN 'AG' THEN 'Antigua and Barbuda'
        WHEN 'AL' THEN 'Albania'              WHEN 'AM' THEN 'Armenia'
        WHEN 'AO' THEN 'Angola'               WHEN 'AR' THEN 'Argentina'
        WHEN 'AT' THEN 'Austria'              WHEN 'AU' THEN 'Australia'
        WHEN 'AZ' THEN 'Azerbaijan'           WHEN 'BA' THEN 'Bosnia and Herzegovina'
        WHEN 'BB' THEN 'Barbados'             WHEN 'BD' THEN 'Bangladesh'
        WHEN 'BE' THEN 'Belgium'              WHEN 'BF' THEN 'Burkina Faso'
        WHEN 'BG' THEN 'Bulgaria'             WHEN 'BH' THEN 'Bahrain'
        WHEN 'BI' THEN 'Burundi'              WHEN 'BJ' THEN 'Benin'
        WHEN 'BN' THEN 'Brunei'               WHEN 'BO' THEN 'Bolivia'
        WHEN 'BR' THEN 'Brazil'               WHEN 'BS' THEN 'Bahamas'
        WHEN 'BT' THEN 'Bhutan'               WHEN 'BW' THEN 'Botswana'
        WHEN 'BY' THEN 'Belarus'              WHEN 'BZ' THEN 'Belize'
        WHEN 'CA' THEN 'Canada'               WHEN 'CD' THEN 'Democratic Republic of the Congo'
        WHEN 'CF' THEN 'Central African Republic' WHEN 'CG' THEN 'Republic of the Congo'
        WHEN 'CH' THEN 'Switzerland'          WHEN 'CI' THEN 'Ivory Coast'
        WHEN 'CL' THEN 'Chile'                WHEN 'CM' THEN 'Cameroon'
        WHEN 'CN' THEN 'China'                WHEN 'CO' THEN 'Colombia'
        WHEN 'CR' THEN 'Costa Rica'           WHEN 'CU' THEN 'Cuba'
        WHEN 'CV' THEN 'Cape Verde'           WHEN 'CY' THEN 'Cyprus'
        WHEN 'CZ' THEN 'Czech Republic'       WHEN 'DE' THEN 'Germany'
        WHEN 'DJ' THEN 'Djibouti'             WHEN 'DK' THEN 'Denmark'
        WHEN 'DM' THEN 'Dominica'             WHEN 'DO' THEN 'Dominican Republic'
        WHEN 'DZ' THEN 'Algeria'              WHEN 'EC' THEN 'Ecuador'
        WHEN 'EE' THEN 'Estonia'              WHEN 'EG' THEN 'Egypt'
        WHEN 'ER' THEN 'Eritrea'              WHEN 'ES' THEN 'Spain'
        WHEN 'ET' THEN 'Ethiopia'             WHEN 'FI' THEN 'Finland'
        WHEN 'FJ' THEN 'Fiji'                 WHEN 'FR' THEN 'France'
        WHEN 'GA' THEN 'Gabon'                WHEN 'GB' THEN 'United Kingdom'
        WHEN 'GD' THEN 'Grenada'              WHEN 'GE' THEN 'Georgia'
        WHEN 'GH' THEN 'Ghana'                WHEN 'GM' THEN 'Gambia'
        WHEN 'GN' THEN 'Guinea'               WHEN 'GQ' THEN 'Equatorial Guinea'
        WHEN 'GR' THEN 'Greece'               WHEN 'GT' THEN 'Guatemala'
        WHEN 'GW' THEN 'Guinea-Bissau'        WHEN 'GY' THEN 'Guyana'
        WHEN 'HN' THEN 'Honduras'             WHEN 'HR' THEN 'Croatia'
        WHEN 'HT' THEN 'Haiti'                WHEN 'HU' THEN 'Hungary'
        WHEN 'ID' THEN 'Indonesia'            WHEN 'IE' THEN 'Ireland'
        WHEN 'IL' THEN 'Israel'               WHEN 'IN' THEN 'India'
        WHEN 'IQ' THEN 'Iraq'                 WHEN 'IR' THEN 'Iran'
        WHEN 'IS' THEN 'Iceland'              WHEN 'IT' THEN 'Italy'
        WHEN 'JM' THEN 'Jamaica'              WHEN 'JO' THEN 'Jordan'
        WHEN 'JP' THEN 'Japan'                WHEN 'KE' THEN 'Kenya'
        WHEN 'KG' THEN 'Kyrgyzstan'           WHEN 'KH' THEN 'Cambodia'
        WHEN 'KI' THEN 'Kiribati'             WHEN 'KM' THEN 'Comoros'
        WHEN 'KN' THEN 'Saint Kitts and Nevis' WHEN 'KP' THEN 'North Korea'
        WHEN 'KR' THEN 'South Korea'          WHEN 'KW' THEN 'Kuwait'
        WHEN 'KZ' THEN 'Kazakhstan'           WHEN 'LA' THEN 'Laos'
        WHEN 'LB' THEN 'Lebanon'              WHEN 'LC' THEN 'Saint Lucia'
        WHEN 'LI' THEN 'Liechtenstein'        WHEN 'LK' THEN 'Sri Lanka'
        WHEN 'LR' THEN 'Liberia'              WHEN 'LS' THEN 'Lesotho'
        WHEN 'LT' THEN 'Lithuania'            WHEN 'LU' THEN 'Luxembourg'
        WHEN 'LV' THEN 'Latvia'               WHEN 'LY' THEN 'Libya'
        WHEN 'MA' THEN 'Morocco'              WHEN 'MC' THEN 'Monaco'
        WHEN 'MD' THEN 'Moldova'              WHEN 'ME' THEN 'Montenegro'
        WHEN 'MG' THEN 'Madagascar'           WHEN 'MH' THEN 'Marshall Islands'
        WHEN 'MK' THEN 'North Macedonia'      WHEN 'ML' THEN 'Mali'
        WHEN 'MM' THEN 'Myanmar'              WHEN 'MN' THEN 'Mongolia'
        WHEN 'MR' THEN 'Mauritania'           WHEN 'MT' THEN 'Malta'
        WHEN 'MU' THEN 'Mauritius'            WHEN 'MV' THEN 'Maldives'
        WHEN 'MW' THEN 'Malawi'               WHEN 'MX' THEN 'Mexico'
        WHEN 'MY' THEN 'Malaysia'             WHEN 'MZ' THEN 'Mozambique'
        WHEN 'NA' THEN 'Namibia'              WHEN 'NE' THEN 'Niger'
        WHEN 'NG' THEN 'Nigeria'              WHEN 'NI' THEN 'Nicaragua'
        WHEN 'NL' THEN 'Netherlands'          WHEN 'NO' THEN 'Norway'
        WHEN 'NP' THEN 'Nepal'                WHEN 'NR' THEN 'Nauru'
        WHEN 'NZ' THEN 'New Zealand'          WHEN 'OM' THEN 'Oman'
        WHEN 'PA' THEN 'Panama'               WHEN 'PE' THEN 'Peru'
        WHEN 'PG' THEN 'Papua New Guinea'     WHEN 'PH' THEN 'Philippines'
        WHEN 'PK' THEN 'Pakistan'             WHEN 'PL' THEN 'Poland'
        WHEN 'PT' THEN 'Portugal'             WHEN 'PW' THEN 'Palau'
        WHEN 'PY' THEN 'Paraguay'             WHEN 'QA' THEN 'Qatar'
        WHEN 'RO' THEN 'Romania'              WHEN 'RS' THEN 'Serbia'
        WHEN 'RU' THEN 'Russia'               WHEN 'RW' THEN 'Rwanda'
        WHEN 'SA' THEN 'Saudi Arabia'         WHEN 'SB' THEN 'Solomon Islands'
        WHEN 'SC' THEN 'Seychelles'           WHEN 'SD' THEN 'Sudan'
        WHEN 'SE' THEN 'Sweden'               WHEN 'SG' THEN 'Singapore'
        WHEN 'SI' THEN 'Slovenia'             WHEN 'SK' THEN 'Slovakia'
        WHEN 'SL' THEN 'Sierra Leone'         WHEN 'SM' THEN 'San Marino'
        WHEN 'SN' THEN 'Senegal'              WHEN 'SO' THEN 'Somalia'
        WHEN 'SR' THEN 'Suriname'             WHEN 'SS' THEN 'South Sudan'
        WHEN 'ST' THEN 'Sao Tome and Principe' WHEN 'SV' THEN 'El Salvador'
        WHEN 'SY' THEN 'Syria'                WHEN 'SZ' THEN 'Eswatini'
        WHEN 'TD' THEN 'Chad'                 WHEN 'TG' THEN 'Togo'
        WHEN 'TH' THEN 'Thailand'             WHEN 'TJ' THEN 'Tajikistan'
        WHEN 'TL' THEN 'Timor-Leste'          WHEN 'TM' THEN 'Turkmenistan'
        WHEN 'TN' THEN 'Tunisia'              WHEN 'TO' THEN 'Tonga'
        WHEN 'TR' THEN 'Turkey'               WHEN 'TT' THEN 'Trinidad and Tobago'
        WHEN 'TV' THEN 'Tuvalu'               WHEN 'TZ' THEN 'Tanzania'
        WHEN 'UA' THEN 'Ukraine'              WHEN 'UG' THEN 'Uganda'
        WHEN 'US' THEN 'United States'        WHEN 'UY' THEN 'Uruguay'
        WHEN 'UZ' THEN 'Uzbekistan'           WHEN 'VA' THEN 'Vatican City'
        WHEN 'VC' THEN 'Saint Vincent and the Grenadines'
        WHEN 'VE' THEN 'Venezuela'            WHEN 'VN' THEN 'Vietnam'
        WHEN 'VU' THEN 'Vanuatu'              WHEN 'WS' THEN 'Samoa'
        WHEN 'YE' THEN 'Yemen'                WHEN 'ZA' THEN 'South Africa'
        WHEN 'ZM' THEN 'Zambia'               WHEN 'ZW' THEN 'Zimbabwe'
        ELSE MAX(c.client_country)
    END                                                                         AS client_country,                  -- 7
    MAX(c.client_state)                                                         AS client_state,                    -- 8
    MAX(c.client_city)                                                          AS client_city,                     -- 9
    MAX(c.client_street)                                                        AS client_street,                   -- 10
    COALESCE(
        MAX(CASE WHEN c.funnel_type = 'main' THEN c.product_name END),
        (
            SELECT mp2.main_product_name
            FROM main_por_grupo mp2
            WHERE mp2.client_email = c.client_email
              AND mp2.account_id = c.account_id
              AND mp2.main_product_name IS NOT NULL
              AND mp2.grupo_ts <= MIN(c.created_at_ts)
            ORDER BY mp2.grupo_ts DESC
            LIMIT 1
        )
    )                                                                           AS product_name,                    -- 11
    COALESCE(
        MAX(CASE WHEN c.funnel_type = 'main' THEN c.offer_name END),
        (
            SELECT mp2.main_offer_name
            FROM main_por_grupo mp2
            WHERE mp2.client_email = c.client_email
              AND mp2.account_id = c.account_id
              AND mp2.main_offer_name IS NOT NULL
              AND mp2.grupo_ts <= MIN(c.created_at_ts)
            ORDER BY mp2.grupo_ts DESC
            LIMIT 1
        )
    )                                                                           AS offer_name,                      -- 12
    COALESCE(
        MAX(CASE WHEN c.funnel_type = 'main' THEN c.product_sku END),
        (
            SELECT mp2.main_product_sku
            FROM main_por_grupo mp2
            WHERE mp2.client_email = c.client_email
              AND mp2.account_id = c.account_id
              AND mp2.main_product_sku IS NOT NULL
              AND mp2.grupo_ts <= MIN(c.created_at_ts)
            ORDER BY mp2.grupo_ts DESC
            LIMIT 1
        )
    )                                                                           AS product_sku,                     -- 13
    ROUND(SUM(c.product_cost), 4)                                               AS product_cost,                    -- 14
    ROUND(SUM(c.product_cost_usd), 2)                                           AS product_cost_usd,                -- 15
    SUM(c.quantity)                                                             AS quantity,                        -- 16
    MAX(CASE WHEN c.funnel_type = 'main' THEN c.quantity END)                   AS quantity_principal,              -- 17
    ROUND(SUM(c.total_price), 4)                                                AS total_price,                     -- 18
    ROUND(SUM(c.total_price_usd), 2)                                            AS total_price_usd,                 -- 19
    ROUND(SUM(c.taxes), 4)                                                      AS taxes,                           -- 20
    ROUND(SUM(c.taxes_usd), 2)                                                  AS taxes_usd,                       -- 21
    ROUND(SUM(c.total_refund), 4)                                               AS total_refund,                    -- 22
    ROUND(SUM(c.total_refund_usd), 2)                                           AS total_refund_usd,                -- 23
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN COALESCE(c.commission, 0) + COALESCE(c.affiliate_amount, 0)
             ELSE c.commission END), 4)                                         AS commission,                      -- 24
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN COALESCE(c.commission_usd, 0) + COALESCE(c.affiliate_amount_usd, 0)
             ELSE c.commission_usd END), 2)                                     AS commission_usd,                  -- 25
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN 0
             ELSE c.affiliate_amount END), 4)                                   AS affiliate_amount,                -- 26
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN 0
             ELSE c.affiliate_amount_usd END), 2)                               AS affiliate_amount_usd,            -- 27
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN COALESCE(c.affiliate_amount, 0)
             ELSE 0 END), 4)                                                    AS revenue_afiliado,                -- 28
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN COALESCE(c.affiliate_amount_usd, 0)
             ELSE 0 END), 2)                                                    AS revenue_afiliado_usd,            -- 29
    SUM(CASE WHEN c.funnel_type = 'upsell1'    THEN 1 ELSE 0 END)               AS has_upsell,                      -- 30
    SUM(CASE WHEN c.funnel_type = 'upsell2'    THEN 1 ELSE 0 END)               AS has_upsell2,                     -- 31
    SUM(CASE WHEN c.funnel_type = 'upsell3'    THEN 1 ELSE 0 END)               AS has_upsell3,                     -- 32
    SUM(CASE WHEN c.funnel_type = 'downsell1'  THEN 1 ELSE 0 END)               AS has_downsell,                    -- 33
    SUM(CASE WHEN c.funnel_type = 'downsell2'  THEN 1 ELSE 0 END)               AS has_downsell2,                   -- 34
    SUM(CASE WHEN c.funnel_type = 'downsell3'  THEN 1 ELSE 0 END)               AS has_downsell3,                   -- 35
    SUM(CASE WHEN c.funnel_type = 'order_bump' THEN 1 ELSE 0 END)               AS has_order_bump,                  -- 36
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell1'    THEN c.total_price     ELSE 0 END), 2) AS total_price_upsell,           -- 37
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell1'    THEN c.total_price_usd ELSE 0 END), 2) AS total_price_upsell_usd,       -- 38
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell2'    THEN c.total_price     ELSE 0 END), 2) AS total_price_upsell2,          -- 39
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell2'    THEN c.total_price_usd ELSE 0 END), 2) AS total_price_upsell2_usd,      -- 40
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell3'    THEN c.total_price     ELSE 0 END), 2) AS total_price_upsell3,          -- 41
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell3'    THEN c.total_price_usd ELSE 0 END), 2) AS total_price_upsell3_usd,      -- 42
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell1'  THEN c.total_price     ELSE 0 END), 2) AS total_price_downsell,         -- 43
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell1'  THEN c.total_price_usd ELSE 0 END), 2) AS total_price_downsell_usd,     -- 44
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell2'  THEN c.total_price     ELSE 0 END), 2) AS total_price_downsell2,        -- 45
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell2'  THEN c.total_price_usd ELSE 0 END), 2) AS total_price_downsell2_usd,    -- 46
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell3'  THEN c.total_price     ELSE 0 END), 2) AS total_price_downsell3,        -- 47
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell3'  THEN c.total_price_usd ELSE 0 END), 2) AS total_price_downsell3_usd,    -- 48
    ROUND(SUM(CASE WHEN c.funnel_type = 'order_bump' THEN c.total_price     ELSE 0 END), 2) AS total_price_order_bump,       -- 49
    ROUND(SUM(CASE WHEN c.funnel_type = 'order_bump' THEN c.total_price_usd ELSE 0 END), 2) AS total_price_order_bump_usd,   -- 50

    -- Colunas NAO existentes no BuyGoods - preenchidas com NULL
    CAST(NULL AS CHAR)                                                          AS coupon_code,                     -- 51

    DATE(MIN(c.created_at_ts))                                                  AS created_at_date,                 -- 52
    TIME_FORMAT(TIME(MIN(c.created_at_ts)), '%H:%i:%s')                         AS created_at_hour,                 -- 53
    MAX(c.date_refunded)                                                        AS date_refunded,                   -- 54

    -- UTMs agora vem direto da silver tb_gex_buygoods_physical_new
    MAX(c.utm_source)                                                           AS utm_source,                      -- 55
    MAX(c.utm_medium)                                                           AS utm_medium,                      -- 56
    MAX(c.utm_content)                                                          AS utm_content,                     -- 57
    MAX(c.utm_term)                                                             AS utm_term,                        -- 58
    MAX(c.utm_campaign)                                                         AS utm_campaign,                    -- 59
    CAST(NULL AS CHAR)                                                          AS src,                             -- 60

    MAX(c.platform)                                                             AS platform,                        -- 61
    MAX(c.affiliate_name)                                                       AS affiliate_name,                  -- 62

    -- vendor_name nao existe na BuyGoods (vem vazio no silver)
    CAST(NULL AS CHAR)                                                          AS vendor_name,                     -- 63
    CAST(MAX(CASE WHEN c.is_house_traffic = 1 THEN 1 ELSE 0 END) AS SIGNED)     AS is_house_traffic,                -- 64

    -- ============================================================
    -- NOVAS COLUNAS EXCLUSIVAS DO BUYGOODS (a partir da 65)
    -- ============================================================
    CONCAT(c.client_email, '_', c.account_id, '_', c.purchase_group_id_final)   AS purchase_group_id,               -- 65
    c.account_id                                                                AS account_id,                      -- 66
    MIN(c.datetime_platform)                                                    AS datetime_platform,               -- 67
    ROUND(SUM(c.total_collected_usd), 2)                                        AS total_collected_usd,             -- 68
    ROUND(SUM(c.iva), 4)                                                        AS iva,                             -- 69
    ROUND(SUM(c.iva_usd), 2)                                                    AS iva_usd,                         -- 70
    ROUND(SUM(c.refund_fee), 4)                                                 AS refund_fee,                      -- 71
    ROUND(SUM(c.refund_fee_usd), 2)                                             AS refund_fee_usd,                  -- 72
    ROUND(SUM(c.chargeback_fee), 4)                                             AS chargeback_fee,                  -- 73
    ROUND(SUM(c.chargeback_fee_usd), 2)                                         AS chargeback_fee_usd,              -- 74
    MAX(c.affiliate_id)                                                         AS affiliate_id                     -- 75

FROM classificado c
GROUP BY c.client_email, c.account_id, c.purchase_group_id_final
ORDER BY created_at_date DESC, created_at_hour DESC;

    -- 3. Troca atomica: usuario nunca ve tabela vazia
    RENAME TABLE
        instituto_experience.dashboard_gold_buygoods       TO instituto_experience.dashboard_gold_buygoods_old,
        instituto_experience.dashboard_gold_buygoods_stage TO instituto_experience.dashboard_gold_buygoods,
        instituto_experience.dashboard_gold_buygoods_old   TO instituto_experience.dashboard_gold_buygoods_stage;

END
```
