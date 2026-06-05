---
tipo: procedure
definer: "root@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-26 22:33:17"
alterada_em: "2026-05-26 22:33:17"
execucoes: ""
tags: [rotina, procedure]
---

# fill_clickbank_offer_names_aws

## Dependências

- **Lê:** [[clickbank_internal_affiliates]], [[clickbank_products]]
- **Escreve:** [[clickbank_physical_new_aws]], [[clickbank_products]]
- **Cria:** —
- **Trunca:** —
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN

    SET SQL_SAFE_UPDATES = 0;

    -- ================================================================
    -- CENÁRIO 1: Primeiro preenchimento — AFILIADO EXTERNO
    -- ================================================================
    UPDATE instituto_experience.clickbank_physical_new_aws cb
        INNER JOIN instituto_experience.clickbank_products cp
        ON cp.product_id = cb.product_sku
            AND cp.account_name = cb.vendor_name
    SET cb.offer_name = cp.offer_name,
        cb.updated_at = DATE_SUB(NOW(), INTERVAL 3 HOUR)
    WHERE cb.offer_name IS NULL
      AND cb.is_house_traffic = 0
      AND cp.offer_name IS NOT NULL
      AND cp.offer_name <> ''
      AND cp.offer_name_locked = 1;


    -- ================================================================
    -- CENÁRIO 2: Primeiro preenchimento — HOUSE TRAFFIC
    -- ================================================================
    UPDATE instituto_experience.clickbank_physical_new_aws cb
        INNER JOIN instituto_experience.clickbank_products cp
        ON cp.product_id = cb.product_sku
            AND cp.account_name = cb.vendor_name
        INNER JOIN instituto_experience.clickbank_internal_affiliates ia
        ON ia.affiliate_name = cb.affiliate_name
    SET cb.offer_name = CASE
                            WHEN LOCATE('] [', REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source)) > 0 THEN
                                CONCAT(
                                        SUBSTRING(
                                                REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source),
                                                1,
                                                CHAR_LENGTH(REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source))
                                                    - CHAR_LENGTH(SUBSTRING_INDEX(REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source), '] [', -1))
                                                    - 3
                                        ),
                                        '] [Gestor de Tráfego: ', ia.traffic_manager, '] [',
                                        SUBSTRING_INDEX(REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source), '] [', -1)
                                )
                            ELSE CONCAT(
                                    REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source),
                                    ' [Gestor de Tráfego: ', ia.traffic_manager, ']'
                                 )
        END,
        cb.updated_at = DATE_SUB(NOW(), INTERVAL 3 HOUR)
    WHERE cb.offer_name IS NULL
      AND cb.is_house_traffic = 1
      AND cp.offer_name IS NOT NULL
      AND cp.offer_name <> ''
      AND cp.offer_name_locked = 1;


    -- ================================================================
    -- CENÁRIO 3: Correção — HOUSE TRAFFIC com offer_name errado
    -- ================================================================
    UPDATE instituto_experience.clickbank_physical_new_aws cb
        INNER JOIN instituto_experience.clickbank_products cp
        ON cp.product_id = cb.product_sku
            AND cp.account_name = cb.vendor_name
        INNER JOIN instituto_experience.clickbank_internal_affiliates ia
        ON ia.affiliate_name = cb.affiliate_name
    SET cb.offer_name = CASE
                            WHEN LOCATE('] [', REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source)) > 0 THEN
                                CONCAT(
                                        SUBSTRING(
                                                REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source),
                                                1,
                                                CHAR_LENGTH(REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source))
                                                    - CHAR_LENGTH(SUBSTRING_INDEX(REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source), '] [', -1))
                                                    - 3
                                        ),
                                        '] [Gestor de Tráfego: ', ia.traffic_manager, '] [',
                                        SUBSTRING_INDEX(REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source), '] [', -1)
                                )
                            ELSE CONCAT(
                                    REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source),
                                    ' [Gestor de Tráfego: ', ia.traffic_manager, ']'
                                 )
        END,
        cb.updated_at = DATE_SUB(NOW(), INTERVAL 3 HOUR)
    WHERE cb.is_house_traffic = 1
      AND cb.offer_name LIKE '%Affiliate Marketing%'
      AND cp.offer_name IS NOT NULL
      AND cp.offer_name <> ''
      AND cp.offer_name_locked = 1;


    -- ================================================================
    -- CENÁRIO 4: Correção — HOUSE TRAFFIC sem tag de gestor
    -- ================================================================
    UPDATE instituto_experience.clickbank_physical_new_aws cb
        INNER JOIN instituto_experience.clickbank_internal_affiliates ia
        ON ia.affiliate_name = cb.affiliate_name
    SET cb.offer_name = CASE
                            WHEN LOCATE('] [', cb.offer_name) > 0 THEN
                                CONCAT(
                                        SUBSTRING(
                                                cb.offer_name,
                                                1,
                                                CHAR_LENGTH(cb.offer_name)
                                                    - CHAR_LENGTH(SUBSTRING_INDEX(cb.offer_name, '] [', -1))
                                                    - 3
                                        ),
                                        '] [Gestor de Tráfego: ', ia.traffic_manager, '] [',
                                        SUBSTRING_INDEX(cb.offer_name, '] [', -1)
                                )
                            ELSE CONCAT(cb.offer_name, ' [Gestor de Tráfego: ', ia.traffic_manager, ']')
        END,
        cb.updated_at = DATE_SUB(NOW(), INTERVAL 3 HOUR)
    WHERE cb.is_house_traffic = 1
      AND cb.offer_name IS NOT NULL
      AND cb.offer_name NOT LIKE '%Affiliate Marketing%'
      AND cb.offer_name NOT LIKE '%Gestor de Tráfego:%';


    -- ================================================================
    -- CENÁRIO 5: Marca is_house_traffic pra linhas que ainda não foram marcadas
    -- ================================================================
    UPDATE instituto_experience.clickbank_physical_new_aws cb
        INNER JOIN instituto_experience.clickbank_internal_affiliates ia
        ON ia.affiliate_name = cb.affiliate_name
    SET cb.is_house_traffic = 1,
        cb.updated_at = DATE_SUB(NOW(), INTERVAL 3 HOUR)
    WHERE cb.is_house_traffic = 0;


    -- ================================================================
    -- CENÁRIO 6: Resync — renomeação de oferta (afiliado externo)
    -- ================================================================
    UPDATE instituto_experience.clickbank_physical_new_aws cb
        INNER JOIN instituto_experience.clickbank_products cp
        ON cp.product_id = cb.product_sku
            AND cp.account_name = cb.vendor_name
    SET cb.offer_name = cp.offer_name,
        cb.updated_at = DATE_SUB(NOW(), INTERVAL 3 HOUR)
    WHERE cp.offer_name_resync = 1
      AND cb.is_house_traffic = 0
      AND cp.offer_name IS NOT NULL
      AND cp.offer_name <> ''
      AND cp.offer_name_locked = 1;


    -- ================================================================
    -- CENÁRIO 7: Resync — renomeação de oferta (house traffic)
    -- ================================================================
    UPDATE instituto_experience.clickbank_physical_new_aws cb
        INNER JOIN instituto_experience.clickbank_products cp
        ON cp.product_id = cb.product_sku
            AND cp.account_name = cb.vendor_name
        INNER JOIN instituto_experience.clickbank_internal_affiliates ia
        ON ia.affiliate_name = cb.affiliate_name
    SET cb.offer_name = CASE
                            WHEN LOCATE('] [', REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source)) > 0 THEN
                                CONCAT(
                                        SUBSTRING(
                                                REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source),
                                                1,
                                                CHAR_LENGTH(REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source))
                                                    - CHAR_LENGTH(SUBSTRING_INDEX(REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source), '] [', -1))
                                                    - 3
                                        ),
                                        '] [Gestor de Tráfego: ', ia.traffic_manager, '] [',
                                        SUBSTRING_INDEX(REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source), '] [', -1)
                                )
                            ELSE CONCAT(
                                    REPLACE(cp.offer_name, 'Affiliate Marketing', ia.traffic_source),
                                    ' [Gestor de Tráfego: ', ia.traffic_manager, ']'
                                 )
        END,
        cb.updated_at = DATE_SUB(NOW(), INTERVAL 3 HOUR)
    WHERE cp.offer_name_resync = 1
      AND cb.is_house_traffic = 1
      AND cp.offer_name IS NOT NULL
      AND cp.offer_name <> ''
      AND cp.offer_name_locked = 1;


    -- Resetar flag de resync
    UPDATE instituto_experience.clickbank_products
    SET offer_name_resync = 0
    WHERE offer_name_resync = 1;

    SET SQL_SAFE_UPDATES = 1;

END
```
