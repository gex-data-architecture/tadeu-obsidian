---
tipo: fluxo-n8n
instancia: pneuma
workflow_id: EHk2cHOc0uHnRhOe
gatilho: schedule (a cada 12h)
status: ativo  # ⚠️ a confirmar
tags: [fluxo-n8n, operacao, clickbank, trafego-interno, foundational]
---
# 🔁 ClickBank — Identificação do Tráfego Interno

- **Instância n8n:** pneuma (`pneuma.work.institutoexperience.com`)
- **Link do fluxo:** https://pneuma.work.institutoexperience.com/workflow/EHk2cHOc0uHnRhOe
- **Gatilho:** Schedule — **a cada 12 horas**
- **Credenciais (por nome):** `[Google Sheets] [gabriel.gomes@institutoexperience.com.br]` · `[MySQL] [AWS]`

## O que faz
Lê na planilha o **registro do tráfego interno** do ClickBank (afiliado ↔ gestor de tráfego) e
insere no banco, marcando quais afiliados são tráfego interno.

## Lê de
- **Google Sheets** — aba `⚙️ Registro do Tráfego Interno`.

## Escreve em (MySQL `instituto_experience`)
- [[clickbank_internal_affiliates]] (INSERT: `affiliate_name`, `traffic_manager`, …).

## Planilha(s) relacionada(s)
- [[ClickBank - Tráfego Interno]] (`11iYvBwefiAbdv9ocvestRcAWO4avIcaX_MmzcrQfWto`)

## Dashboard(s)
- [[Dashboards/Vendas Internas]] (identifica tráfego interno).

## ⚠️ Nota
Usa a conta Google **`gabriel.gomes@`** (as demais usam `diretoria@`) — ponto de dependência pessoal a revisar.

## Relacionados
[[Operação/N8N/_sobre]]
