---
tipo: moc
tags: [moc, conhecimento, fluxo-n8n]
---
# N8N — Fluxos

> Documentação das automações no n8n (ingestão/consumo). Use o template **`fluxo-n8n`**.
> Linke as tabelas/procedures que o fluxo toca com [[...]].

## Páginas

### Instância `psyche` (`psyche.work.institutoexperience.com`)
| Fluxo | Gatilho | Escreve em | Dashboard |
|---|---|---|---|
| [[Chatwoot - Postgres-MySQL (Reembolso)]] | schedule 15 min | `cw_*_mat` | [[Dashboards/Reembolso e Atendimento]] |
| [[Custos Tráfego Gestores]] | schedule 4h/1h | `custos_*` | [[Dashboards/Vendas Internas]] |
| [[Dimensões Copys e Squads]] | webhook | `dim_squad`/`dim_copywriter` | [[Dashboards/Vendas Internas]] |
| [[SMS e E-mail - Metas]] | webhook | `gross_recovery_target` | [[Dashboards/SMS Marketing]] · [[Dashboards/E-mail Marketing]] |
| [[Operação/N8N/Custos SMS, E-mail e Whats\|Custos SMS, E-mail e Whats]] | webhook | `sms_costs` | [[Dashboards/SMS Marketing]] · [[Dashboards/E-mail Marketing]] |

### Instância `pneuma` (`pneuma.work.institutoexperience.com`)
| Fluxo | Gatilho | Escreve em | Dashboard |
|---|---|---|---|
| [[BuyGoods - Identificador de Ofertas]] | schedule 1h | `buygoods_products` | foundational · [[Dashboards/Afiliados]] |
| [[ClickBank - Identificador Tráfego Interno]] | schedule 12h | `clickbank_internal_affiliates` | [[Dashboards/Vendas Internas]] |

> ⚠️ Status "ativo" de cada fluxo é a confirmar na UI do n8n. Conteúdo das planilhas: ver `Operação/Planilhas/`.
