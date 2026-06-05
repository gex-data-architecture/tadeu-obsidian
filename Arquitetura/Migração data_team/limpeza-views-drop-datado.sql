-- ============================================================================
-- DROP DE VIEWS NÃO UTILIZADAS  ·  instituto_experience
-- Data da análise: 2026-06-04
-- Gerado pela skill `limpeza-banco` (proposta — NÃO foi executado pelo assistente)
-- ============================================================================
-- ORDEM DE EXECUÇÃO RECOMENDADA
--   PASSO 0 (sempre): backup do DDL de TODAS as views/rotinas.
--   PARTE A: DROP das 5 views QUEBRADAS  -> pode rodar JÁ (erram ao consultar,
--            ninguém consegue usá-las).
--   PARTE B: DROP das 59 views válidas  -> rodar SÓ APÓS 1-2 semanas de
--            quarentena (limpeza-views-quarentena.sql) sem nenhuma reclamação.
--
-- DROP VIEW nunca falha por dependência de FK (views não têm). Se uma view
-- dropada era usada por outra, a outra fica quebrada — mas todas as dependentes
-- aqui já estão na lista. Ordem entre os DROPs é irrelevante.
-- Executar com conta ADMIN.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- PASSO 0 — BACKUP DO DDL (rodar no shell, NÃO no cliente SQL)
-- ----------------------------------------------------------------------------
-- Estrutura completa (views + tabelas + rotinas), sem dados — leve e suficiente
-- para recriar qualquer view via CREATE:
--
--   mysqldump -h <HOST> -u <ADMIN> -p --no-data --routines --events \
--     --skip-triggers instituto_experience > backup_estrutura_2026-06-04.sql
--
-- (Opcional) só as 64 views afetadas:
--   mysqldump -h <HOST> -u <ADMIN> -p --no-data instituto_experience \
--     unified_data_view v_team_performance view_nutra_eua_acompanhamento \
--     view_unified_data_all_with_upsell vw_enriquecimento_dados \
--     <...as 59 da PARTE B...> > backup_views_drop_2026-06-04.sql


-- ============================================================================
-- PARTE A — 5 VIEWS QUEBRADAS (DROP imediato, após o PASSO 0)
-- ============================================================================
DROP VIEW IF EXISTS instituto_experience.unified_data_view;
DROP VIEW IF EXISTS instituto_experience.v_team_performance;
DROP VIEW IF EXISTS instituto_experience.view_nutra_eua_acompanhamento;
DROP VIEW IF EXISTS instituto_experience.view_unified_data_all_with_upsell;
DROP VIEW IF EXISTS instituto_experience.vw_enriquecimento_dados;  -- substituída por vw_enriquecimento_buygoods


-- ============================================================================
-- PARTE B — 59 VIEWS VÁLIDAS (DROP só APÓS a quarentena)
-- ----------------------------------------------------------------------------
-- Os nomes abaixo já assumem que passaram pela quarentena com prefixo _zzdrop_.
-- Se você PULOU a quarentena (não recomendado), remova o prefixo `_zzdrop_`.
-- ============================================================================
DROP VIEW IF EXISTS instituto_experience._zzdrop_empresa_geral;
DROP VIEW IF EXISTS instituto_experience._zzdrop_empresa_nutraceuticos_eua;
DROP VIEW IF EXISTS instituto_experience._zzdrop_empresa_nutraceuticos_novo;
DROP VIEW IF EXISTS instituto_experience._zzdrop_internal_sales_meta_cartpanda_v2;
DROP VIEW IF EXISTS instituto_experience._zzdrop_nps_distribuicao;
DROP VIEW IF EXISTS instituto_experience._zzdrop_nps_tempos;
DROP VIEW IF EXISTS instituto_experience._zzdrop_nutraceuticos_reembolso;
DROP VIEW IF EXISTS instituto_experience._zzdrop_nutraceuticos_reembolso_v3;
DROP VIEW IF EXISTS instituto_experience._zzdrop_reembolso_teste;
DROP VIEW IF EXISTS instituto_experience._zzdrop_sua_view_unified_data;
DROP VIEW IF EXISTS instituto_experience._zzdrop_v_daily_overview;
DROP VIEW IF EXISTS instituto_experience._zzdrop_v_group_health;
DROP VIEW IF EXISTS instituto_experience._zzdrop_v_messages_enriched;
DROP VIEW IF EXISTS instituto_experience._zzdrop_v_novos_recorrentes;
DROP VIEW IF EXISTS instituto_experience._zzdrop_v_retencao_dias;
DROP VIEW IF EXISTS instituto_experience._zzdrop_v_retencao_mensal;
DROP VIEW IF EXISTS instituto_experience._zzdrop_v_sla_summary_by_tier;
DROP VIEW IF EXISTS instituto_experience._zzdrop_v_top5_longtail;
DROP VIEW IF EXISTS instituto_experience._zzdrop_v_top5_longtail_mensal;
DROP VIEW IF EXISTS instituto_experience._zzdrop_v_unanswered_current;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_affiliate_engagement;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_backend_performance_thales_final;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_base_and_additional_data;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_call_center;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_campanhas_health;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_campanhas_health_v2;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_campanhas_love;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_campanhas_love_money_health;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_campanhas_love_v2;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_campanhas_money;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_campanhas_money_v2;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_consolidado_geral;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_consolidated_transactions;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_funil_nova_ideia;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_funil_nova_ideia_consolidado;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_groups_active_inactive;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_messages_per_group;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_messages_per_hour;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_messages_per_period;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_nutra_eua_vendas_reagrupado;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_refund_analisys_cartpanda_funil_inter;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_refund_analisys_funil_nao_inter;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_refund_analisys_hotmart_funil_inter;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_refund_analisys_physical_funil_nao_inter;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_response_times;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_segmentation;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_sla_compliance;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_team_performance;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_unified_data_all;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_unified_data_all_with_subs;
DROP VIEW IF EXISTS instituto_experience._zzdrop_view_vendas_assinaturas;
DROP VIEW IF EXISTS instituto_experience._zzdrop_vw_affiliate_ads_spy;
DROP VIEW IF EXISTS instituto_experience._zzdrop_vw_affiliate_share;
DROP VIEW IF EXISTS instituto_experience._zzdrop_vw_escalation_map;
DROP VIEW IF EXISTS instituto_experience._zzdrop_vw_fca_week_comparison;
DROP VIEW IF EXISTS instituto_experience._zzdrop_vw_logicall_rpl;
DROP VIEW IF EXISTS instituto_experience._zzdrop_vw_mention_summary;
DROP VIEW IF EXISTS instituto_experience._zzdrop_vw_team_performance_weekly;
DROP VIEW IF EXISTS instituto_experience._zzdrop_vw_weekly_trend_by_tier;

-- Total: 5 (Parte A) + 59 (Parte B) = 64 views removidas.
-- De 92 views -> restam 28 em uso.
