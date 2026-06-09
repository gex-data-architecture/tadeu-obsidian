---
tipo: fluxo-n8n
instancia: psyche
workflow_id: 0MaG4P02yom0hktm
gatilho: schedule (4h produtos/gestores; 1h sync)
status: ativo  # ⚠️ a confirmar
tags: [fluxo-n8n, operacao, custos, vendas-internas]
---
# 🔁 Custos de Tráfego (Gestores)

- **Instância n8n:** psyche (`psyche.work.institutoexperience.com`)
- **Link do fluxo:** https://psyche.work.institutoexperience.com/workflow/0MaG4P02yom0hktm
- **Gatilho:** Schedule — "Atualiza Produtos" e "Atualiza Gestores" a cada **4h**; sync **a cada 1h**
- **Credenciais (por nome):** `[Google Sheets] [diretoria@institutoexperience.com.br]` · `[MySQL] [AWS]`

## O que faz
Mantém a **planilha de custos** sincronizada com as dimensões do banco (lista de produtos e gestores)
e depois lê os custos preenchidos à mão e grava no MySQL, versionando por `is_current`.

## Lê de
- MySQL: `dashboard_channels_marketing` (produtos), `gerenciador_meta*` (gestores de tráfego).
- **Google Sheets** (custos preenchidos à mão) — ver planilhas abaixo.

## Escreve em
- **MySQL `instituto_experience`:** [[custos_trafego_gestores]] · [[custos_conta_agencia]] · [[custos_gerais]] (UPDATE `is_current=0` + INSERT).
- **Google Sheets** (`appendOrUpdate`): abas `Gestores` e `Produtos` (mantém a planilha alinhada às dimensões).

## Planilha(s) relacionada(s)
- [[Custos de Tráfego Pago]] (`1SkhW3blll6usavCi3nibf1zJgz8GrD8Wm6p3ETqzdYA`)
- [[Squads e Copywriters]] (`1ocQk-PPGNthIIpbNvFTje8l_XlC1ItuTXs9DLJEkyIQ`) — abas Produtos/Gestores reaproveitadas.

## Dashboard(s)
- [[Dashboards/Vendas Internas]]

## Relacionados
[[Operação/N8N/_sobre]]
