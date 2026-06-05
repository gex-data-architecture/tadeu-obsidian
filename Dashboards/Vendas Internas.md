---
tipo: dashboard
dono: # ⚠️ a confirmar
looker_url: https://datastudio.google.com/u/0/reporting/7e6392c3-3e11-49b7-b731-0dd4b9b06f79
report_id: 7e6392c3-3e11-49b7-b731-0dd4b9b06f79
status: rascunho
tags: [dashboard]
---
# 📊 Vendas Internas

> ⚠️ **Rascunho** — fontes inferidas (alta confiança pelo nome). A confirmar abrindo o relatório.

- **Link:** [Vendas Internas](https://datastudio.google.com/u/0/reporting/7e6392c3-3e11-49b7-b731-0dd4b9b06f79/page/p_0gwv7tuz0d/edit)
- **Dono / área:** ⚠️ a confirmar (provável Vendas / Comercial interno)

## Fontes de dados (tabelas que alimentam) — ⚠️ inferido (alta confiança)
- [[dashboard_internal_sales_v2]] — vendas internas. 🔜 `tb_mart_internal_sales`
- [[internal_product_v2]] — produto. 🔜 `tb_mart_internal_product`
- [[internal_funnel_v2]] — funil. 🔜 `tb_mart_internal_funnel`
  - todas derivam de [[dashboard_gold_clickbank_buygoods]] (+ custos `_daily`)
- Dimensões: [[dashboard_dim_product]] · [[dashboard_dim_funil]] · [[dim_squad]] · [[dim_copywriter]]

## Atualização (como os dados são gerados)
- Procedures: [[refresh_dashboard_internal_sales_v2]] · [[refresh_internal_product_v2]] · [[refresh_internal_funnel_v2]] (fecho via [[sp_master_run_all]]).
- Agenda do refresh: ⚠️ a confirmar.

## Páginas / abas e métricas — ⚠️ a preencher (browser)
- Página principal: `p_0gwv7tuz0d`
- _(listar abas e principais métricas/gráficos)_

## Observações / pegadinhas — ⚠️ a confirmar
- Usa custos diários ([[custos_trafego_gestores_diaria]], [[custos_conta_agencia_diaria]], [[custos_gerais_diaria]]) — checar dependência.
- Fuso / moeda / filtros padrão: _(a verificar)_

## 🔗 Planilhas relacionadas
> Planilhas que alimentam ou compõem este dashboard. Para cada uma: o que contém, quem mantém,
> frequência de atualização e qual tabela/parte do dash ela alimenta. Fonte: `Operação/Planilhas/`.
- _(⚠️ a preencher)_

## 🔁 Fluxos N8N relacionados
> Automações n8n ligadas a este dashboard (ingestão, sync, alertas). Para cada fluxo: gatilho,
> o que faz e o que escreve (tabela destino). Fonte: `Operação/N8N/`.
- _(⚠️ a preencher)_

## Relacionados
[[Dashboards/_sobre]] · [[migracao-data_team-mapa]]
