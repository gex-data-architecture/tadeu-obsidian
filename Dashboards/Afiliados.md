---
tipo: dashboard
dono: # ⚠️ a confirmar
looker_url: https://datastudio.google.com/u/0/reporting/4ae59aa8-c488-493e-8985-1c7ac700c81b
report_id: 4ae59aa8-c488-493e-8985-1c7ac700c81b
status: rascunho
tags: [dashboard]
---
# 📊 Afiliados

> ⚠️ **Rascunho** — fontes inferidas (alta confiança pelo nome). A confirmar abrindo o relatório.

- **Link:** [Afiliados](https://datastudio.google.com/u/0/reporting/4ae59aa8-c488-493e-8985-1c7ac700c81b/page/p_wl8e7pt2wd)
- **Dono / área:** ⚠️ a confirmar (provável Afiliados / Parcerias)

## Fontes de dados (tabelas que alimentam) — ⚠️ inferido (alta confiança)
- [[dashboard_affiliate_nutra]] — afiliados nutra (BRL). 🔜 `tb_mart_affiliate_nutra`
- [[dashboard_affiliate_nutra_usd]] — afiliados nutra (USD). 🔜 `tb_mart_affiliate_nutra_usd`
  - ambas derivam de [[dashboard_gold_clickbank_buygoods]]
- Lookups possíveis: [[clickbank_internal_affiliates]] / [[buygoods_internal_affiliates]] 🔜 `tb_dim_clickbank_affiliate` / `tb_dim_buygoods_affiliate`

## Atualização (como os dados são gerados)
- Procedures: [[refresh_dashboard_affiliate_nutra]] · [[refresh_dashboard_affiliate_nutra_usd]] (fecho via [[sp_master_run_all]]).
- Agenda do refresh: ⚠️ a confirmar.

## Páginas / abas e métricas — ⚠️ a preencher (browser)
- Página principal: `p_wl8e7pt2wd`
- _(listar abas e principais métricas/gráficos)_

## Observações / pegadinhas — ⚠️ a confirmar
- Tem versão **BRL** e **USD** — checar se o dashboard alterna moeda por página/filtro.
- Fuso / filtros padrão: _(a verificar)_

## Relacionados
[[Dashboards/_sobre]] · [[migracao-data_team-mapa]]
