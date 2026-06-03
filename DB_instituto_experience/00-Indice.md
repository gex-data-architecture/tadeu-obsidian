---
tipo: indice
tags: [moc]
---
# 🗂️ Documentação do Time de Dados — `instituto_experience`

> Base de conhecimento gerada a partir do banco MySQL/RDS `instituto_experience`.
> Última geração automática: 2026-06-03.

## O que tem aqui
- **355** tabelas em [[#Tabelas]] (pasta `Tabelas/`)
- **92** views (pasta `Views/`)
- **54** procedures + **1** function (pasta `Rotinas/`)
- **31** eventos agendados (pasta `Eventos/`)

Cada nota traz métricas, dependências como `[[links]]` e o SQL. Abra o **Graph View**
(ícone de grafo na barra lateral) para ver o pipeline inteiro conectado.

## 🔁 Padrão LLM Wiki
Este vault segue o padrão *LLM Wiki* (Karpathy): uma base que **se acumula** em vez de ser
re-derivada a cada pergunta.
- **Raw Sources** (cruas, imutáveis): inventário `.xlsx` + `_mapdata/*.json` + banco via MCP `mysql`.
- **Wiki**: este vault (notas + páginas curadas).
- **Schema**: [[CLAUDE]] — convenções e operações **Ingest / Query / Lint**.
- **Diário**: [[log]] — registro append-only de toda mudança.
- **Conhecimento curado**: pasta `Conhecimento/` ([[_sobre-esta-pasta]]) — **não é sobrescrita** pelos scripts.

> ⚠️ As pastas `Tabelas/ Views/ Rotinas/ Eventos/` são **geradas** e sobrescritas nas regerações.
> Conhecimento manual (dossiês, decisões, narrativas) vai em `Conhecimento/`.

## Como navegar
- **Quem mexe numa tabela?** Abra a nota da tabela → seções *Quem escreve aqui* / *Quem lê daqui*,
  ou use o painel **Backlinks** (canto inferior direito).
- **O que uma procedure faz?** Abra a nota da rotina → *Dependências* + *Corpo SQL*.
- **Grafo filtrado:** no Graph View use `tag:#rotina` ou `tag:#tabela` para focar.

## 🔗 Cadeia de orquestração — `sp_master_run_all`
O event/rotina que dispara o refresh dos dashboards chama, em ordem:

- [[sp_master_run_all]]
    - [[fix_collation_clickbank]]
    - [[fill_buygoods_offer_names]]
    - [[fill_clickbank_offer_names]]
    - [[fix_gestor_offer_names_aws]]
    - [[refresh_dashboard_gold_clickbank]]
    - [[refresh_dashboard_gold_buygoods]]
    - [[refresh_dashboard_gold_clickbank_buygoods]]
    - [[refresh_dashboard_channels_marketing]]
    - [[refresh_dashboard_channels_country_daily]]
    - [[refresh_dashboard_auditoria_leads]]
    - [[refresh_dashboard_anomalia_diaria]]
    - [[refresh_dashboard_leads_alerts]]
    - [[refresh_dashboard_leads_por_dia]]
    - [[refresh_dashboard_lead_events]]
    - [[refresh_dashboard_dims]]
    - [[atualizar_custos_trafego_diaria]]
    - [[atualizar_custos_conta_agencia_diaria]]
    - [[atualizar_custos_gerais_diaria]]
    - [[refresh_internal_funnel_v2]]
    - [[refresh_internal_product_v2]]
    - [[refresh_gerenciador_meta_ads_v2]]
    - [[refresh_gerenciador_meta_vendas_v2]]
    - [[refresh_dashboard_internal_sales_v2]]
    - [[refresh_gerenciador_meta_consolidado_v2]]
    - [[refresh_dashboard_affiliate_nutra_usd]]
    - [[refresh_dashboard_affiliate_nutra]]
    - [[refresh_dashboard_reembolso]]
    - [[refresh_dashboard_reembolso_coortes]]
    - [[refresh_dashboard_atendimento]]
    - [[refresh_dashboard_atendimento_backlog]]
    - [[refresh_dashboard_atendimento_retornos]]
    - [[refresh_dashboard_sla_times]]
    - [[refresh_dashboard_ranking_agentes]]

## 📊 Índices dinâmicos (requer plugin **Dataview**)
Depois de instalar o Dataview (Settings → Community plugins), estas consultas se preenchem sozinhas:

### Maiores tabelas
```dataview
TABLE categoria AS Categoria, linhas AS Linhas, tamanho_mb AS "Tam (MB)"
FROM "DB_instituto_experience/Tabelas"
SORT tamanho_mb DESC
LIMIT 20
```

### Tabelas candidatas a limpeza
```dataview
TABLE tamanho_mb AS "Tam (MB)", linhas AS Linhas
FROM "DB_instituto_experience/Tabelas"
WHERE contains(string(categoria), "backup") OR contains(string(categoria), "teste") OR linhas = 0
SORT tamanho_mb DESC
```

### Tabelas sem PK
```dataview
TABLE tamanho_mb AS "Tam (MB)", linhas AS Linhas
FROM "DB_instituto_experience/Tabelas"
WHERE tem_pk != "Sim"
SORT tamanho_mb DESC
```

### Eventos e sua agenda
```dataview
TABLE status AS Status, intervalo AS Intervalo, unidade AS Unidade, ultima_execucao AS "Última exec"
FROM "DB_instituto_experience/Eventos"
SORT status ASC
```

## 🛠️ Como atualizar esta documentação
Na pasta `Inventario MSQL` (Área de Trabalho), rode em ordem:
1. `python 1_extrair_rotinas.py` — re-extrai do banco
2. `python 3_gerar_vault.py` — regenera as notas de tabelas/rotinas/eventos
3. `python 4_gerar_indice.py` — regenera este índice

## 📌 Próximos passos
- [ ] Conectar o **Athena** (instalar AWS CLI + credenciais) e gerar notas equivalentes.
- [ ] Instalar plugins: **Dataview**, **Obsidian Git**, **Templater**.
- [ ] Revisar manualmente as notas das tabelas core mais críticas.
- [ ] (Opcional) Plugin **Terminal** para rodar `claude` dentro do Obsidian.
