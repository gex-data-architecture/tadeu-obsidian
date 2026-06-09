---
tipo: fluxo-n8n
instancia: psyche
workflow_id: M7nxT7UHlsmqi79r
gatilho: schedule (a cada 15 min)
status: ativo  # ⚠️ a confirmar
tags: [fluxo-n8n, operacao, chatwoot, reembolso]
---
# 🔁 Chatwoot — Postgres → MySQL (sync de atendimento)

- **Instância n8n:** psyche (`psyche.work.institutoexperience.com`)
- **Link do fluxo:** https://psyche.work.institutoexperience.com/workflow/M7nxT7UHlsmqi79r
- **Gatilho:** Schedule Trigger — **a cada 15 minutos**
- **Credenciais (por nome):** `[MySQL] [AWS]` · `[Postgres] [AWS] [Instituto Experience] [chatwoot]`

## O que faz
Sincroniza incrementalmente os dados do **Chatwoot** (Postgres) para o MySQL. Para cada entidade,
busca o último `updated_at` no MySQL, lê só o que mudou no Postgres e faz **upsert** na tabela espelho `*_mat`.

## Lê de
- **Postgres (Chatwoot):** `public.conversations`, `messages`, `activities`, `team_members`, `teams`, `users` (busca incremental por `updated_at`).

## Escreve em (MySQL `instituto_experience`)
- [[cw_conversations_mat]] · [[cw_messages_mat]] · [[cw_activities_mat]] · [[cw_team_members_mat]] · [[cw_teams_mat]] · [[cw_users_mat]] (operação **upsert**)

## Dashboard(s)
- [[Dashboards/Reembolso e Atendimento]]

## Planilha(s)
- Nenhuma (fonte é o banco do Chatwoot, não há planilha manual).

## Relacionados
[[Operação/N8N/_sobre]]
