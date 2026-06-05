---
tipo: procedure
definer: "root@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-04-20 17:51:59"
alterada_em: "2026-04-20 17:51:59"
execucoes: 56
tags: [rotina, procedure]
---

# ProcessMetaAdsFromJSON_FAST

## Dependências

- **Lê:** [[exchange_rates]]
- **Escreve:** [[meta_ad_id]]
- **Cria:** `tmp_meta_ads`
- **Trunca:** —
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 56 |
| Tempo médio | 58 ms |
| Tempo máx | 665 ms |
| Tempo total | 3.2 s |
| Erros | 0 |
| Warnings | 28,585 |
| Linhas afetadas (total) | 40,677 |

## Corpo SQL

```sql
BEGIN
    CREATE TEMPORARY TABLE tmp_meta_ads (
        account_id VARCHAR(45),
        ad_id VARCHAR(255),
        account_name VARCHAR(255),
        campaign_name VARCHAR(255),
        adset_name VARCHAR(255),
        ad_name VARCHAR(255),
        created_at_date DATE,
        amount_spent DECIMAL(15,2),
        impressions INT,
        reach INT,
        link_clicks INT,
        account_currency VARCHAR(3),
        PRIMARY KEY (account_id, ad_id, created_at_date)
    ) ENGINE=MEMORY;

    INSERT INTO tmp_meta_ads
    SELECT
        jt.account_id,
        jt.ad_id,
        jt.account_name,
        jt.campaign_name,
        jt.adset_name,
        jt.ad_name,
        jt.created_at_date,
        jt.amount_spent_brl,
        jt.impressions,
        jt.reach,
        jt.link_clicks,
        jt.account_currency
    FROM JSON_TABLE(
        p_json_data,
        '$[*]' COLUMNS (
            account_id VARCHAR(45) PATH '$.account_id',
            ad_id VARCHAR(255) PATH '$.ad_id',
            account_name VARCHAR(255) PATH '$.account_name',
            campaign_name VARCHAR(255) PATH '$.campaign_name',
            adset_name VARCHAR(255) PATH '$.adset_name',
            ad_name VARCHAR(255) PATH '$.ad_name',
            created_at_date DATE PATH '$.created_at_date',
            amount_spent_brl DECIMAL(15,2) PATH '$.amount_spent_brl',
            impressions INT PATH '$.impressions',
            reach INT PATH '$.reach',
            link_clicks INT PATH '$.link_clicks',
            account_currency VARCHAR(3) PATH '$.account_currency'
        )
    ) jt;

    INSERT INTO meta_ad_id (
        account_id,
        ad_id,
        account_name,
        campaign_name,
        adset_name,
        ad_name,
        created_at_date,
        amount_spent_brl,
        impressions,
        reach,
        link_clicks,
        account_currency,
        original_value,
        amount_spent_usd,
        spent_taxes
    )
    SELECT
        t.account_id,
        t.ad_id,
        t.account_name,
        t.campaign_name,
        t.adset_name,
        t.ad_name,
        t.created_at_date,
        CASE
            WHEN t.account_currency = 'USD'
            THEN t.amount_spent * er.rate
            ELSE t.amount_spent
        END,
        t.impressions,
        t.reach,
        t.link_clicks,
        t.account_currency,
        t.amount_spent,
        CASE
            WHEN t.account_currency = 'USD'
            THEN t.amount_spent
            ELSE 0
        END,
        CASE
            WHEN t.account_currency = 'BRL'
            THEN t.amount_spent*0.12
            ELSE 0
        END
    FROM tmp_meta_ads t
    LEFT JOIN exchange_rates er
        ON er.source_currency = 'USD'
       AND er.target_currency = 'BRL'
       AND er.date = t.created_at_date
    ON DUPLICATE KEY UPDATE
        account_name      = VALUES(account_name),
        campaign_name     = VALUES(campaign_name),
        adset_name        = VALUES(adset_name),
        ad_name           = VALUES(ad_name),
        amount_spent_brl  = VALUES(amount_spent_brl),
        amount_spent_usd  = VALUES(amount_spent_usd),
        impressions       = VALUES(impressions),
        reach             = VALUES(reach),
        link_clicks       = VALUES(link_clicks),
        account_currency  = VALUES(account_currency),
        original_value    = VALUES(original_value),
        spent_taxes 	  = VALUES(spent_taxes),
        account_id        = VALUES(account_id);

    DROP TEMPORARY TABLE tmp_meta_ads;
END
```
