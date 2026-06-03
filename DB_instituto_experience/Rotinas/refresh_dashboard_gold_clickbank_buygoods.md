---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-22 14:23:23"
alterada_em: "2026-05-22 14:23:23"
execucoes: 185
tags: [rotina, procedure]
---

# refresh_dashboard_gold_clickbank_buygoods

## Dependências

- **Lê:** [[dashboard_gold_buygoods]], [[dashboard_gold_clickbank]]
- **Escreve:** [[dashboard_gold_clickbank_buygoods_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_gold_clickbank_buygoods_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 185 |
| Tempo médio | 14.1 s |
| Tempo máx | 3m50s |
| Tempo total | 43m36s |
| Erros | 6 |
| Warnings | 0 |
| Linhas afetadas (total) | 75,233,488 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_gold_clickbank_buygoods_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_gold_clickbank_buygoods_stage;

    -- 2. Insere todas as linhas da gold_clickbank (mantem todos os campos do CB intactos)
    INSERT INTO instituto_experience.dashboard_gold_clickbank_buygoods_stage
    SELECT
        transaction_id, payment_status, client_name, client_email, client_phone, client_zip,
        client_country, client_state, client_city, client_street, product_name, offer_name,
        product_sku, product_cost, product_cost_usd, quantity, quantity_principal, total_price,
        total_price_usd, taxes, taxes_usd, total_refund, total_refund_usd, commission,
        commission_usd, affiliate_amount, affiliate_amount_usd, revenue_afiliado, revenue_afiliado_usd, has_upsell,
        has_upsell2, has_upsell3, has_downsell, has_downsell2, has_downsell3, has_order_bump,
        total_price_upsell, total_price_upsell_usd, total_price_upsell2, total_price_upsell2_usd, total_price_upsell3, total_price_upsell3_usd,
        total_price_downsell, total_price_downsell_usd, total_price_downsell2, total_price_downsell2_usd, total_price_downsell3, total_price_downsell3_usd,
        total_price_order_bump, total_price_order_bump_usd, coupon_code, created_at_date, created_at_hour, date_refunded,
        utm_source, utm_medium, utm_content, utm_term, utm_campaign, src,
        platform, affiliate_name, vendor_name, is_house_traffic
    FROM instituto_experience.dashboard_gold_clickbank;

    -- 3. Insere todas as linhas da gold_buygoods
    --    Pega APENAS as 64 colunas que existem na clickbank (descarta as exclusivas BG da 65 em diante)
    --    Substitui vendor_name (que e NULL no BG) pelo account_id como TEXTO
    INSERT INTO instituto_experience.dashboard_gold_clickbank_buygoods_stage
    SELECT
        transaction_id, payment_status, client_name, client_email, client_phone, client_zip,
        client_country, client_state, client_city, client_street, product_name, offer_name,
        product_sku, product_cost, product_cost_usd, quantity, quantity_principal, total_price,
        total_price_usd, taxes, taxes_usd, total_refund, total_refund_usd, commission,
        commission_usd, affiliate_amount, affiliate_amount_usd, revenue_afiliado, revenue_afiliado_usd, has_upsell,
        has_upsell2, has_upsell3, has_downsell, has_downsell2, has_downsell3, has_order_bump,
        total_price_upsell, total_price_upsell_usd, total_price_upsell2, total_price_upsell2_usd, total_price_upsell3, total_price_upsell3_usd,
        total_price_downsell, total_price_downsell_usd, total_price_downsell2, total_price_downsell2_usd, total_price_downsell3, total_price_downsell3_usd,
        total_price_order_bump, total_price_order_bump_usd, coupon_code, created_at_date, created_at_hour, date_refunded,
        utm_source, utm_medium, utm_content, utm_term, utm_campaign, src,
        platform, affiliate_name, CAST(account_id AS CHAR) AS vendor_name, is_house_traffic
    FROM instituto_experience.dashboard_gold_buygoods;

    -- 4. Troca atomica: usuario nunca ve tabela vazia
    RENAME TABLE
        instituto_experience.dashboard_gold_clickbank_buygoods       TO instituto_experience.dashboard_gold_clickbank_buygoods_old,
        instituto_experience.dashboard_gold_clickbank_buygoods_stage TO instituto_experience.dashboard_gold_clickbank_buygoods,
        instituto_experience.dashboard_gold_clickbank_buygoods_old   TO instituto_experience.dashboard_gold_clickbank_buygoods_stage;

END
```
