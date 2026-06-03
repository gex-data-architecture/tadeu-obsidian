---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-03-22 23:03:33"
alterada_em: "2026-03-22 23:03:33"
execucoes: 182
tags: [rotina, procedure]
---

# refresh_gerenciador_meta_ads_v2

## Dependências

- **Lê:** [[gerenciador_meta_ads_v2]], [[meta_ad_id]]
- **Escreve:** [[gerenciador_meta_ads_v2_stage]]
- **Cria:** —
- **Trunca:** [[gerenciador_meta_ads_v2_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 182 |
| Tempo médio | 1m32s |
| Tempo máx | 3m0s |
| Tempo total | 4h38m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 614,296,964 |

## Corpo SQL

```sql
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.gerenciador_meta_ads_v2_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.gerenciador_meta_ads_v2_stage;

    -- 2. Processa apenas os últimos 3 dias
    INSERT INTO instituto_experience.gerenciador_meta_ads_v2_stage
    SELECT
        ma.ad_id,
        ma.ad_name,
        ma.created_at_date,
        ma.account_name,
        ma.campaign_name,
        ma.adset_name,
        CASE
            WHEN ma.campaign_name LIKE '%[Gestor de Tr_fego:%]%'
                THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Tráfego:', -1), ']', 1))
            WHEN ma.campaign_name LIKE '%[Gestor de Trafego:%]%'
                THEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(ma.campaign_name, '[Gestor de Trafego:', -1), ']', 1))
            ELSE 'Não Encontrado'
        END AS gestor_trafego,
        CASE
            WHEN ma.campaign_name LIKE '%Funil de Nova Ideia #%'
                THEN CONCAT(
                    'Funil de Nova Ideia #',
                    REGEXP_SUBSTR(
                        SUBSTRING_INDEX(ma.campaign_name, 'Funil de Nova Ideia #', -1),
                        '^[0-9]+'
                    )
                )
            ELSE 'Não Encontrado'
        END AS funil_id,
        CONCAT(
            UPPER(LEFT(REGEXP_REPLACE(TRIM(SUBSTRING_INDEX(ma.campaign_name, ':', 1)), ' ', ''), 1)),
            LOWER(SUBSTRING(REGEXP_REPLACE(TRIM(SUBSTRING_INDEX(ma.campaign_name, ':', 1)), ' ', ''), 2))
        ) AS produto,
        COALESCE(SUM(ma.amount_spent_brl), 0)                                       AS amount_spent_brl,
        COALESCE(SUM(ma.spent_taxes), 0)                                            AS spent_taxes,
        COALESCE(SUM(ma.amount_spent_brl), 0) + COALESCE(SUM(ma.spent_taxes), 0)   AS amount_spent_total,
        ROUND((COALESCE(SUM(ma.amount_spent_brl), 0) + COALESCE(SUM(ma.spent_taxes), 0)) / 5.2, 2) AS amount_spent_total_usd,
        SUM(ma.impressions)                                                          AS impressions,
        SUM(ma.reach)                                                                AS reach,
        SUM(ma.link_clicks)                                                          AS link_clicks
    FROM instituto_experience.meta_ad_id ma FORCE INDEX (idx_meta_ads_date)
    WHERE ma.created_at_date >= DATE_SUB(CURDATE(), INTERVAL 3 DAY)
    GROUP BY
        ma.ad_id,
        ma.ad_name,
        ma.created_at_date,
        ma.account_name,
        ma.campaign_name,
        ma.adset_name;

    -- 3. Copia histórico anterior aos últimos 3 dias da tabela atual
    INSERT INTO instituto_experience.gerenciador_meta_ads_v2_stage
    SELECT *
    FROM instituto_experience.gerenciador_meta_ads_v2
    WHERE created_at_date < DATE_SUB(CURDATE(), INTERVAL 3 DAY);

    -- 4. Swap atômico
    RENAME TABLE
        instituto_experience.gerenciador_meta_ads_v2         TO instituto_experience.gerenciador_meta_ads_v2_old,
        instituto_experience.gerenciador_meta_ads_v2_stage   TO instituto_experience.gerenciador_meta_ads_v2,
        instituto_experience.gerenciador_meta_ads_v2_old     TO instituto_experience.gerenciador_meta_ads_v2_stage;
END
```
