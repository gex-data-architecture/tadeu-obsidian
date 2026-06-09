---
tipo: moc
tags: [moc, planilha-manual]
---
# Planilhas

> Registro das **planilhas mantidas à mão** (Google Sheets / Excel) que alimentam
> ou complementam os dados — fontes que NÃO vêm do banco automaticamente.

> Para cada planilha, documente: dono, onde mora (link), frequência de atualização,
> quem preenche, e para onde os dados vão (qual tabela/pipeline consome).
> São pontos frágeis do pipeline — vale marcar pegadinhas e riscos.

## Páginas
| Planilha | Consumida pelo fluxo | Vai para (tabela) | Dashboard |
|---|---|---|---|
| [[Custos de Tráfego Pago]] | [[Custos Tráfego Gestores]] | `custos_*` | [[Dashboards/Vendas Internas]] |
| [[Squads e Copywriters]] | [[Dimensões Copys e Squads]] | `dim_squad`/`dim_copywriter` | [[Dashboards/Vendas Internas]] |
| [[Metas de Monetização e Recuperação]] | [[SMS e E-mail - Metas]] | `gross_recovery_target` | [[Dashboards/SMS Marketing]] · [[Dashboards/E-mail Marketing]] |
| [[Operação/Planilhas/Custos SMS, E-mail e Whats\|Custos SMS, E-mail e Whats]] | [[Operação/N8N/Custos SMS, E-mail e Whats\|fluxo Custos SMS]] | `sms_costs` | [[Dashboards/SMS Marketing]] · [[Dashboards/E-mail Marketing]] |
| [[BuyGoods - Offers e Vendors]] | [[BuyGoods - Identificador de Ofertas]] | `buygoods_products` | [[Dashboards/Afiliados]] |
| [[ClickBank - Tráfego Interno]] | [[ClickBank - Identificador Tráfego Interno]] | `clickbank_internal_affiliates` | [[Dashboards/Vendas Internas]] |

> ⚠️ Dono, frequência e **conteúdo (abas/colunas)** de cada planilha = a documentar na 2ª passada
> (via MCP do Google Sheets). Estas são fontes mantidas à mão → pontos frágeis do pipeline.
