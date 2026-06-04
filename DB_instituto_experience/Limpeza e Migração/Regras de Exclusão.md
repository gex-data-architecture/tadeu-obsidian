---
tipo: regras-limpeza
schema: instituto_experience
atualizado_em: 2026-06-04
tags: [limpeza, regras, metodologia, lint]
---
# 🧭 Regras de Exclusão — tabelas e views (`instituto_experience`)

> **O que é este arquivo:** o **passo a passo e as regras** usadas para decidir se uma
> tabela ou view pode ser excluída. O resultado objeto-a-objeto fica no
> [[Checklist de Limpeza]]. Metodologia derivada da skill `limpeza-banco`, depurada
> contra o banco de produção (RDS/MySQL 8.0).

## 🔒 Princípio de segurança (inviolável)
O acesso de análise (MCP `mysql`) é **READ-ONLY**. O processo **nunca executa
`DROP`/`RENAME`/`TRUNCATE`/`ALTER`**. Ele apenas:
1. **Lê** o banco para investigar;
2. **Gera scripts `.sql`** que o DBA/admin executa com conta privilegiada;
3. **Documenta** a decisão aqui e no checklist.

A separação entre **quem analisa** (assistente) e **quem executa** (humano com conta
de admin) é a rede de segurança. Quem aprova/roda o DDL é sempre o DBA.

## ⛔ Regras invioláveis (a lista de "nunca")
- **Nunca** incluir tabelas de **swap atômico** (`_stage`, `_old`, `_new`, `_aws_new`).
  São pontas do swap: a procedure/job popula `_stage`/`_new`, faz `RENAME` e o `_old`
  vira backup. Ficam vazias **entre ciclos** — isso é estado normal, não morte.
- **Nunca** declarar uma tabela vazia morta sem checar o **irmão vivo**: tire o sufixo
  de build (`_new`, `_aws_new`, `_stage`, `_old`) e veja se existe a irmã de nome-base
  **cheia / escrita hoje**. Se existir, a vazia é o **alvo do próximo swap** → mantém.
  (Casos reais: `gold_clickbank_aws_new`, `clickbank_physical_new_aws_new`,
  `dashboard_channels_marketing_aws_new` — todas com irmã viva de 40k–330k linhas.)
- **Nunca** confiar em `information_schema.TABLES.TABLE_ROWS` para afirmar "vazia": é
  **estimativa** do InnoDB e mente (já deu `0` para tabela com linhas e vice-versa).
  Use **`COUNT(*)` real** antes de afirmar.
- **Nunca** dar um "não é lida/escrita" que não se consegue provar. Referência estática
  (procedure/view) **não cobre** leitura externa (n8n, Looker, app). Sem o sinal de
  runtime, declarar isso explicitamente e usar a **quarentena**.
- **Nunca** tratar **view** por "estar vazia" (muitas são vazias por design — ver abaixo).

## 🗂️ Passo a passo — TABELAS
0. **Schema-alvo:** `instituto_experience` (tudo filtrado por `TABLE_SCHEMA`).
1. **Candidatas brutas:** base tables com `TABLE_ROWS = 0` (estim.), **não** swap, e que
   **não** aparecem (substring `LIKE '%nome%'`, conservador) em nenhuma procedure/function,
   event ou view.
2. **Teste do irmão vivo:** para cada candidata, procurar `LIKE 'base%'` cheia/recente → se
   houver, descartar (é alvo de swap).
3. **Confirmar vazio DE VERDADE:** `COUNT(*)` real em cada candidata. Só seguem as que dão **0**.
4. **Integridade referencial:** FK externa apontando para a candidata (trata o filho antes);
   triggers na candidata (investigar).
5. **Escrita recente:** `UPDATE_TIME` (NULL = sem escrita desde o restart) + `Uptime` para
   dimensionar a janela. `CREATE_TIME` de hoje = bandeira vermelha (build em andamento).
6. **Leitura real (precisa de privilégio):** `performance_schema` —
   `table_io_waits_summary_by_table` (`COUNT_READ/WRITE`) e/ou
   `events_statements_summary_by_digest` (texto das queries). Sem privilégio/sinal →
   **quarentena por RENAME** (não DROP direto).

## 👁️ Passo a passo — VIEWS
O sinal de morte de view **não é emptiness** (views de alerta `vw_*_alert` ficam vazias
quando está tudo bem; views de estado atual `v_*_current` idem). Os sinais são:
1. **Referência estática:** a view é citada por procedure/function, event ou outra view?
2. **Uso em runtime:** `performance_schema.events_statements_summary_by_digest` —
   `MAX(LAST_SEEN)` + `SUM(COUNT_STAR)` por nome (last seen + nº execuções). Views
   alimentam o **Looker Studio** direto, e isso aparece aqui.
3. **Integridade:** `SELECT * FROM <view> LIMIT 0` resolve as colunas sem varrer dados.
   **Erro** = view **quebrada** (referencia tabela/coluna/função inexistente) = DROP forte.
   **Sucesso** = resolve; emptiness é irrelevante.
4. **Cruzar com `Dashboards/`** do vault antes de sugerir DROP (consumo Looker).

## ⚠️ Limites da análise (o que a foto NÃO prova)
- **Janela de uso curta:** o `performance_schema` só acumula **desde o último restart**
  (em 2026-06-04: uptime ~8,9 dias; restart 26/05). O `general_log` está **desligado**
  (`log_output=TABLE`), então **não há log histórico**. ⇒ *"sem uso no digest" =
  "não usada nos últimos ~9 dias"*, **não** "nunca usada". Use semanal/mensal pode escapar.
- **Digest tem teto e é volátil:** tabela de digests ~9.9k/10k (quase cheia) e zera no restart.
- **Leitura externa é invisível** à referência estática (Looker/n8n/app). Por isso a saída
  padrão para incerteza é a **quarentena por RENAME `_zzdrop_`**: se algo lê, quebra na
  hora e visível, e é **reversível** (rename de volta). 1–2 semanas sem reclamação → DROP.
- **Auto-contaminação do digest:** rodar `SELECT ... LIMIT 0` numa view para testá-la
  **registra** um acesso no digest. Logo, contagens de **1 dígito datadas do dia da análise**
  em views que antes estavam frias são **sondagem própria**, não uso real — a classificação
  usa o snapshot **pré-sondagem**.

## 🏷️ Como classifico (o que cada status do checklist significa)
**Tabelas:**
- `SWAP atomico - NAO excluir` — `_stage`/`_old`/`_new`/`_aws_new`. Intocável.
- `EM USO (referenciada) - manter` — citada por procedure/event/view.
- `VAZIA mas referenciada - manter/investigar` — 0 linhas mas referenciada (provável alvo
  de build/refresh). Investigar quem popula antes de qualquer coisa.
- `COM DADOS, sem ref. estatica - revisar` — tem dados mas nada a referencia. **Não** é prova
  de descarte (pode ser lida por Looker/n8n). Revisar caso a caso; quarentena se for remover.
- `VAZIA (estim) - confirmar COUNT, quarentena` — candidata real; confirmar `COUNT(*)` e mandar p/ quarentena.

**Views:**
- `QUEBRADA - excluir (DROP direto)` — erra no `SELECT`; ninguém consegue usar.
- `SEM USO >=9d - quarentena` — resolve, sem ref. estática e sem acesso no digest na janela.
- `EM USO - manter` — runtime e/ou referência estática.

## 📦 Saídas / scripts (nesta pasta)
- [[limpeza-tabelas-quarentena.sql]] · [[limpeza-tabelas-drop-datado.sql]]
- [[limpeza-views-quarentena.sql]] · [[limpeza-views-drop-datado.sql]]
- Backup `mysqldump --no-data --routines` é **obrigatório** no PASSO 0 de qualquer DROP.

## 🧾 Histórico de decisões e execuções
- **2026-06-03 — TABELAS (lote 1):** 28 tabelas vazias **dropadas** (DROP direto, aprovado
  pelo time — conjunto conhecido de baixo risco): Django/auth (7), temp/scratch/teste (4),
  clickbank affiliate vazias (3), exports de campanhas antigas (3), features de app não
  usadas (11). FK: `affiliate_products` antes de `affiliate_details`.
- **2026-06-03 — TABELAS (lote 2, quarentena pendente):** `clickbank_physical_v2`,
  `dashboard_cartpanda_pais_diario`, `dashboard_dim_gestorl`, `dashboard_gerenciador_unificado`,
  `dashboard_partner_affiliates` — órfãs de dashboard, incógnita de leitura externa → RENAME `_zzdrop_`.
- **2026-06-04 — VIEWS (92):** 28 mantidas · **5 quebradas** (DROP): `unified_data_view`,
  `v_team_performance`, `view_nutra_eua_acompanhamento`, `view_unified_data_all_with_upsell`,
  `vw_enriquecimento_dados` (substituída por `vw_enriquecimento_buygoods`). **59** sem uso ≥9d → quarentena.
- **Abrir leitura real (opcional):** com `GRANT SELECT ON performance_schema.table_io_waits_summary_by_table`
  ao usuário do MCP, dá para cravar quem lê e, se ninguém lê, pular a quarentena.

## Relacionados
[[Checklist de Limpeza]] · [[migracao-data_team-mapa]] · [[00-Indice]] · skill `limpeza-banco`
