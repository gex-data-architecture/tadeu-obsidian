---
tipo: procedure
definer: "root@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-02-16 17:18:01"
alterada_em: "2026-02-16 17:18:01"
execucoes: ""
tags: [rotina, procedure]
---

# sp_refresh_gerenciador_meta_ads

## Dependências

- **Lê:** [[meta_ad_id]]
- **Escreve:** [[gerenciador_meta_ads]]
- **Cria:** —
- **Trunca:** [[gerenciador_meta_ads]]
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN

    TRUNCATE TABLE `instituto_experience`.`gerenciador_meta_ads`;

    INSERT INTO `instituto_experience`.`gerenciador_meta_ads` (
        ad_id,
        ad_name,
        created_at_date,
        account_name,
        campaign_name,
        adset_name,
        gestor_trafego,
        funil_id,
        amount_spent_brl,
        spent_taxes,
        amount_spent_total,
        impressions,
        reach,
        link_clicks
    )
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
                THEN CONCAT('Funil de Nova Ideia #',
                            REGEXP_SUBSTR(
                                    SUBSTRING_INDEX(ma.campaign_name, 'Funil de Nova Ideia #', -1),
                                    '^[0-9]+'
                            ))
            ELSE 'Não Encontrado'
            END AS funil_id,
        COALESCE(SUM(ma.amount_spent_brl), 0) AS amount_spent_brl,
        COALESCE(SUM(ma.spent_taxes), 0) AS spent_taxes,
        COALESCE(SUM(ma.amount_spent_brl), 0) + COALESCE(SUM(ma.spent_taxes), 0) AS amount_spent_total,
        SUM(ma.impressions) AS impressions,
        SUM(ma.reach) AS reach,
        SUM(ma.link_clicks) AS link_clicks
    FROM `instituto_experience`.`meta_ad_id` ma FORCE INDEX (`idx_meta_ads_date`)
    WHERE ma.created_at_date >= '2026-01-01'
    GROUP BY
        ma.ad_id,
        ma.ad_name,
        ma.created_at_date,
        ma.account_name,
        ma.campaign_name,
        ma.adset_name;

END
```
