---
tipo: fluxo-n8n
instancia: psyche
workflow_id: ysJJC4WJdrf338p7
gatilho: webhook
status: ativo  # ⚠️ a confirmar
tags: [fluxo-n8n, operacao, metas, sms, email]
---
# 🔁 SMS / E-mail / Whats — Metas de Monetização e Recuperação

- **Instância n8n:** psyche (`psyche.work.institutoexperience.com`)
- **Link do fluxo:** https://psyche.work.institutoexperience.com/workflow/ysJJC4WJdrf338p7
- **Gatilho:** **Webhook** (a partir da planilha de Metas)
- **Credenciais (por nome):** `[Google Sheets] [diretoria@institutoexperience.com.br]` · `[MySQL] [AWS]`

## O que faz
Lê as **metas mensais** (SMS, E-mail, Whatsapp) preenchidas na planilha e grava na tabela de metas no banco.

## Lê de
- **Google Sheets** — planilha de Metas, abas `gross_recovery_target`, `Metas E-mail`, `Metas Whatsapp`.

## Escreve em (MySQL `instituto_experience`)
- [[gross_recovery_target]] (INSERT por `yearmonth` — sms / email / whatsapp).

## Planilha(s) relacionada(s)
- [[Metas de Monetização e Recuperação]] (`1G1TyeyZH8DhdUcSADgpTiRTNmkq73-UTAXuqTQSk55I`)

## Dashboard(s)
- [[Dashboards/SMS Marketing]] · [[Dashboards/E-mail Marketing]]

## Relacionados
[[Operação/N8N/_sobre]]
