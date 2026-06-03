---
tipo: procedure
definer: "root@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-06-01 21:46:18"
alterada_em: "2026-06-01 21:46:18"
execucoes: 40
tags: [rotina, procedure]
---

# fill_buygoods_offer_names

## Dependências

- **Lê:** [[buygoods_internal_affiliates]], [[buygoods_products]]
- **Escreve:** [[tb_gex_buygoods_unified]]
- **Cria:** —
- **Trunca:** —
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 40 |
| Tempo médio | 1m22s |
| Tempo máx | 2m16s |
| Tempo total | 54m26s |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 93,613 |

## Corpo SQL

```sql
BEGIN

    -- ================================================================
    -- CENÁRIO 1: Primeiro preenchimento — AFILIADO EXTERNO
    -- ================================================================
    UPDATE instituto_experience.tb_gex_buygoods_unified cb
        INNER JOIN instituto_experience.buygoods_products cp
        ON cp.product_id = cb.product_id
            AND cp.account_name COLLATE utf8mb4_unicode_ci = cb.account_id
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
    UPDATE instituto_experience.tb_gex_buygoods_unified cb
        INNER JOIN instituto_experience.buygoods_products cp
        ON cp.product_id = cb.product_id
            AND cp.account_name COLLATE utf8mb4_unicode_ci = cb.account_id
        INNER JOIN instituto_experience.buygoods_internal_affiliates ia
        ON ia.affiliate_name COLLATE utf8mb4_unicode_ci = cb.affiliate_name
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
    UPDATE instituto_experience.tb_gex_buygoods_unified cb
        INNER JOIN instituto_experience.buygoods_products cp
        ON cp.product_id = cb.product_id
            AND cp.account_name COLLATE utf8mb4_unicode_ci = cb.account_id
        INNER JOIN instituto_experience.buygoods_internal_affiliates ia
        ON ia.affiliate_name COLLATE utf8mb4_unicode_ci = cb.affiliate_name

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
    UPDATE instituto_experience.tb_gex_buygoods_unified cb
        INNER JOIN instituto_experience.buygoods_internal_affiliates ia
        ON ia.affiliate_name COLLATE utf8mb4_unicode_ci = cb.affiliate_name
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
    UPDATE instituto_experience.tb_gex_buygoods_unified cb
        INNER JOIN instituto_experience.buygoods_internal_affiliates ia
        ON ia.affiliate_name COLLATE utf8mb4_unicode_ci = cb.affiliate_name
    SET cb.is_house_traffic = 1,
        cb.updated_at = DATE_SUB(NOW(), INTERVAL 3 HOUR)
    WHERE cb.is_house_traffic = 0;

END
```
