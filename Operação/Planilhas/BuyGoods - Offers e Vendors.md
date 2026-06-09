---
tipo: planilha-manual
dono: # ⚠️ a confirmar
url: https://docs.google.com/spreadsheets/d/1uV977L9DRZKMHkjdHwJohFdzDXvOw9Ie7N9_KsHdxcM
spreadsheet_id: 1uV977L9DRZKMHkjdHwJohFdzDXvOw9Ie7N9_KsHdxcM
frequencia: # ⚠️ a confirmar (curadoria contínua)
tags: [planilha-manual, operacao, buygoods, ofertas]
---
# 📄 BuyGoods — Offers e Vendors

- **Link:** https://docs.google.com/spreadsheets/d/1uV977L9DRZKMHkjdHwJohFdzDXvOw9Ie7N9_KsHdxcM/edit?gid=0
- **Spreadsheet ID:** `1uV977L9DRZKMHkjdHwJohFdzDXvOw9Ie7N9_KsHdxcM`
- **Conta Google do fluxo:** `diretoria@institutoexperience.com.br` (OAuth do n8n)
- **Dono / quem preenche:** ⚠️ a confirmar (curadoria de nomes de oferta)

## O que contém (abas)
- `⚙️ Offers`, `⚙️ Registro de Vendors Existentes`, `⚙️ Registro do Tráfego Interno`. ⚠️ Colunas a documentar (2ª passada).
- O fluxo escreve nela (novas offers/vendors) **e** lê dela o `offer_name` curado.

## Consumida por (fluxo → tabela)
- [[BuyGoods - Identificador de Ofertas]] → [[buygoods_products]]

## Dashboard(s)
- Foundational (offer names do gold BuyGoods) — relaciona-se a [[Dashboards/Afiliados]] ⚠️ a confirmar.

## ⚠️ Risco
Curadoria humana de nomes de oferta — atraso na curadoria deixa ofertas sem `offer_name` no banco.

## Relacionados
[[Operação/Planilhas/_sobre]] · [[Fontes de Dados/Buygoods/doc_silver_buygoods]]
