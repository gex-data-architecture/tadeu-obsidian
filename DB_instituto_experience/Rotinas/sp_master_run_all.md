---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-27 11:33:57"
alterada_em: "2026-05-27 11:33:57"
execucoes: 172
tags: [rotina, procedure]
---

# sp_master_run_all

## Dependências

- **Lê:** —
- **Escreve:** —
- **Cria:** —
- **Trunca:** —
- **Dropa:** —
- **Chama:** [[atualizar_custos_conta_agencia_diaria]], [[atualizar_custos_gerais_diaria]], [[atualizar_custos_trafego_diaria]], [[fill_buygoods_offer_names]], [[fill_clickbank_offer_names]], [[fix_collation_clickbank]], [[fix_gestor_offer_names_aws]], [[refresh_dashboard_affiliate_nutra]], [[refresh_dashboard_affiliate_nutra_usd]], [[refresh_dashboard_anomalia_diaria]], [[refresh_dashboard_atendimento]], [[refresh_dashboard_atendimento_backlog]], [[refresh_dashboard_atendimento_retornos]], [[refresh_dashboard_auditoria_leads]], [[refresh_dashboard_channels_country_daily]], [[refresh_dashboard_channels_marketing]], [[refresh_dashboard_dims]], [[refresh_dashboard_gold_buygoods]], [[refresh_dashboard_gold_clickbank]], [[refresh_dashboard_gold_clickbank_buygoods]], [[refresh_dashboard_internal_sales_v2]], [[refresh_dashboard_lead_events]], [[refresh_dashboard_leads_alerts]], [[refresh_dashboard_leads_por_dia]], [[refresh_dashboard_ranking_agentes]], [[refresh_dashboard_reembolso]], [[refresh_dashboard_reembolso_coortes]], [[refresh_dashboard_sla_times]], [[refresh_gerenciador_meta_ads_v2]], [[refresh_gerenciador_meta_consolidado_v2]], [[refresh_gerenciador_meta_vendas_v2]], [[refresh_internal_funnel_v2]], [[refresh_internal_product_v2]]

## Chamada por
—

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 172 |
| Tempo médio | 36m2s |
| Tempo máx | 2h4m |
| Tempo total | 103h17m |
| Erros | 0 |
| Warnings | 0 |
| Linhas afetadas (total) | 26,263 |

## Corpo SQL

```sql
BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;

    -- Aplica READ COMMITTED para toda a sessão do event.
    -- Reduz contenção de lock com inserts/updates de outros sistemas
    -- (ETL, escritas de produção) durante o refresh dos dashboards.
    SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

    IF GET_LOCK('lock_fila_dashboard', 0) THEN
        
        CALL instituto_experience.fix_collation_clickbank();
        SET  SQL_SAFE_UPDATES = 0;
        CALL instituto_experience.fill_buygoods_offer_names();
        CALL instituto_experience.fill_clickbank_offer_names();
        CALL instituto_experience.fix_gestor_offer_names_aws();
        SET  SQL_SAFE_UPDATES = 1;
        CALL instituto_experience.refresh_dashboard_gold_clickbank();
        CALL instituto_experience.refresh_dashboard_gold_buygoods();
        CALL instituto_experience.refresh_dashboard_gold_clickbank_buygoods();
        CALL instituto_experience.refresh_dashboard_channels_marketing();
        CALL instituto_experience.refresh_dashboard_channels_country_daily();
        CALL instituto_experience.refresh_dashboard_auditoria_leads();
        CALL instituto_experience.refresh_dashboard_anomalia_diaria();
        CALL instituto_experience.refresh_dashboard_leads_alerts();
        CALL instituto_experience.refresh_dashboard_leads_por_dia();
        CALL instituto_experience.refresh_dashboard_lead_events();

        CALL instituto_experience.refresh_dashboard_dims();
        CALL instituto_experience.atualizar_custos_trafego_diaria();
        CALL instituto_experience.atualizar_custos_conta_agencia_diaria();
        CALL instituto_experience.atualizar_custos_gerais_diaria();

        CALL instituto_experience.refresh_internal_funnel_v2();
        CALL instituto_experience.refresh_internal_product_v2();
        CALL instituto_experience.refresh_gerenciador_meta_ads_v2();
        CALL instituto_experience.refresh_gerenciador_meta_vendas_v2();
        CALL instituto_experience.refresh_dashboard_internal_sales_v2();
        CALL instituto_experience.refresh_gerenciador_meta_consolidado_v2();
        
        CALL instituto_experience.refresh_dashboard_affiliate_nutra_usd();
        CALL instituto_experience.refresh_dashboard_affiliate_nutra();
        
        CALL instituto_experience.refresh_dashboard_reembolso();
        CALL instituto_experience.refresh_dashboard_reembolso_coortes();
        CALL instituto_experience.refresh_dashboard_atendimento();
        CALL instituto_experience.refresh_dashboard_atendimento_backlog();
        CALL instituto_experience.refresh_dashboard_atendimento_retornos();
        CALL instituto_experience.refresh_dashboard_sla_times();
        CALL instituto_experience.refresh_dashboard_ranking_agentes();




        SELECT RELEASE_LOCK('lock_fila_dashboard');
    END IF;
END
```
