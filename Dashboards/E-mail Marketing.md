---
tipo: dashboard
dono: # ⚠️ a confirmar
looker_url: https://datastudio.google.com/u/0/reporting/dcaa9045-5723-4373-a758-2a31f44aecab
report_id: dcaa9045-5723-4373-a758-2a31f44aecab
status: rascunho
tags: [dashboard]
---
# 📊 E-mail Marketing

> ⚠️ **Rascunho** — estrutura montada com **fontes inferidas** pela linhagem da migração.
> A confirmar abrindo o relatório (páginas, métricas, dono, fontes exatas em *Recurso → Gerenciar fontes de dados*).

- **Link:** [E-mail Marketing](https://datastudio.google.com/u/0/reporting/dcaa9045-5723-4373-a758-2a31f44aecab/page/p_hb7rlut6yd)
- **Dono / área:** ⚠️ a confirmar (provável Marketing)

## Fontes de dados (tabelas que alimentam) — ⚠️ inferido
- [[dashboard_channels_marketing]] — canais de marketing (canal e-mail é um recorte). 🔜 `tb_mart_marketing_channels`
- [[dashboard_channels_country_daily]] *(possível)* — recorte país/dia. 🔜 `tb_mart_marketing_channels_country_daily`
- ⚠️ Pode usar fonte de e-mail própria (ex.: provedor de e-mail / leads) **fora** das tabelas do fecho — confirmar.

## Atualização (como os dados são gerados)
- Procedure: [[refresh_dashboard_channels_marketing]] (fecho via [[sp_master_run_all]]).
- Agenda do refresh: ⚠️ a confirmar.

## Páginas / abas e métricas — ⚠️ a preencher (browser)
- Página principal: `p_hb7rlut6yd`
- _(listar abas e principais métricas/gráficos)_

## Observações / pegadinhas — ⚠️ a confirmar
- Fonte de dados de e-mail pode ser externa (não-MySQL) — verificar em *Gerenciar fontes de dados*.
- Fuso / moeda / filtros padrão: _(a verificar)_

## 🔗 Planilhas relacionadas
> Planilhas que alimentam ou compõem este dashboard. Para cada uma: o que contém, quem mantém,
> frequência de atualização e qual tabela/parte do dash ela alimenta. Fonte: `Operação/Planilhas/`.
- [[Metas de Monetização e Recuperação]] → metas mensais (inclui E-mail) → [[gross_recovery_target]]
- [[Operação/Planilhas/Custos SMS, E-mail e Whats|Custos SMS, E-mail e Whats (planilha)]] → custos de e-mail (recup/monet) → [[sms_costs]]

## 🔁 Fluxos N8N relacionados
> Automações n8n ligadas a este dashboard (ingestão, sync, alertas). Para cada fluxo: gatilho,
> o que faz e o que escreve (tabela destino). Fonte: `Operação/N8N/`.
- [[SMS e E-mail - Metas]] — webhook → escreve `gross_recovery_target` (metas de e-mail)
- [[Operação/N8N/Custos SMS, E-mail e Whats|Custos SMS, E-mail e Whats (fluxo)]] — webhook → escreve `sms_costs` (colunas `email_*`)

## Relacionados
[[Dashboards/_sobre]] · [[migracao-data_team-mapa]]
