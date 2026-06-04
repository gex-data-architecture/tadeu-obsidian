---
tipo: fonte
plataforma: Buygoods
status: ativa
tags: [fonte, "fonte/buygoods"]
---
# Buygoods

> Fonte principal (integração recente). Arquitetura: **webhook / API → silver → gold**.

## 📎 Documentação (Markdown nativo)
> Tudo convertido para `.md` (versionável no GitHub, pesquisável no Obsidian).
> Os arquivos crus (`.csv`, `.docx`) ficam na pasta como backup — só aparecem no explorador
> com **Settings → Files and links → "Detect all file extensions"** ligado.

| Nota `.md` | O que é | Cru |
|---|---|---|
| [[doc_silver_buygoods]] | Especificação técnica da camada **silver** — regras de unificação das 2 silvers (webhook = fonte da verdade, API = complemento) → `[[tb_gex_buygoods_unified]]` | — |
| [[doc_gold_buygoods]] | Especificação técnica da camada **gold** (75 colunas, agrupamento por janela de 240min) → `[[dashboard_gold_buygoods]]` | `doc_gold_buygoods.docx` |
| [[amostra_webhook_buygoods]] | Referência da amostra do **webhook** (92 colunas, action_type: neworder/newcustomer/cancel/refund/abandon) | `amostra_webhook_buygoods.csv` |
| [[amostra_api_buygoods]] | Referência da amostra da **API** (130 colunas; tem subid/cogs/merchant_commission) | `amostra_api_buygoods.csv` |

## 🔗 Camadas (pipeline da fonte)
- **Webhook** → `tb_buygoods_physical_new` (silver, **fonte da verdade**) → ver [[doc_silver_buygoods]]
- **API** → `tb_silver_buygoods_orders` (silver, **complemento** de transaction_ids) → ver [[doc_silver_buygoods]]
- **2 silvers → Silver unificada** → `[[tb_gex_buygoods_unified]]` (job `gex-buygoods-unified-to-mysql-prod`) → ver [[doc_silver_buygoods]]
- **Silver → Gold** → `[[dashboard_gold_buygoods]]`, `[[dashboard_gold_clickbank_buygoods]]` (ver [[doc_gold_buygoods]])

## Tabelas relacionadas no banco
`[[buygoods_products]]` · `[[buygoods_internal_affiliates]]` · `[[tb_gex_buygoods_unified]]`

## Pendências
- [x] Receber e documentar `silver_buygoods` (webhook) e `silver_buygoods` (api). → [[doc_silver_buygoods]] (2026-06-04)
- [ ] Mapear campos das amostras → colunas das tabelas silver/gold.
