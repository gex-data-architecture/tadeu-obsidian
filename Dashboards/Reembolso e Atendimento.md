---
tipo: dashboard
dono: # ⚠️ a confirmar
looker_url: https://datastudio.google.com/u/0/reporting/d14fa7d9-5eb9-4aff-8f8a-d5ff996ea6ec
report_id: d14fa7d9-5eb9-4aff-8f8a-d5ff996ea6ec
status: rascunho
tags: [dashboard]
---
# 📊 Reembolso e Atendimento

> ⚠️ **Rascunho** — fontes inferidas (alta confiança pelo nome). A confirmar abrindo o relatório.

- **Link:** [Reembolso e Atendimento](https://datastudio.google.com/u/0/reporting/d14fa7d9-5eb9-4aff-8f8a-d5ff996ea6ec/page/p_hb7rlut6yd/edit)
- **Dono / área:** ⚠️ a confirmar (provável Atendimento / CS)

## Fontes de dados (tabelas que alimentam) — ⚠️ inferido (alta confiança)
**Reembolso (refund):**
- [[dashboard_reembolso]] 🔜 `tb_gold_refund`
- [[dashboard_reembolso_coortes]] 🔜 `tb_gold_refund_cohorts`

**Atendimento (support):**
- [[dashboard_atendimento]] 🔜 `tb_gold_support`
- [[dashboard_sla_times]] 🔜 `tb_gold_support_sla`
- [[dashboard_atendimento_retornos]] 🔜 `tb_gold_support_returns`
- [[dashboard_atendimento_backlog]] 🔜 `tb_mart_support_backlog`
- [[dashboard_ranking_agentes]] 🔜 `tb_mart_support_agent_ranking`

> Origem dos dados de atendimento = tabelas Chatwoot `cw_*` ([[cw_messages_mat]], [[cw_conversations_mat]], [[cw_activities_mat]]…) 🔜 `tb_bronze_chatwoot_*`.
> Reembolso lê de [[cb_tickets]] / [[clickbank_physical_new]] e [[cw_refund_classifier]].

## Atualização (como os dados são gerados)
- Procedures: [[refresh_dashboard_reembolso]] · [[refresh_dashboard_reembolso_coortes]] · [[refresh_dashboard_atendimento]] · [[refresh_dashboard_sla_times]] · [[refresh_dashboard_atendimento_retornos]] · [[refresh_dashboard_atendimento_backlog]] · [[refresh_dashboard_ranking_agentes]] (fecho via [[sp_master_run_all]]).
- Agenda do refresh: ⚠️ a confirmar.

## Páginas / abas e métricas — ⚠️ a preencher (browser)
- Página principal: `p_hb7rlut6yd`
- _(listar abas — provável separação Reembolso × Atendimento — e principais métricas)_

## Observações / pegadinhas — ⚠️ a confirmar
- Dashboard "guarda-chuva": junta dois domínios (refund + support). Confirmar separação por aba.
- Fuso / moeda / filtros padrão: _(a verificar)_

## Relacionados
[[Dashboards/_sobre]] · [[migracao-data_team-mapa]]
