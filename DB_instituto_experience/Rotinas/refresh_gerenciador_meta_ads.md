---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-03-08 13:39:43"
alterada_em: "2026-03-08 13:39:43"
execucoes: ""
tags: [rotina, procedure]
---

# refresh_gerenciador_meta_ads

## Dependências

- **Lê:** [[meta_ad_id]]
- **Escreve:** —
- **Cria:** —
- **Trunca:** `gerenciador_meta_ads_stage`
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
        TRUNCATE TABLE instituto_experience.gerenciador_meta_ads_stage;
        RESIGNAL;
    END;

    TRUNCATE TABLE instituto_experience.gerenciador_meta_ads_stage;

    INSERT INTO instituto_experience.gerenciador_meta_ads_stage
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
        COALESCE(SUM(ma.amount_spent_brl), 0)                                    AS amount_spent_brl,
        COALESCE(SUM(ma.spent_taxes), 0)                                         AS spent_taxes,
        COALESCE(SUM(ma.amount_spent_brl), 0) + COALESCE(SUM(ma.spent_taxes), 0) AS amount_spent_total,
        SUM(ma.impressions)                                                       AS impressions,
        SUM(ma.reach)                                                             AS reach,
        SUM(ma.link_clicks)                                                       AS link_clicks
    FROM instituto_experience.meta_ad_id ma FORCE INDEX (idx_meta_ads_date)
    WHERE ma.created_at_date >= '2026-01-01'
    GROUP BY
        ma.ad_id,
        ma.ad_name,
        ma.created_at_date,
        ma.account_name,
        ma.campaign_name,
        ma.adset_name;

    RENAME TABLE
        instituto_experience.gerenciador_meta_ads       TO instituto_experience.gerenciador_meta_ads_old,
        instituto_experience.gerenciador_meta_ads_stage TO instituto_experience.gerenciador_meta_ads,
        instituto_experience.gerenciador_meta_ads_old   TO instituto_experience.gerenciador_meta_ads_stage;

END
```
