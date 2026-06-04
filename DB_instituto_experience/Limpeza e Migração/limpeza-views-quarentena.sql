-- ============================================================================
-- QUARENTENA DE VIEWS NÃO UTILIZADAS  ·  instituto_experience
-- Data da análise: 2026-06-04
-- Gerado pela skill `limpeza-banco` (proposta — NÃO foi executado pelo assistente)
-- ============================================================================
-- O QUE ESTE SCRIPT FAZ
--   Renomeia 59 views (válidas, mas sem uso há >=9 dias) para o prefixo
--   `_zzdrop_`. Isso é REVERSÍVEL e funciona como TESTE: se algo externo
--   (Looker Studio, n8n, app) lê a view, quebra na hora e visível -> basta
--   renomear de volta. Passadas 1-2 semanas sem reclamação, rode o DROP.
--
-- POR QUE QUARENTENA E NÃO DROP DIRETO
--   O performance_schema só enxerga ~9 dias (uptime). Views de uso mensal ou
--   dashboards não abertos na janela NÃO aparecem como "usados". O rename
--   transforma essa incerteza num teste real e seguro.
--
-- COMO REVERTER UMA VIEW (se algo quebrar):
--   RENAME TABLE instituto_experience._zzdrop_<nome> TO instituto_experience.<nome>;
--
-- PRÉ-REQUISITO: rodar o backup do DDL (ver limpeza-views-drop-datado.sql, PASSO 0).
-- Executar com conta ADMIN. RENAME TABLE em view é suportado no MySQL 8 (mesmo schema).
-- ============================================================================

USE instituto_experience;

RENAME TABLE empresa_geral                              TO _zzdrop_empresa_geral;
RENAME TABLE empresa_nutraceuticos_eua                  TO _zzdrop_empresa_nutraceuticos_eua;
RENAME TABLE empresa_nutraceuticos_novo                 TO _zzdrop_empresa_nutraceuticos_novo;
RENAME TABLE internal_sales_meta_cartpanda_v2           TO _zzdrop_internal_sales_meta_cartpanda_v2;
RENAME TABLE nps_distribuicao                           TO _zzdrop_nps_distribuicao;
RENAME TABLE nps_tempos                                 TO _zzdrop_nps_tempos;
RENAME TABLE nutraceuticos_reembolso                    TO _zzdrop_nutraceuticos_reembolso;
RENAME TABLE nutraceuticos_reembolso_v3                 TO _zzdrop_nutraceuticos_reembolso_v3;
RENAME TABLE reembolso_teste                            TO _zzdrop_reembolso_teste;
RENAME TABLE sua_view_unified_data                      TO _zzdrop_sua_view_unified_data;
RENAME TABLE v_daily_overview                           TO _zzdrop_v_daily_overview;
RENAME TABLE v_group_health                             TO _zzdrop_v_group_health;
RENAME TABLE v_messages_enriched                        TO _zzdrop_v_messages_enriched;
RENAME TABLE v_novos_recorrentes                        TO _zzdrop_v_novos_recorrentes;
RENAME TABLE v_retencao_dias                            TO _zzdrop_v_retencao_dias;
RENAME TABLE v_retencao_mensal                          TO _zzdrop_v_retencao_mensal;
RENAME TABLE v_sla_summary_by_tier                      TO _zzdrop_v_sla_summary_by_tier;
RENAME TABLE v_top5_longtail                            TO _zzdrop_v_top5_longtail;
RENAME TABLE v_top5_longtail_mensal                     TO _zzdrop_v_top5_longtail_mensal;
RENAME TABLE v_unanswered_current                       TO _zzdrop_v_unanswered_current;
RENAME TABLE view_affiliate_engagement                  TO _zzdrop_view_affiliate_engagement;
RENAME TABLE view_backend_performance_thales_final      TO _zzdrop_view_backend_performance_thales_final;
RENAME TABLE view_base_and_additional_data              TO _zzdrop_view_base_and_additional_data;
RENAME TABLE view_call_center                           TO _zzdrop_view_call_center;
RENAME TABLE view_campanhas_health                      TO _zzdrop_view_campanhas_health;
RENAME TABLE view_campanhas_health_v2                   TO _zzdrop_view_campanhas_health_v2;
RENAME TABLE view_campanhas_love                        TO _zzdrop_view_campanhas_love;
RENAME TABLE view_campanhas_love_money_health           TO _zzdrop_view_campanhas_love_money_health;
RENAME TABLE view_campanhas_love_v2                     TO _zzdrop_view_campanhas_love_v2;
RENAME TABLE view_campanhas_money                       TO _zzdrop_view_campanhas_money;
RENAME TABLE view_campanhas_money_v2                    TO _zzdrop_view_campanhas_money_v2;
RENAME TABLE view_consolidado_geral                     TO _zzdrop_view_consolidado_geral;
RENAME TABLE view_consolidated_transactions             TO _zzdrop_view_consolidated_transactions;
RENAME TABLE view_funil_nova_ideia                      TO _zzdrop_view_funil_nova_ideia;
RENAME TABLE view_funil_nova_ideia_consolidado          TO _zzdrop_view_funil_nova_ideia_consolidado;
RENAME TABLE view_groups_active_inactive                TO _zzdrop_view_groups_active_inactive;
RENAME TABLE view_messages_per_group                    TO _zzdrop_view_messages_per_group;
RENAME TABLE view_messages_per_hour                     TO _zzdrop_view_messages_per_hour;
RENAME TABLE view_messages_per_period                   TO _zzdrop_view_messages_per_period;
RENAME TABLE view_nutra_eua_vendas_reagrupado           TO _zzdrop_view_nutra_eua_vendas_reagrupado;
RENAME TABLE view_refund_analisys_cartpanda_funil_inter TO _zzdrop_view_refund_analisys_cartpanda_funil_inter;
RENAME TABLE view_refund_analisys_funil_nao_inter       TO _zzdrop_view_refund_analisys_funil_nao_inter;
RENAME TABLE view_refund_analisys_hotmart_funil_inter   TO _zzdrop_view_refund_analisys_hotmart_funil_inter;
RENAME TABLE view_refund_analisys_physical_funil_nao_inter TO _zzdrop_view_refund_analisys_physical_funil_nao_inter;
RENAME TABLE view_response_times                         TO _zzdrop_view_response_times;
RENAME TABLE view_segmentation                          TO _zzdrop_view_segmentation;
RENAME TABLE view_sla_compliance                        TO _zzdrop_view_sla_compliance;
RENAME TABLE view_team_performance                      TO _zzdrop_view_team_performance;
RENAME TABLE view_unified_data_all                      TO _zzdrop_view_unified_data_all;
RENAME TABLE view_unified_data_all_with_subs            TO _zzdrop_view_unified_data_all_with_subs;
RENAME TABLE view_vendas_assinaturas                    TO _zzdrop_view_vendas_assinaturas;
RENAME TABLE vw_affiliate_ads_spy                       TO _zzdrop_vw_affiliate_ads_spy;
RENAME TABLE vw_affiliate_share                         TO _zzdrop_vw_affiliate_share;
RENAME TABLE vw_escalation_map                          TO _zzdrop_vw_escalation_map;
RENAME TABLE vw_fca_week_comparison                     TO _zzdrop_vw_fca_week_comparison;
RENAME TABLE vw_logicall_rpl                            TO _zzdrop_vw_logicall_rpl;
RENAME TABLE vw_mention_summary                         TO _zzdrop_vw_mention_summary;
RENAME TABLE vw_team_performance_weekly                 TO _zzdrop_vw_team_performance_weekly;
RENAME TABLE vw_weekly_trend_by_tier                    TO _zzdrop_vw_weekly_trend_by_tier;

-- Total: 59 views renomeadas para _zzdrop_.
-- Conferir o que sobrou em quarentena:
--   SELECT TABLE_NAME FROM information_schema.VIEWS
--   WHERE TABLE_SCHEMA='instituto_experience' AND TABLE_NAME LIKE '\_zzdrop\_%';
