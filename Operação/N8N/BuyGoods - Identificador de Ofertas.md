---
tipo: fluxo-n8n
instancia: pneuma
workflow_id: GW4GJAJtKIUh7PTe
gatilho: schedule (a cada 1h)
status: ativo  # ⚠️ a confirmar
tags: [fluxo-n8n, operacao, buygoods, ofertas, foundational]
---
# 🔁 BuyGoods — Identificador de Ofertas

- **Instância n8n:** pneuma (`pneuma.work.institutoexperience.com`)
- **Link do fluxo:** https://pneuma.work.institutoexperience.com/workflow/GW4GJAJtKIUh7PTe
- **Gatilho:** Schedule — **a cada 1 hora** (vários triggers escalonados)
- **Credenciais (por nome):** `AWS Athena BuyGoods` · `[Google Sheets] [diretoria@institutoexperience.com.br]` · `[MySQL] [AWS]`

## O que faz
Fluxo **foundational** (não é de um dashboard específico): descobre **novas ofertas/vendors** do
BuyGoods (via Athena), registra na planilha de Offers para curadoria humana (nome da oferta), e
sincroniza de volta o `offer_name` curado para o banco — alimentando o `buygoods_products` que o
gold de BuyGoods usa.

## Lê de
- **AWS Athena** (BuyGoods) — descoberta de produtos/ofertas/vendors.
- **Google Sheets** — abas `⚙️ Offers`, `⚙️ Registro de Vendors Existentes`, `⚙️ Registro do Tráfego Interno`.

## Escreve em
- **Google Sheets** (`append`/`update`): novas offers/vendors + marca offer como "pronta"/"lockada".
- **MySQL `instituto_experience`:** [[buygoods_products]] (UPDATE `offer_name`; INSERT `product_id`, `account_name`, …).

## Planilha(s) relacionada(s)
- [[BuyGoods - Offers e Vendors]] (`1uV977L9DRZKMHkjdHwJohFdzDXvOw9Ie7N9_KsHdxcM`)

## Dashboard(s)
- Foundational — alimenta o gold BuyGoods (offer names). Relaciona-se a [[Dashboards/Afiliados]] (⚠️ a confirmar abrangência).

## Relacionados
[[Operação/N8N/_sobre]] · [[Fontes de Dados/Buygoods/doc_silver_buygoods]]
