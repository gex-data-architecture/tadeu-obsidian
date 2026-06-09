---
tipo: fluxo-n8n
instancia: psyche
workflow_id: saJuke4J4P8HioSj
gatilho: webhook
status: ativo  # ⚠️ a confirmar
tags: [fluxo-n8n, operacao, dimensoes, vendas-internas]
---
# 🔁 Dimensões — Copywriters e Squads

- **Instância n8n:** psyche (`psyche.work.institutoexperience.com`)
- **Link do fluxo:** https://psyche.work.institutoexperience.com/workflow/saJuke4J4P8HioSj
- **Gatilho:** **Webhook** (disparado a partir da planilha de Squads/Copywriters)
- **Credenciais (por nome):** `[MySQL] [AWS]`

## O que faz
Recebe via webhook os dados de **copywriters e squads** (mantidos na planilha) e atualiza as
dimensões no banco, versionando por `is_current` (desativa o vigente e insere o novo).

## Lê de
- Payload do **webhook** (origem: planilha de Squads e Copywriters).

## Escreve em (MySQL `instituto_experience`)
- [[dim_copywriter]] · [[dim_squad]] (UPDATE `is_current=0` + INSERT).

## Planilha(s) relacionada(s)
- [[Squads e Copywriters]] (`1ocQk-PPGNthIIpbNvFTje8l_XlC1ItuTXs9DLJEkyIQ`)

## Dashboard(s)
- [[Dashboards/Vendas Internas]]

## Relacionados
[[Operação/N8N/_sobre]]
