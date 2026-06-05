---
tipo: indice
tags: [moc, dashboards]
---
# 📊 Dashboards — Looker Studio

> Pasta **curada**: documentação dos dashboards do time no **Looker Studio**.
> Os scripts de geração nunca tocam aqui.

## O que documentar em cada dashboard
- **Link** do relatório no Looker Studio + dono/área.
- **Fonte(s) de dados**: quais tabelas finais alimentam (linke com `[[wikilinks]]`,
  ex.: `[[dashboard_gold_clickbank_buygoods]]`, e futuramente as cópias no `data_team`).
- **Atualização**: qual evento/procedure gera os dados e em que agenda.
- **Páginas/abas** e principais métricas.
- **Observações / pegadinhas** (filtros padrão, fuso, moeda).
- **Planilhas relacionadas**: planilhas (Sheets/Excel) que alimentam o dash → `Operação/Planilhas/`.
- **Fluxos N8N relacionados**: automações n8n que alimentam o dash → `Operação/N8N/`.

## Convenção
- Uma nota por dashboard. Nome do arquivo = nome do dashboard.
- Frontmatter sugerido: `tipo: dashboard`, `dono:`, `looker_url:`, `tags: [dashboard]`.

## Dashboards documentados
> ⚠️ Notas em **rascunho** (estrutura + fontes inferidas pela linhagem). Páginas/métricas/dono e
> as **fontes exatas** ficam pendentes de abrir cada relatório no Looker Studio.

| Dashboard | Fontes principais (inferidas) | 🔜 no `data_team` |
|---|---|---|
| [[SMS Marketing]] | [[dashboard_channels_marketing]] · [[sms_costs]] | `tb_mart_marketing_channels` |
| [[E-mail Marketing]] | [[dashboard_channels_marketing]] (+ fonte e-mail externa?) | `tb_mart_marketing_channels` |
| [[Auditoria de Leads]] | [[dashboard_auditoria_leads]] | `tb_mart_leads_audit` |
| [[Afiliados]] | [[dashboard_affiliate_nutra]] · [[dashboard_affiliate_nutra_usd]] | `tb_mart_affiliate_nutra` / `_usd` |
| [[Vendas Internas]] | [[dashboard_internal_sales_v2]] · [[internal_product_v2]] · [[internal_funnel_v2]] | `tb_mart_internal_*` |
| [[Reembolso e Atendimento]] | [[dashboard_reembolso]] · [[dashboard_atendimento]] · [[dashboard_sla_times]] (+5) | `tb_gold_refund*` / `tb_gold_support*` / `tb_mart_support_*` |
