---
tipo: fluxo-n8n
instancia: psyche
workflow_id: 1A94MkT4O15EfYSk
gatilho: webhook
status: ativo  # ⚠️ a confirmar
tags: [fluxo-n8n, operacao, custos, sms, email]
---
# 🔁 Custos de SMS, E-mail e Whatsapp

- **Instância n8n:** psyche (`psyche.work.institutoexperience.com`)
- **Link do fluxo:** https://psyche.work.institutoexperience.com/workflow/1A94MkT4O15EfYSk
- **Gatilho:** **Webhook** (a partir da planilha de custos)
- **Credenciais (por nome):** `[MySQL] [AWS]`

## O que faz
Recebe via webhook os **custos diários** dos canais (SMS, E-mail, Whatsapp) — separados por
recuperação e monetização — e grava na tabela de custos.

## Lê de
- Payload do **webhook** (origem: planilha de custos SMS/E-mail/Whats).

## Escreve em (MySQL `instituto_experience`)
- [[sms_costs]] (INSERT por `data`: `sms_recup_cost`, `sms_monet_cost`, `email_recup_cost`, `email_monet_cost`, `whatsapp_recup_cost`, `whatsapp_monet_cost`).

## Planilha(s) relacionada(s)
- [[Custos SMS, E-mail e Whats]] (`1l33YWmReWBBQ3QfQh_VoAzBBfN5_kZ0OOaxpGhiRbIQ`)

## Dashboard(s)
- [[Dashboards/SMS Marketing]] · [[Dashboards/E-mail Marketing]]

## Relacionados
[[Operação/N8N/_sobre]]
