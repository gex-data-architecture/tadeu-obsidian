---
tipo: dashboard
dono: # ⚠️ a confirmar
looker_url: https://datastudio.google.com/u/0/reporting/172fe214-bd04-404f-a448-50c4970ca033
report_id: 172fe214-bd04-404f-a448-50c4970ca033
status: rascunho
tags: [dashboard]
---
# 📊 SMS Marketing

> ⚠️ **Rascunho** — estrutura montada com **fontes inferidas** pela linhagem da migração.
> A confirmar abrindo o relatório (páginas, métricas, dono, fontes exatas em *Recurso → Gerenciar fontes de dados*).

- **Link:** [SMS Marketing](https://datastudio.google.com/u/0/reporting/172fe214-bd04-404f-a448-50c4970ca033/page/p_51joc3x70d/edit)
- **Dono / área:** ⚠️ a confirmar (provável Marketing)

## Fontes de dados (tabelas que alimentam) — ⚠️ inferido
- [[dashboard_channels_marketing]] — canais de marketing (deriva de `gold_clickbank_buygoods`); `sms_costs` entra aqui.
  - 🔜 no `data_team`: `tb_mart_marketing_channels`
- [[dashboard_channels_country_daily]] *(possível)* — recorte país/dia. 🔜 `tb_mart_marketing_channels_country_daily`
- Custo de SMS na origem: [[sms_costs]] (bronze) → 🔜 `tb_bronze_sms_costs`

## Atualização (como os dados são gerados)
- Procedure: [[refresh_dashboard_channels_marketing]] (roda no fecho via [[sp_master_run_all]]).
- Custo SMS ingerido pelo Glue `mysql-to-bronze sms_costs` (agenda `gex-mysql-sms-costs-timer-prod`, ~05:15 UTC).
- Agenda do refresh: ⚠️ a confirmar (qual evento ativo dispara).

## Páginas / abas e métricas — ⚠️ a preencher (browser)
- Página principal: `p_51joc3x70d`
- _(listar abas e principais métricas/gráficos)_

## Observações / pegadinhas — ⚠️ a confirmar
- Fuso / moeda dos números: _(a verificar)_
- Filtros padrão: _(a verificar)_

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
