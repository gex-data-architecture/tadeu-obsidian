---
tipo: checklist-limpeza
schema: instituto_experience
data_analise: 2026-06-04
total_tabelas: 356
total_views: 92
status: proposta (nenhum DDL executado)
tags: [limpeza, checklist, lint]
---
# ☑️ Checklist de limpeza — `instituto_experience` (tabelas + views)

> **Como usar:** percorra as tabelas abaixo e, na coluna **Excluir?**, escreva `x`
> nas que você quer remover (deixe vazio = manter). Depois me avise — eu gero os
> scripts de **quarentena (RENAME)** e **DROP** só com o que você marcou.
> **Nada é apagado por aqui** (MCP é read-only; quem executa DDL é o DBA/admin).

## ⚠️ Antes de marcar (resumo — **regras completas em [[Regras de Exclusão]]**)
- **Uso = janela de ~9 dias** (digest do `performance_schema`; `general_log` off): *"sem uso" ≠ "nunca usada"*.
- **Leitura externa (Looker/n8n) é invisível** → para remover algo incerto, prefira **quarentena por RENAME `_zzdrop_`** (reversível) antes do DROP.
- **Linhas é estimativa** do InnoDB — confirmar `COUNT(*)` nas vazias.
- **Nunca exclua** tabelas de **swap** (`_stage`/`_old`/`_new`/`_aws_new`).
- Views "em uso" com 1 acesso datado de hoje podem ser **sondagem própria** — a classificação usa o estado pré-sondagem.

## Resumo
| Objeto | Total | Excluir/Quarentena sugerido | Manter |
|---|--:|--:|--:|
| **Views** | 92 | 5 quebradas + 59 sem uso | 28 |
| **Tabelas** | 356 | 15 vazias + ~180 "revisar" | ~160 (em uso + swap) |

> Metodologia, passo a passo e histórico em [[Regras de Exclusão]].

---

# 1) VIEWS (92)

## ❌ Quebradas — recomendado **excluir** (DROP direto; erram ao consultar)
| View                                | Análise                                                 | Sinal | Excluir? |
| ----------------------------------- | ------------------------------------------------------- | ----- | -------- |
| `unified_data_view`                 | QUEBRADA — referência inválida                          | erro  |          |
| `v_team_performance`                | QUEBRADA — erro de sintaxe na definição                 | erro  |          |
| `view_nutra_eua_acompanhamento`     | QUEBRADA — referência inválida                          | erro  |          |
| `view_unified_data_all_with_upsell` | QUEBRADA — referência inválida                          | erro  |          |
| `vw_enriquecimento_dados`           | QUEBRADA — substituída por `vw_enriquecimento_buygoods` | erro  |          |

## 🟡 Sem uso há ≥9 dias e sem referência — **quarentena** → DROP
| View                                            | Análise                                             | Sinal | Excluir? |
| ----------------------------------------------- | --------------------------------------------------- | ----- | -------- |
| `empresa_geral`                                 | Sem uso ≥9d                                         | 0     |          |
| `empresa_nutraceuticos_eua`                     | Sem uso ≥9d                                         | 0     |          |
| `empresa_nutraceuticos_novo`                    | Sem uso ≥9d                                         | 0     |          |
| `internal_sales_meta_cartpanda_v2`              | Sem uso ≥9d (versão `_v2`)                          | 0     |          |
| `nps_distribuicao`                              | Sem uso ≥9d                                         | 0     |          |
| `nps_tempos`                                    | Sem uso ≥9d                                         | 0     |          |
| `nutraceuticos_reembolso`                       | Sem uso ≥9d                                         | 0     |          |
| `nutraceuticos_reembolso_v3`                    | Sem uso ≥9d (versão `_v3`)                          | 0     |          |
| `reembolso_teste`                               | Sem uso ≥9d (nome "teste")                          | 0     |          |
| `sua_view_unified_data`                         | Sem uso ≥9d (nome template "sua_view")              | 0     |          |
| `v_daily_overview`                              | Sem uso ≥9d                                         | 0     |          |
| `v_group_health`                                | Sem uso ≥9d                                         | 0     |          |
| `v_messages_enriched`                           | Sem uso ≥9d                                         | 0     |          |
| `v_novos_recorrentes`                           | Sem uso ≥9d                                         | 0     |          |
| `v_retencao_dias`                               | Sem uso ≥9d                                         | 0     |          |
| `v_retencao_mensal`                             | Sem uso ≥9d                                         | 0     |          |
| `v_sla_summary_by_tier`                         | Sem uso ≥9d                                         | 0     |          |
| `v_top5_longtail`                               | Sem uso ≥9d                                         | 0     |          |
| `v_top5_longtail_mensal`                        | Sem uso ≥9d                                         | 0     |          |
| `v_unanswered_current`                          | Sem uso ≥9d                                         | 0     |          |
| `view_affiliate_engagement`                     | Sem uso ≥9d                                         | 0     |          |
| `view_backend_performance_thales_final`         | Sem uso ≥9d (nome pessoal "thales_final")           | 0     |          |
| `view_base_and_additional_data`                 | Sem uso ≥9d                                         | 0     |          |
| `view_call_center`                              | Sem uso ≥9d                                         | 0     |          |
| `view_campanhas_health`                         | Sem uso ≥9d                                         | 0     |          |
| `view_campanhas_health_v2`                      | Sem uso ≥9d (versão `_v2`)                          | 0     |          |
| `view_campanhas_love`                           | Sem uso ≥9d                                         | 0     |          |
| `view_campanhas_love_money_health`              | Sem uso ≥9d                                         | 0     |          |
| `view_campanhas_love_v2`                        | Sem uso ≥9d (versão `_v2`)                          | 0     |          |
| `view_campanhas_money`                          | Sem uso ≥9d                                         | 0     |          |
| `view_campanhas_money_v2`                       | Sem uso ≥9d (versão `_v2`)                          | 0     |          |
| `view_consolidado_geral`                        | Sem uso ≥9d                                         | 0     |          |
| `view_consolidated_transactions`                | Sem uso ≥9d                                         | 0     |          |
| `view_funil_nova_ideia`                         | Sem uso ≥9d (nome "nova_ideia")                     | 0     |          |
| `view_funil_nova_ideia_consolidado`             | Sem uso ≥9d (nome "nova_ideia")                     | 0     |          |
| `view_groups_active_inactive`                   | Sem uso ≥9d                                         | 0     |          |
| `view_messages_per_group`                       | Sem uso ≥9d                                         | 0     |          |
| `view_messages_per_hour`                        | Sem uso ≥9d                                         | 0     |          |
| `view_messages_per_period`                      | Sem uso ≥9d                                         | 0     |          |
| `view_nutra_eua_vendas_reagrupado`              | Sem uso ≥9d                                         | 0     |          |
| `view_refund_analisys_cartpanda_funil_inter`    | Sem uso ≥9d                                         | 0     |          |
| `view_refund_analisys_funil_nao_inter`          | Sem uso ≥9d                                         | 0     |          |
| `view_refund_analisys_hotmart_funil_inter`      | Sem uso ≥9d                                         | 0     |          |
| `view_refund_analisys_physical_funil_nao_inter` | Sem uso ≥9d                                         | 0     |          |
| `view_response_times`                           | Sem uso ≥9d                                         | 0     |          |
| `view_segmentation`                             | Sem uso ≥9d                                         | 0     |          |
| `view_sla_compliance`                           | Sem uso ≥9d                                         | 0     |          |
| `view_team_performance`                         | Sem uso ≥9d (≠ `v_team_performance`, esta é válida) | 0     |          |
| `view_unified_data_all`                         | Sem uso ≥9d                                         | 0     |          |
| `view_unified_data_all_with_subs`               | Sem uso ≥9d                                         | 0     |          |
| `view_vendas_assinaturas`                       | Sem uso ≥9d                                         | 0     |          |
| `vw_affiliate_ads_spy`                          | Sem uso ≥9d                                         | 0     |          |
| `vw_affiliate_share`                            | Sem uso ≥9d                                         | 0     |          |
| `vw_escalation_map`                             | Sem uso ≥9d                                         | 0     |          |
| `vw_fca_week_comparison`                        | Sem uso ≥9d                                         | 0     |          |
| `vw_logicall_rpl`                               | Sem uso ≥9d                                         | 0     |          |
| `vw_mention_summary`                            | Sem uso ≥9d                                         | 0     |          |
| `vw_team_performance_weekly`                    | Sem uso ≥9d                                         | 0     |          |
| `vw_weekly_trend_by_tier`                       | Sem uso ≥9d                                         | 0     |          |

## ✅ Em uso — **manter** (runtime e/ou referência estática)
| View | Análise | Sinal (exec pré-sonda) | Excluir? |
|---|---|---|---|
| `vw_enriquecimento_buygoods` | Em uso (lida direto/Looker) | 89.870 |  |
| `affiliate_nutra` | Em uso (proc/event/view + runtime) | 41.806 |  |
| `affiliate_nutra_usd` | Em uso (proc/event/view + runtime) | 32.452 |  |
| `internal_sales` | Em uso (proc/event/view + runtime) | 5.137 |  |
| `affiliate_product` | Em uso (Looker) | 141 |  |
| `affiliate_funnel` | Em uso (Looker) | 126 |  |
| `vw_logicall_leads` | Em uso (referenciada + runtime) | 71 |  |
| `view_nutra_eua_vendas` | Em uso | 64 |  |
| `internal_funnel` | Em uso (proc/event + runtime) | 45 |  |
| `nutra_eua_vendas_2` | Em uso | 40 |  |
| `view_creative_tasks` | Em uso | 34 |  |
| `affiliate_score_usd` | Em uso (Looker) | 33 |  |
| `internal_product` | Em uso (proc/event + runtime) | 31 |  |
| `dashboard_gold_clickbank_dados_brutos` | Em uso | 29 |  |
| `vw_clickbank_offer_null_alert` | Em uso (view de alerta) | 22 |  |
| `affiliate_internal_funnel` | Em uso (Looker) | 14 |  |
| `affiliate_nutra_clickbank_new` | Em uso (Looker) | 14 |  |
| `affiliate_nutra_usd_worldmap_view` | Em uso (Looker) | 14 |  |
| `clickbank_as_affiliate_nutra_usd` | Em uso (Looker) | 14 |  |
| `dashboard_sms_marketing_v3` | Em uso (Looker) | 12 |  |
| `nutra_eua_vendas_new` | Em uso | 10 |  |
| `vw_affiliate_ranking` | Em uso (referenciada) | 3 |  |
| `vw_affiliate_ranking_mes` | Em uso | 2 |  |
| `vw_fila_grupos_pendentes` | Em uso | 2 |  |
| `v_afiliados_por_mes` | Em uso (referenciada) | 1 |  |
| `v_primeiro_mes_afiliado` | Referenciada por outra view | ref |  |
| `v_sla_calculations` | Referenciada por outra view | ref |  |
| `vw_phone_lookup` | Referenciada por procedure | ref |  |

---

# 2) TABELAS (356)
> Coluna *Análise* já traz a leitura. *Linhas* = **estimativa** (confirmar com `COUNT(*)` nas vazias).

## ⚠️ Vazias (estimativa) — confirmar e mandar p/ **quarentena** (15)
| Tabela | Análise | Linhas | Atualizada | Excluir? |
|---|---|--:|---|---|
| `cbc_c02_mar_2025_leads_oneclick` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `clickbank_fee_rates` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `clickbank_physical_v2` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `contatos_captura1x1` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `dashboard_cartpanda_pais_diario` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `dashboard_dim_gestorl` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `dashboard_gerenciador_unificado` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `dashboard_partner_affiliates` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `django_migrations` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `duelab_sessions` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `general_product_costs` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `regime_config` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `setup_carteirinha` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `v2cmp_c01_nov_2024_leads_oneclick` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |
| `web_users` | VAZIA (estim) - confirmar COUNT, quarentena | 0 | — |  |

## 🟡 Com dados, sem referência estática — **revisar** (não é prova de uso; checar Looker/n8n antes)
| Tabela | Análise | Linhas | Atualizada | Excluir? |
|---|---|--:|---|---|
| `300digital_customers` | COM DADOS, sem ref. estatica - revisar | 241 | — |  |
| `ULT_C01_ABR_2024` | COM DADOS, sem ref. estatica - revisar | 6557 | — |  |
| `acb_c01_jun_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 3672 | — |  |
| `acb_c02_set_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 1393 | — |  |
| `affiliate_forms` | COM DADOS, sem ref. estatica - revisar | 157 | — |  |
| `affiliate_orders` | COM DADOS, sem ref. estatica - revisar | 242 | — |  |
| `affiliate_performance` | COM DADOS, sem ref. estatica - revisar | 14251 | 2026-06-04 |  |
| `affiliate_score` | COM DADOS, sem ref. estatica - revisar | 2486 | — |  |
| `arf_f38_2024_aqs_whatsapp_history` | COM DADOS, sem ref. estatica - revisar | 1704 | — |  |
| `aulas_cademi` | COM DADOS, sem ref. estatica - revisar | 2441 | — |  |
| `automatecheckout` | COM DADOS, sem ref. estatica - revisar | 4655 | — |  |
| `block_offer` | COM DADOS, sem ref. estatica - revisar | 324 | — |  |
| `buygoods_export` | COM DADOS, sem ref. estatica - revisar | 7818 | — |  |
| `buygoods_new_raw` | COM DADOS, sem ref. estatica - revisar | 1085 | — |  |
| `buygoods_setup` | COM DADOS, sem ref. estatica - revisar | 157 | 2026-06-04 |  |
| `buygoods_silver_orders` | COM DADOS, sem ref. estatica - revisar | 312741 | 2026-06-01 |  |
| `buygoods_silver_orders_v2` | COM DADOS, sem ref. estatica - revisar | 294002 | 2026-06-01 |  |
| `buygoods_teste` | COM DADOS, sem ref. estatica - revisar (nome "teste") | 8521 | — |  |
| `call_center_leads` | COM DADOS, sem ref. estatica - revisar | 12910 | 2026-06-04 |  |
| `carteira_online` | COM DADOS, sem ref. estatica - revisar | 42 | — |  |
| `carteirinha_experience_control` | COM DADOS, sem ref. estatica - revisar | 2505 | — |  |
| `cartpanda_hash_list` | COM DADOS, sem ref. estatica - revisar | 180516 | — |  |
| `cartpanda_lostcarts` | COM DADOS, sem ref. estatica - revisar | 11372 | — |  |
| `cartpanda_physical_backup` | COM DADOS, sem ref. estatica - revisar (nome "backup") | 294696 | — |  |
| `cartpanda_processamento` | COM DADOS, sem ref. estatica - revisar | 2 | — |  |
| `cb_offer_lookup` | COM DADOS, sem ref. estatica - revisar | 115 | — |  |
| `cb_ticket_comments` | COM DADOS, sem ref. estatica - revisar | 80313 | 2026-06-04 |  |
| `cbc_c01_jun_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 3835 | — |  |
| `cct_c03_mai_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 19151 | — |  |
| `cdp_c01_mai_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 1119 | — |  |
| `cev_c09_upsell_history` | COM DADOS, sem ref. estatica - revisar | 817 | — |  |
| `cev_c10_mai_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 5769 | — |  |
| `cev_c11_jul_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 1886 | — |  |
| `cev_c12_set_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 2353 | — |  |
| `cev_c15_jan_2025_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 9287 | — |  |
| `cev_research` | COM DADOS, sem ref. estatica - revisar | 727 | — |  |
| `clickbank_setup` | COM DADOS, sem ref. estatica - revisar | 16 | — |  |
| `clickbank_webhook_raw` | COM DADOS, sem ref. estatica - revisar | 47000 | — |  |
| `clickup_automation` | COM DADOS, sem ref. estatica - revisar | 1430 | 2026-06-03 |  |
| `coi_c01_dez_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 1829 | — |  |
| `combo_experience_vip4_leads` | COM DADOS, sem ref. estatica - revisar | 3656 | — |  |
| `cpm_c01_jul_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 2308 | — |  |
| `cpt_c02_out_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 2340 | — |  |
| `csat_data` | COM DADOS, sem ref. estatica - revisar | 1211 | 2026-06-04 |  |
| `customers_carteirinha_setup` | COM DADOS, sem ref. estatica - revisar | 719 | — |  |
| `cxp_c01_abr_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 1383 | — |  |
| `cxp_c02_fev_2025_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 753 | — |  |
| `dashboard_atendimento_backlog_historico` | COM DADOS, sem ref. estatica - revisar | 1144 | — |  |
| `dashboard_channels_marketing_aws` | COM DADOS, sem ref. estatica - revisar | 47560 | — |  |
| `dashboard_daily_aov` | COM DADOS, sem ref. estatica - revisar | 6476 | — |  |
| `dashboard_unifed_cartclick` | COM DADOS, sem ref. estatica - revisar | 569808 | — |  |
| `dashboard_volume_diario` | COM DADOS, sem ref. estatica - revisar | 730 | — |  |
| `ddp_c01_set_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 21033 | — |  |
| `digistore_debug_log` | COM DADOS, sem ref. estatica - revisar (nome "debug_log") | 50 | — |  |
| `digistore_offers` | COM DADOS, sem ref. estatica - revisar | 40 | — |  |
| `digistore_orders_temp` | COM DADOS, sem ref. estatica - revisar (nome "temp") | 1833 | — |  |
| `digistore_physical_backup` | COM DADOS, sem ref. estatica - revisar (nome "backup") | 142 | — |  |
| `digistore_setup` | COM DADOS, sem ref. estatica - revisar | 710 | 2026-06-04 |  |
| `digistore_transactions_temp` | COM DADOS, sem ref. estatica - revisar (nome "temp") | 2065 | — |  |
| `duelab_events` | COM DADOS, sem ref. estatica - revisar | 2 | — |  |
| `duelab_tests` | COM DADOS, sem ref. estatica - revisar | 2 | — |  |
| `email_reports` | COM DADOS, sem ref. estatica - revisar | 7244 | — |  |
| `facebook_reports` | COM DADOS, sem ref. estatica - revisar | 32538 | — |  |
| `facebook_reports_accounts_list` | COM DADOS, sem ref. estatica - revisar | 333 | — |  |
| `facebook_reports_ad_id` | COM DADOS, sem ref. estatica - revisar | 202364 | — |  |
| `facebook_reports_country` | COM DADOS, sem ref. estatica - revisar | 571 | — |  |
| `facebook_reports_macro` | COM DADOS, sem ref. estatica - revisar | 31024 | — |  |
| `gabriel_finance_accounts` | COM DADOS, sem ref. estatica - revisar | 20 | — |  |
| `gabriel_finance_category` | COM DADOS, sem ref. estatica - revisar | 45 | — |  |
| `gabriel_finance_suppliers` | COM DADOS, sem ref. estatica - revisar | 165 | — |  |
| `gabriel_finance_transactions` | COM DADOS, sem ref. estatica - revisar | 3991 | — |  |
| `gex_company_config` | COM DADOS, sem ref. estatica - revisar | 4 | — |  |
| `gex_finance_accounts` | COM DADOS, sem ref. estatica - revisar | 27 | — |  |
| `gex_finance_category` | COM DADOS, sem ref. estatica - revisar | 291 | 2026-06-02 |  |
| `gex_finance_departments` | COM DADOS, sem ref. estatica - revisar | 96 | 2026-06-02 |  |
| `gex_finance_suppliers` | COM DADOS, sem ref. estatica - revisar | 6246 | 2026-06-03 |  |
| `gex_finance_transactions` | COM DADOS, sem ref. estatica - revisar | 57487 | 2026-06-04 |  |
| `gold_clickbank_aws` | COM DADOS, sem ref. estatica - revisar | 209976 | 2026-06-04 |  |
| `google_reports_ad_id` | COM DADOS, sem ref. estatica - revisar | 10825 | — |  |
| `google_reports_macro` | COM DADOS, sem ref. estatica - revisar | 1361 | — |  |
| `heygencriativo` | COM DADOS, sem ref. estatica - revisar | 10 | — |  |
| `ia_comments` | COM DADOS, sem ref. estatica - revisar | 3441 | — |  |
| `ia_messages` | COM DADOS, sem ref. estatica - revisar | 4 | — |  |
| `ia_pages` | COM DADOS, sem ref. estatica - revisar | 33 | — |  |
| `internacional_sales` | COM DADOS, sem ref. estatica - revisar | 44127 | — |  |
| `lead_05042024` | COM DADOS, sem ref. estatica - revisar (export datado) | 627 | — |  |
| `lead_campanha_05042024` | COM DADOS, sem ref. estatica - revisar (export datado) | 5432 | — |  |
| `leads_active_campaign` | COM DADOS, sem ref. estatica - revisar | 167998 | — |  |
| `leads_callcenter` | COM DADOS, sem ref. estatica - revisar | 1 | — |  |
| `leads_cbc_c01_jun_2024` | COM DADOS, sem ref. estatica - revisar | 2142 | — |  |
| `leads_cbc_c02_mar_2025` | COM DADOS, sem ref. estatica - revisar | 591 | — |  |
| `leads_cdp_c01_mai_2024` | COM DADOS, sem ref. estatica - revisar | 1356 | — |  |
| `leads_cev_c05_set_2023` | COM DADOS, sem ref. estatica - revisar | 3777 | — |  |
| `leads_cev_c06_set_2023` | COM DADOS, sem ref. estatica - revisar | 5000 | — |  |
| `leads_cev_c07_dez_2023` | COM DADOS, sem ref. estatica - revisar | 3527 | — |  |
| `leads_cev_c08_jan_2024` | COM DADOS, sem ref. estatica - revisar | 4284 | — |  |
| `leads_cev_c09_mar_2024` | COM DADOS, sem ref. estatica - revisar | 3999 | — |  |
| `leads_cev_c10_mai_2024` | COM DADOS, sem ref. estatica - revisar | 3442 | — |  |
| `leads_cev_c11_jul_2024` | COM DADOS, sem ref. estatica - revisar | 6348 | — |  |
| `leads_cev_c12_set_2024` | COM DADOS, sem ref. estatica - revisar | 3374 | — |  |
| `leads_cev_c13_nov_2024` | COM DADOS, sem ref. estatica - revisar | 2487 | — |  |
| `leads_cev_c14_dez_2024` | COM DADOS, sem ref. estatica - revisar | 1787 | — |  |
| `leads_cev_c15_jan_2025` | COM DADOS, sem ref. estatica - revisar | 3028 | — |  |
| `leads_cev_c16_fev_2025` | COM DADOS, sem ref. estatica - revisar | 2085 | — |  |
| `leads_cev_c17_mar_2025` | COM DADOS, sem ref. estatica - revisar | 2098 | — |  |
| `leads_cev_c18_abr_2025` | COM DADOS, sem ref. estatica - revisar | 1047 | — |  |
| `leads_cev_c19_mai_2025` | COM DADOS, sem ref. estatica - revisar | 452 | — |  |
| `leads_cev_c21_jun_2025` | COM DADOS, sem ref. estatica - revisar | 1385 | — |  |
| `leads_cev_f00_2023_mon` | COM DADOS, sem ref. estatica - revisar | 2353 | — |  |
| `leads_cmp_c01_nov_2024` | COM DADOS, sem ref. estatica - revisar | 1176 | — |  |
| `leads_coi_c01_dez_2024` | COM DADOS, sem ref. estatica - revisar | 1015 | — |  |
| `leads_cpm_c01_jul_2024` | COM DADOS, sem ref. estatica - revisar | 974 | — |  |
| `leads_cpt_c01_mar_2024` | COM DADOS, sem ref. estatica - revisar | 2055 | — |  |
| `leads_cpt_c02_out_2024` | COM DADOS, sem ref. estatica - revisar | 1432 | — |  |
| `leads_cxp_c01_abr_2024` | COM DADOS, sem ref. estatica - revisar | 1690 | — |  |
| `leads_cxp_c02_fev_2025` | COM DADOS, sem ref. estatica - revisar | 803 | — |  |
| `leads_ever_webinar` | COM DADOS, sem ref. estatica - revisar | 18532 | — |  |
| `leads_fm5d_c01_out_2024` | COM DADOS, sem ref. estatica - revisar | 1748 | — |  |
| `leads_massage_experience` | COM DADOS, sem ref. estatica - revisar | 388 | — |  |
| `leads_mdo_c01_ago_2024` | COM DADOS, sem ref. estatica - revisar | 2482 | — |  |
| `leads_pm360_c02_out_2023` | COM DADOS, sem ref. estatica - revisar | 3832 | — |  |
| `leads_pm360_c06_abr_2024` | COM DADOS, sem ref. estatica - revisar | 3076 | — |  |
| `leads_pm360_c07_jun_2024` | COM DADOS, sem ref. estatica - revisar | 3403 | — |  |
| `leads_pm360_c08_ago_2024` | COM DADOS, sem ref. estatica - revisar | 3711 | — |  |
| `leads_slicktext` | COM DADOS, sem ref. estatica - revisar | 1305 | — |  |
| `leads_tm10k_c01_fev_2024` | COM DADOS, sem ref. estatica - revisar | 3224 | — |  |
| `leads_validit` | COM DADOS, sem ref. estatica - revisar | 573373 | 2026-06-04 |  |
| `link_reports` | COM DADOS, sem ref. estatica - revisar | 7320 | — |  |
| `list_leads_1x1` | COM DADOS, sem ref. estatica - revisar | 2 | — |  |
| `listas_sms` | COM DADOS, sem ref. estatica - revisar | 38 | — |  |
| `mat_group_health` | COM DADOS, sem ref. estatica - revisar | 31 | — |  |
| `mat_sla_calculations` | COM DADOS, sem ref. estatica - revisar | 5329 | — |  |
| `mat_sla_summary_by_tier` | COM DADOS, sem ref. estatica - revisar | 6 | — |  |
| `mdo_c01_ago_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 8078 | — |  |
| `mdo_c01_ago_2024_leads_sender` | COM DADOS, sem ref. estatica - revisar | 15866 | — |  |
| `mentorias_experience_leads` | COM DADOS, sem ref. estatica - revisar | 3003 | — |  |
| `meta_ad_id_backup` | COM DADOS, sem ref. estatica - revisar (nome "backup") | 1121726 | — |  |
| `meta_ad_id_teste` | COM DADOS, sem ref. estatica - revisar (nome "teste") | 130673 | — |  |
| `nacional_lost_sales` | COM DADOS, sem ref. estatica - revisar | 2352 | — |  |
| `nacional_sales` | COM DADOS, sem ref. estatica - revisar | 423043 | — |  |
| `olp_c01_jul_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 14103 | — |  |
| `oneclickcheckout` | COM DADOS, sem ref. estatica - revisar | 80232 | — |  |
| `orders_tracking` | COM DADOS, sem ref. estatica - revisar | 28099 | 2026-06-04 |  |
| `payt_audit` | COM DADOS, sem ref. estatica - revisar | 3 | — |  |
| `payt_auditoria` | COM DADOS, sem ref. estatica - revisar | 2368 | — |  |
| `pm360_c06_abr_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 3160 | — |  |
| `pm360_c07_jun_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 3890 | — |  |
| `pm360_c08_ago_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 1881 | — |  |
| `pm360_f14_2023_aqs_whatsapp_history` | COM DADOS, sem ref. estatica - revisar | 253 | — |  |
| `pmo_c01_jul_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 17732 | — |  |
| `product_cost_records` | COM DADOS, sem ref. estatica - revisar | 77 | 2026-06-04 |  |
| `produtos_cademi` | COM DADOS, sem ref. estatica - revisar | 353 | — |  |
| `produtos_secoes_cademi` | COM DADOS, sem ref. estatica - revisar | 1001 | — |  |
| `recovery_guru` | COM DADOS, sem ref. estatica - revisar | 3 | — |  |
| `recup_sales_history` | COM DADOS, sem ref. estatica - revisar | 716 | — |  |
| `recup_sales_history2` | COM DADOS, sem ref. estatica - revisar | 155935 | — |  |
| `registros_financeiros` | COM DADOS, sem ref. estatica - revisar | 19059 | — |  |
| `reports_call_center` | COM DADOS, sem ref. estatica - revisar | 143925 | — |  |
| `sales_bound_origens_csv` | COM DADOS, sem ref. estatica - revisar | 294312 | 2026-06-04 |  |
| `sales_bound_sales_csv` | COM DADOS, sem ref. estatica - revisar | 5895 | 2026-06-04 |  |
| `secoes_cademi` | COM DADOS, sem ref. estatica - revisar | 989 | — |  |
| `sex_c01_jun_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 8852 | — |  |
| `sex_toys_whatsapp_history` | COM DADOS, sem ref. estatica - revisar | 1551 | — |  |
| `sku_hub` | COM DADOS, sem ref. estatica - revisar | 203 | — |  |
| `slicktext_events` | COM DADOS, sem ref. estatica - revisar | 161637 | — |  |
| `slicktext_message_metrics` | COM DADOS, sem ref. estatica - revisar | 290 | — |  |
| `slicktext_snapshots` | COM DADOS, sem ref. estatica - revisar | 151 | — |  |
| `slicktext_workflows` | COM DADOS, sem ref. estatica - revisar | 53 | — |  |
| `sms_costs_daily` | COM DADOS, sem ref. estatica - revisar | 9720 | — |  |
| `sms_messages_sends` | COM DADOS, sem ref. estatica - revisar | 235408 | — |  |
| `sms_messages_status` | COM DADOS, sem ref. estatica - revisar | 557380 | — |  |
| `sms_messages_status2` | COM DADOS, sem ref. estatica - revisar (versão "2") | 218842 | — |  |
| `students` | COM DADOS, sem ref. estatica - revisar | 191090 | — |  |
| `students_access` | COM DADOS, sem ref. estatica - revisar | 510069 | — |  |
| `subscriptions_guru` | COM DADOS, sem ref. estatica - revisar | 12100 | — |  |
| `subscriptions_hotmart` | COM DADOS, sem ref. estatica - revisar | 7554 | — |  |
| `subscriptions_nacional_sales` | COM DADOS, sem ref. estatica - revisar | 22649 | — |  |
| `subscriptions_payt` | COM DADOS, sem ref. estatica - revisar | 33417 | — |  |
| `table_size_history` | COM DADOS, sem ref. estatica - revisar | 444 | — |  |
| `tags_active_campaign` | COM DADOS, sem ref. estatica - revisar | 523 | 2026-06-04 |  |
| `tags_active_campaign_c2` | COM DADOS, sem ref. estatica - revisar | 236 | 2026-06-04 |  |
| `tb_gex_gold_buygoods` | COM DADOS, sem ref. estatica - revisar | 208581 | 2026-06-04 |  |
| `temp_account_ids` | COM DADOS, sem ref. estatica - revisar (nome "temp") | 355605 | — |  |
| `temp_aguardando_ship24_chatwoot` | COM DADOS, sem ref. estatica - revisar (nome "temp") | 1 | — |  |
| `temporary_whatsapp_messages1` | COM DADOS, sem ref. estatica - revisar (nome "temporary") | 318 | — |  |
| `temporary_whatsapp_messages2` | COM DADOS, sem ref. estatica - revisar (nome "temporary") | 1825 | — |  |
| `temporary_whatsapp_messages3` | COM DADOS, sem ref. estatica - revisar (nome "temporary") | 151 | — |  |
| `teste_ad_id` | COM DADOS, sem ref. estatica - revisar (nome "teste") | 478 | — |  |
| `tracking_events` | COM DADOS, sem ref. estatica - revisar | 3966 | — |  |
| `transacoes_refund` | COM DADOS, sem ref. estatica - revisar | 337 | — |  |
| `ult_c02_mai_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 8873 | — |  |
| `ult_c03_jan_2025_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 7131 | — |  |
| `webinar_experience_leads` | COM DADOS, sem ref. estatica - revisar | 3133 | — |  |
| `webinar_experience_leads10` | COM DADOS, sem ref. estatica - revisar | 1528 | — |  |
| `webinar_experience_leads_perpetuo` | COM DADOS, sem ref. estatica - revisar | 1607 | — |  |
| `whatsapp_history` | COM DADOS, sem ref. estatica - revisar | 138413 | — |  |
| `whatsapp_messages` | COM DADOS, sem ref. estatica - revisar | 3172 | — |  |
| `whatsapp_messages_history` | COM DADOS, sem ref. estatica - revisar | 27253 | — |  |
| `whatsapp_messages_status` | COM DADOS, sem ref. estatica - revisar | 43744 | — |  |
| `whatsapp_reponses` | COM DADOS, sem ref. estatica - revisar | 34915 | — |  |
| `ylg_c03_set_2024_leads_oneclick` | COM DADOS, sem ref. estatica - revisar | 21720 | — |  |

## ✅ Em uso (referenciada por proc/event/view) — **manter** (inclui 5 vazias-referenciadas a investigar)
| Tabela | Análise | Linhas | Atualizada | Excluir? |
|---|---|--:|---|---|
| `buygoods_internal_affiliates` | EM USO (referenciada) - manter | 22 | 2026-06-04 |  |
| `buygoods_physical` | EM USO (referenciada) - manter | 9833 | 2026-05-28 |  |
| `buygoods_products` | EM USO (referenciada) - manter | 2246 | 2026-06-04 |  |
| `call_center_sales` | EM USO (referenciada) - manter | 6893 | 2026-06-04 |  |
| `cartpanda_physical` | EM USO (referenciada) - manter | 512636 | — |  |
| `cb_tickets` | EM USO (referenciada) - manter | 70712 | 2026-06-04 |  |
| `clickbank_internal_affiliates` | EM USO (referenciada) - manter | 22 | 2026-06-04 |  |
| `clickbank_physical` | EM USO (referenciada) - manter | 52 | — |  |
| `clickbank_physical_new_aws` | EM USO (referenciada) - manter | 328275 | 2026-06-04 |  |
| `clickbank_products` | EM USO (referenciada) - manter | 2815 | 2026-06-04 |  |
| `creative_tasks` | EM USO (referenciada) - manter | 32485 | 2026-06-04 |  |
| `custos_conta_agencia` | EM USO (referenciada) - manter | 43 | 2026-06-04 |  |
| `custos_conta_agencia_diaria` | EM USO (referenciada) - manter | 280 | 2026-06-04 |  |
| `custos_gerais` | EM USO (referenciada) - manter | 6 | 2026-06-04 |  |
| `custos_gerais_diaria` | EM USO (referenciada) - manter | 150 | 2026-06-04 |  |
| `custos_trafego_gestores` | EM USO (referenciada) - manter | 52 | 2026-06-04 |  |
| `custos_trafego_gestores_diaria` | EM USO (referenciada) - manter | 294 | 2026-06-04 |  |
| `cw_activities_mat` | EM USO (referenciada) - manter | 2412270 | 2026-06-04 |  |
| `cw_conversations_mat` | EM USO (referenciada) - manter | 475087 | 2026-06-04 |  |
| `cw_messages_mat` | EM USO (referenciada) - manter | 4507641 | 2026-06-04 |  |
| `cw_refund_classifier` | EM USO (referenciada) - manter | 23401 | 2026-06-04 |  |
| `cw_team_members_mat` | EM USO (referenciada) - manter | 17 | — |  |
| `cw_teams_mat` | EM USO (referenciada) - manter | 6 | — |  |
| `cw_users_mat` | EM USO (referenciada) - manter | 104 | 2026-06-04 |  |
| `dashboard_affiliate_nutra` | EM USO (referenciada) - manter | 79755 | 2026-06-04 |  |
| `dashboard_affiliate_nutra_usd` | EM USO (referenciada) - manter | 79497 | 2026-06-04 |  |
| `dashboard_anomalia_diaria` | EM USO (referenciada) - manter | 335878 | 2026-06-04 |  |
| `dashboard_atendimento` | EM USO (referenciada) - manter | 537203 | 2026-06-04 |  |
| `dashboard_atendimento_backlog` | EM USO (referenciada) - manter | 9520 | 2026-06-04 |  |
| `dashboard_atendimento_retornos` | EM USO (referenciada) - manter | 903 | 2026-06-04 |  |
| `dashboard_auditoria_leads` | EM USO (referenciada) - manter | 2158501 | 2026-06-04 |  |
| `dashboard_channels_country_daily` | EM USO (referenciada) - manter | 8192 | 2026-06-04 |  |
| `dashboard_channels_marketing` | EM USO (referenciada) - manter | 78892 | 2026-06-04 |  |
| `dashboard_dim_funil` | EM USO (referenciada) - manter | 39 | 2026-06-04 |  |
| `dashboard_dim_gestor` | EM USO (referenciada) - manter | 12 | 2026-06-04 |  |
| `dashboard_dim_product` | EM USO (referenciada) - manter | 120 | 2026-06-04 |  |
| `dashboard_dim_source` | EM USO (referenciada) - manter | 10 | 2026-06-04 |  |
| `dashboard_email_marketing` | EM USO (referenciada) - manter | 20224 | — |  |
| `dashboard_gold_buygoods` | EM USO (referenciada) - manter | 200762 | 2026-06-04 |  |
| `dashboard_gold_clickbank` | EM USO (referenciada) - manter | 183821 | 2026-06-04 |  |
| `dashboard_gold_clickbank_buygoods` | EM USO (referenciada) - manter | 420495 | 2026-06-04 |  |
| `dashboard_internal_sales` | EM USO (referenciada) - manter | 3665 | — |  |
| `dashboard_internal_sales_v2` | EM USO (referenciada) - manter | 1497 | 2026-06-04 |  |
| `dashboard_janela_recup` | EM USO (referenciada) - manter | 15542 | — |  |
| `dashboard_lead_events` | EM USO (referenciada) - manter | 5298 | 2026-06-04 |  |
| `dashboard_leads_alerts` | EM USO (referenciada) - manter | 162159 | 2026-06-04 |  |
| `dashboard_leads_por_dia` | EM USO (referenciada) - manter | 155 | 2026-06-04 |  |
| `dashboard_low_end` | EM USO (referenciada) - manter | 7478 | 2026-06-04 |  |
| `dashboard_ranking_agentes` | EM USO (referenciada) - manter | 16453 | 2026-06-04 |  |
| `dashboard_reembolso` | EM USO (referenciada) - manter | 333406 | 2026-06-04 |  |
| `dashboard_reembolso_coortes` | EM USO (referenciada) - manter | 51 | 2026-06-04 |  |
| `dashboard_sla_times` | EM USO (referenciada) - manter | 546792 | 2026-06-04 |  |
| `dashboard_sms_marketing` | EM USO (referenciada) - manter | 20523 | — |  |
| `digistore_physical` | EM USO (referenciada) - manter | 2260 | 2026-06-04 |  |
| `dim_copywriter` | EM USO (referenciada) - manter | 74 | — |  |
| `dim_squad` | EM USO (referenciada) - manter | 18 | — |  |
| `exchange_rates` | EM USO (referenciada) - manter | 722 | 2026-06-04 |  |
| `funil_produto_mapping` | EM USO (referenciada) - manter | 59 | 2026-06-04 |  |
| `general_costs` | VAZIA mas referenciada - manter/investigar | 0 | — |  |
| `general_sales` | EM USO (referenciada) - manter | 1287 | 2026-06-04 |  |
| `gerenciador_meta_ads` | EM USO (referenciada) - manter | 2230066 | — |  |
| `gerenciador_meta_ads_v2` | EM USO (referenciada) - manter | 3259691 | 2026-06-04 |  |
| `gerenciador_meta_consolidado_v2` | EM USO (referenciada) - manter | 969730 | 2026-06-04 |  |
| `gerenciador_meta_vendas` | EM USO (referenciada) - manter | 10692 | — |  |
| `gerenciador_meta_vendas_v2` | EM USO (referenciada) - manter | 19140 | 2026-06-04 |  |
| `google_ad_id` | EM USO (referenciada) - manter | 24210 | 2026-06-04 |  |
| `gross_recovery_target` | EM USO (referenciada) - manter | 36 | — |  |
| `guru_info` | EM USO (referenciada) - manter | 17515 | 2026-06-04 |  |
| `guru_physical` | EM USO (referenciada) - manter | 862 | — |  |
| `hotmart_info` | EM USO (referenciada) - manter | 39456 | — |  |
| `internal_funnel_v2` | EM USO (referenciada) - manter | 25518 | 2026-06-04 |  |
| `internal_gerenciador_meta` | EM USO (referenciada) - manter | 8015 | — |  |
| `internal_product_v2` | EM USO (referenciada) - manter | 34546 | 2026-06-04 |  |
| `internal_sales_mat` | EM USO (referenciada) - manter | 2290790 | — |  |
| `internal_sales_refresh_log` | EM USO (referenciada) - manter | 23643 | — |  |
| `linha_receita_records` | EM USO (referenciada) - manter | 154 | 2026-06-04 |  |
| `mat_daily_overview` | EM USO (referenciada) - manter | 249 | — |  |
| `mat_daily_overview_by_tier` | VAZIA mas referenciada - manter/investigar | 0 | — |  |
| `mat_mention_tracking` | EM USO (referenciada) - manter | 1378 | — |  |
| `mat_messages_enriched` | EM USO (referenciada) - manter | 10990 | — |  |
| `mat_team_performance` | EM USO (referenciada) - manter | 12 | — |  |
| `mat_team_performance_daily` | VAZIA mas referenciada - manter/investigar | 0 | — |  |
| `meta_ad_id` | EM USO (referenciada) - manter | 4274860 | 2026-06-04 |  |
| `nps_affiliate_groups` | EM USO (referenciada) - manter | 167 | — |  |
| `numbers_recovered` | EM USO (referenciada) - manter | 1382 | — |  |
| `orders` | VAZIA mas referenciada - manter/investigar | 0 | — |  |
| `payt_info` | EM USO (referenciada) - manter | 95654 | — |  |
| `payt_physical` | EM USO (referenciada) - manter | 5641 | — |  |
| `products` | VAZIA mas referenciada - manter/investigar | 0 | — |  |
| `sms_costs` | EM USO (referenciada) - manter | 730 | — |  |
| `taboola_ad_id` | EM USO (referenciada) - manter | 2630 | 2026-06-04 |  |
| `tb_gex_buygoods_unified` | EM USO (referenciada) - manter | 327852 | 2026-06-04 |  |
| `telegram_groups_backup` | EM USO (referenciada) - manter | 11820 | — |  |
| `telegram_groups_metadata` | EM USO (referenciada) - manter | 878 | — |  |
| `telegram_team_members` | EM USO (referenciada) - manter | 12 | — |  |
| `unified_lead_events_new_backup_1` | EM USO (referenciada) - manter (nome "backup") | 1352143 | — |  |
| `unified_lead_events_v2` | EM USO (referenciada) - manter | 103779 | — |  |

## 🔁 Swap atômico — **NUNCA excluir** (transitórias do refresh; vazias = normal)
| Tabela | Análise | Linhas | Atualizada | Excluir? |
|---|---|--:|---|---|
| `buygoods_new` | SWAP atomico - NAO excluir | 3638 | — | — |
| `buygoods_physical_new` | SWAP atomico - NAO excluir | 0 | — | — |
| `buygoods_silver_orders_old` | SWAP atomico - NAO excluir | 0 | — | — |
| `buygoods_silver_orders_v2_old` | SWAP atomico - NAO excluir | 0 | — | — |
| `clickbank_physical_new` | SWAP atomico - NAO excluir | 308194 | 2026-06-04 | — |
| `clickbank_physical_new_aws_new` | SWAP atomico - NAO excluir | 0 | — | — |
| `clickbank_physical_old` | SWAP atomico - NAO excluir | 182438 | — | — |
| `custos_conta_agencia_diaria_stage` | SWAP atomico - NAO excluir | 280 | 2026-06-04 | — |
| `custos_gerais_diaria_stage` | SWAP atomico - NAO excluir | 150 | 2026-06-04 | — |
| `custos_trafego_gestores_diaria_stage` | SWAP atomico - NAO excluir | 294 | 2026-06-04 | — |
| `dashboard_affiliate_nutra_stage` | SWAP atomico - NAO excluir | 80082 | 2026-06-04 | — |
| `dashboard_affiliate_nutra_usd_stage` | SWAP atomico - NAO excluir | 79587 | 2026-06-04 | — |
| `dashboard_anomalia_diaria_stage` | SWAP atomico - NAO excluir | 335091 | 2026-06-04 | — |
| `dashboard_atendimento_backlog_stage` | SWAP atomico - NAO excluir | 9764 | 2026-06-04 | — |
| `dashboard_atendimento_retornos_stage` | SWAP atomico - NAO excluir | 903 | 2026-06-04 | — |
| `dashboard_atendimento_stage` | SWAP atomico - NAO excluir | 532941 | 2026-06-04 | — |
| `dashboard_auditoria_leads_stage` | SWAP atomico - NAO excluir | 2123508 | 2026-06-04 | — |
| `dashboard_cartpanda_country_daily_stage` | SWAP atomico - NAO excluir | 5849 | — | — |
| `dashboard_channels_country_daily_stage` | SWAP atomico - NAO excluir | 8360 | 2026-06-04 | — |
| `dashboard_channels_marketing_aws_new` | SWAP atomico - NAO excluir | 0 | — | — |
| `dashboard_channels_marketing_stage` | SWAP atomico - NAO excluir | 78600 | 2026-06-04 | — |
| `dashboard_gold_buygoods_stage` | SWAP atomico - NAO excluir | 0 | — | — |
| `dashboard_gold_clickbank_buygoods_stage` | SWAP atomico - NAO excluir | 387631 | 2026-06-04 | — |
| `dashboard_gold_clickbank_stage` | SWAP atomico - NAO excluir | 185987 | 2026-06-04 | — |
| `dashboard_gold_clickbank_stage_new` | SWAP atomico - NAO excluir | 0 | — | — |
| `dashboard_internal_sales_v2_stage` | SWAP atomico - NAO excluir | 1497 | 2026-06-04 | — |
| `dashboard_janela_recup_stage` | SWAP atomico - NAO excluir | 15640 | — | — |
| `dashboard_lead_events_stage` | SWAP atomico - NAO excluir | 5298 | 2026-06-04 | — |
| `dashboard_leads_alerts_stage` | SWAP atomico - NAO excluir | 161294 | 2026-06-04 | — |
| `dashboard_ranking_agentes_stage` | SWAP atomico - NAO excluir | 16124 | 2026-06-04 | — |
| `dashboard_reembolso_coortes_stage` | SWAP atomico - NAO excluir | 51 | 2026-06-04 | — |
| `dashboard_reembolso_stage` | SWAP atomico - NAO excluir | 348155 | 2026-06-04 | — |
| `dashboard_sla_times_stage` | SWAP atomico - NAO excluir | 539926 | 2026-06-04 | — |
| `dashboard_sms_marketing_v2_stage` | SWAP atomico - NAO excluir | 0 | — | — |
| `gerenciador_meta_ads_v2_stage` | SWAP atomico - NAO excluir | 3219776 | 2026-06-04 | — |
| `gerenciador_meta_consolidado_v2_stage` | SWAP atomico - NAO excluir | 958732 | 2026-06-04 | — |
| `gerenciador_meta_vendas_v2_stage` | SWAP atomico - NAO excluir | 18931 | 2026-06-04 | — |
| `gold_clickbank_aws_new` | SWAP atomico - NAO excluir | 0 | — | — |
| `internal_funnel_v2_stage` | SWAP atomico - NAO excluir | 25446 | 2026-06-04 | — |
| `internal_product_v2_stage` | SWAP atomico - NAO excluir | 34661 | 2026-06-04 | — |
| `tb_gex_buygoods_physical_new` | SWAP atomico - NAO excluir | 295337 | 2026-06-04 | — |
| `tb_gex_buygoods_physical_new_old` | SWAP atomico - NAO excluir | 0 | — | — |
| `unified_lead_events_new` | SWAP atomico - NAO excluir | 1415554 | 2026-06-04 | — |

---
## Relacionados
[[Regras de Exclusão]] · [[migracao-data_team-mapa]] · [[00-Indice]]
