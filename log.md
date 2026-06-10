# log.md — Diário da base de conhecimento

> Registro **append-only** (só adicionar no topo). Cada entrada: data, operação
> (INGEST / QUERY / LINT / EDIT) e o que mudou. Padrão LLM Wiki.

## 2026-06-09 — QUERY (validação silver tb_gex_buygoods_unified × plataforma BuyGoods — DIÁRIA)
- Reconciliação **dia a dia** com o **export diário** do Master Overview (Excel, 01/04→09/06, USD),
  alinhada pelo **timestamp da plataforma** (`datetime_platform`/`datetime_refunded_platform`).
- De-para final: Gross=`total_price_usd-iva_usd`; Commissions=`affiliate_amount_usd`;
  Refunds=`total_refund_usd` não-chargeback por `datetime_refunded_platform`; Chargebacks=refund de
  rows chargeback; Taxes=`iva_usd` approved. Net=Gross−Comm−Refunds−CB−Taxes (plataforma soma Commission Voids).
- Resultado: **Refunds +0,05%** (reconcilia), Commissions −0,45%, Taxes +0,91%, Gross +0,38%.
  **Chargebacks**: incluído o `chargeback_fee` na definição (`total_refund_usd + chargeback_fee_usd`) →
  desvio caiu de −16,5% para **−5,4%**. ⚠️ Gross **+2% no fim (junho)** = settlement do período recente.
- Nota com **tabela por dia** (plataforma × silver lado a lado, 70 dias) + de-para + total + achados,
  e gerador `.py` que lê Excel+MySQL: `Operação/Validações/validacao-silver-buygoods-plataforma-2026-06-09.md`.

## 2026-06-09 — INGEST (Operação: 7 fluxos N8N + 6 planilhas + linkagem com dashboards)
- 1ª passada da pasta "Operação Obsidian" (OneDrive): criadas **7 notas de fluxo** em `Operação/N8N/`
  (psyche: Chatwoot/Reembolso, Custos Tráfego, Dimensões Copys/Squads, SMS-Metas, Custos SMS;
  pneuma: BuyGoods Ofertas, ClickBank Tráfego Interno) e **6 notas de planilha** em `Operação/Planilhas/`,
  com gatilho, o que lê/escreve (tabelas) e credenciais por nome.
- **Linkados aos dashboards** (seções 🔗 Planilhas e 🔁 Fluxos): Vendas Internas, SMS Marketing,
  E-mail Marketing, Reembolso e Atendimento, Afiliados. Auditoria de Leads: sem fluxo/planilha neste lote.
- `_sobre.md` de N8N e Planilhas viraram índices. Segurança: scan dos JSONs **sem segredos**; JSONs
  ficam no OneDrive (não versionados). **Conteúdo das planilhas (abas/colunas) = 2ª passada via MCP Sheets.**

## 2026-06-09 — SKILL + EDIT (eventos separados em ENABLE/DISABLE)
- Nova skill `organizar-eventos`: lê `information_schema.EVENTS` (read-only) e separa as notas em
  `Eventos/ENABLE` (ativos) e `Eventos/DISABLE` (inativos). Rodada agora: **5 ENABLE / 26 DISABLE**.
- Gerador `3_gerar_vault.py` patchado p/ escrever direto nas subpastas (makedirs + escrita por STATUS +
  limpeza de órfãos por pasta-folha) → o split se mantém nas regerações.
- Catálogo de skills atualizado (7 skills).

## 2026-06-09 — QUERY (validação dashboard_gold_buygoods × tb_gex_gold_buygoods)
- Reconciliação read-only por dia (27/05→08/06) das duas tabelas MySQL em `instituto_experience`.
  **Idênticas** em todas as medidas conferidas (linhas, tx distintos, quantity, total_price BRL/USD,
  total_refund BRL/USD) — diferença zero. Total: 89.530 tx · 903.193 qtd · R$ 182,78 mi · US$ 35,99 mi.
- Estendido p/ **todas as 45 colunas numéricas** (soma do período): **diff = 0 em 45/45**.
- Nota: `Operação/Validações/validacao-gold-buygoods-mysql-2026-06-09.md`.

## 2026-06-05 — FIX (repath dos geradores GERADO p/ nova estrutura ADR-001)
- Geradores que escreviam nos caminhos antigos foram repathados p/ a estrutura pós-reorg:
  - `Inventario MSQL/3_gerar_vault.py` e `4_gerar_indice.py` (OneDrive, fora do repo):
    `DB_instituto_experience` → `Banco de Dados/MySQL/instituto_experience`; `Templates/` → `Sistema/_Templates`;
    Dataview `FROM "DB_instituto_experience/…"` → `FROM "Banco de Dados/MySQL/instituto_experience/…"`;
    textos da antiga pasta `Conhecimento/` → "casa = dono" (entidade dona).
  - skill `catalogo-datalake/gerar_datalake.py` (versionado): `Data Lake/` → `Arquitetura/Data Lake/`;
    SKILL.md alinhada (estrutura gerada, refs a `Conhecimento/` e `DB_instituto_experience`).
- Validado: `py_compile` OK nos 3 scripts; os 4 destinos resolvem p/ pastas já existentes (sem órfãs).

## 2026-06-05 — EDIT (Reuniões: ata da sessão com o Davi)
- Registrada a sessão Davi × Tadeu (05/06, 13:45–14:05 UTC) em `Reuniões/` — **sem transcript bruto** (só o
  resumo do calendário; não há item em `_raw_files`). Temas: migração `instituto_experience` → **Data Team**
  (de-para + `tb_gold_clickbank`/`tb_gold_buygoods`), **skill `onboard-gateway` agnóstica**, **MCP**, **hooks do
  Claude Code**, e **qualidade** (mediana > média; padronizar eventos SMS/e-mail/call center).
- 7 action items abertos; reforça a prioridade do `onboard-gateway` já apontada pelo Gabriel.

## 2026-06-05 — TOOLING (obsidian-cli instalado)
- `Yakitrak/obsidian-cli` (renomeado p/ **notesmd-cli v0.3.6**) — binário oficial no PATH (npm bin), vault
  `DataTeamDocs` registrado como default. Action items da call do Gabriel (superpowers + obsidian-cli) fechados.

## 2026-06-04 — INCIDENTE (Meta Ads) — causa raiz CONFIRMADA via fluxos N8N
- Analisados os 4 workflows N8N da ingestão Meta (perfil Gabriel Gomes). **Confirmado:** token da credencial
  `[Meta Ads] [Perfil | Gabriel Gomes]` (perfil 656581916148820) perdeu acesso a ~50 das 57 contas em ~26/05.
  `facebook_reports_accounts_list` é UPSERT (não remove) → mascara o problema. Não é query/paginação — é permissão do token.
- 🔒 Token do Meta **hardcoded** nos JSONs exportados → não versionar como está; rotacionar. Token de perfil pessoal (frágil) → migrar p/ System User.
- Confirmação anexada ao `Incidentes/2026-06-04 - Meta Ads spend incompleto desde 26-05.md`.

## 2026-06-04 — INCIDENTE (Meta Ads: investimento incompleto desde 26/05)
- Investigação read-only: `[[gerenciador_meta_consolidado_v2]]` **correta** (spend bate com a `ads_v2`);
  a falha é a montante na bruta **`meta_ad_id`** — caiu de **~57 contas / ~20k ads / ~R$120–150k/dia**
  para **3–12 contas / centenas de ads / ~R$1–4k/dia** em **26/05** (dias 02/06 e 05/06 ausentes).
- **Causa raiz:** perda de acesso às contas de anúncio (token/permissão Meta) — camada AWS/Meta.
- **Armadilha:** `refresh_gerenciador_meta_ads_v2` só recalcula 3 dias e congela o resto → gap vira permanente sem rebuild.
- Registrado em `Incidentes/2026-06-04 - Meta Ads spend incompleto desde 26-05.md` (plano + SQL de rebuild pós-backfill).

## 2026-06-04 — EDIT (Reuniões: ata + cru da sessão com o CTO sobre o vault)
- Arquivada a sessão Gabriel × Tadeu (04/06) que não tinha sido salva: transcript **cru** em
  `Sistema/_raw_files/reuniões/processado/` + **ata** estruturada em `Reuniões/` (resumo, decisões,
  action items). Linkada bidirecional com a [[Decisao-2026-06-04-reorganizacao-pastas-vault|ADR-001]] (`resultou_em`).
- Primeiro uso real da esteira `_raw_files` (o cru estava só no chat; agora preservado/reprocessável).

## 2026-06-04 — REORG (estrutura de pastas alinhada ao CTO; ADR-001 executado)
- Executada a reorganização via **git mv** (histórico preservado): **`Sistema/`** (`_raw_files/{reuniões,documentos,notas}/{pendente,processado}`,
  `Capturas (log de populate)/`, `Base de Conhecimento (Claude)/`, `_Templates/`, `Skills/`);
  **`Banco de Dados/MySQL/{instituto_experience,data_team}`** (unifica os 2 `DB_*`);
  **`Arquitetura/{Data Lake, Migração data_team}`**; **`Fontes de Dados/`**; **`Pessoas/Recrutamento/`**;
  **`Parceiros/Teddy/Reuniões/`**; **`Reuniões/`**, **`Decisões/`**, **`Projetos/`**,
  **`Operação/{Validações,Fluxos-N8N,Planilhas Manuais}`**.
- **`Conhecimento/` dissolvida** (princípio "casa = dono"): call Teddy → Parceiros; ADRs → Decisões;
  índice de calls → `Reuniões/_sobre`; `Dossies/_sobre` + `_sobre-esta-pasta` removidos (template de dossiê sobrevive).
- `CLAUDE.md` reescrito (estrutura, convenção de link por caminho, **§8 regra de espelhamento**). Índices,
  Dataview e wikilinks com caminho corrigidos. Skills do CTO adaptadas (dono Gabriel→**Tadeu**; paths já batem).
- ⚠️ **Pendente (geradores GERADO ainda escrevem nos caminhos antigos):** `Inventario MSQL/{1,3,4}_*.py`
  (→ `Banco de Dados/MySQL/<db>`) e `gerar_datalake.py` da skill `catalogo-datalake` (→ `Arquitetura/Data Lake/`).
  Repathar antes de re-rodar, senão recriam `DB_*/` e `Data Lake/` na raiz. `references/` das skills (formats.md, routing.md) ainda pendentes do CTO.

## 2026-06-04 — EDIT (Sistema: instalada 3ª skill do CTO — sincronizar-conhecimento)
- Instalada `.claude/skills/sincronizar-conhecimento/SKILL.md` (verbatim). Catálogo → **6 skills**.
- ⚠️ Mesma ressalva: assume `Sistema/Base de Conhecimento (Claude)/`, regra de espelhamento no `CLAUDE.md`
  e skip-list do Gabriel. Adaptar na reorg. Completam o trio do CTO: populate + transcript-extractor + sincronizar.

## 2026-06-04 — EDIT (Sistema: instaladas skills do CTO — populate + transcript-extractor)
- Instaladas (verbatim, como o CTO enviou): `.claude/skills/populate/SKILL.md` e
  `.claude/skills/transcript-extractor/SKILL.md`. Catálogo atualizado (5 skills) com aviso de compatibilidade.
- ⚠️ Ambas pressupõem a **estrutura do vault do Gabriel** (`Sistema/_raw_files/`, `BUs/`, `Departamentos/`,
  `Parceiros/`, `Pessoas/<Nome>/1on1/`, `_Templates`, "Gabriel é o dono") — não existe no nosso vault.
  E dependem de `references/formats.md` e `references/routing.md` ainda não recebidos. Adaptar após a reorg
  ([[Decisao-2026-06-04-reorganizacao-pastas-vault]]). Não rodar as skills até alinhar. Ainda não commitado.

## 2026-06-04 — EDIT (Sistema: skill + catálogo de skills)
- Criada skill **`catalogo-skills`** (`.claude/skills/catalogo-skills/SKILL.md`): varre `.claude/skills/`
  e gera `Sistema/Skills/_catalogo.md` (o que faz / quando usar por skill). Alinhada à call com o CTO (04/06).
- Criada pasta **`Sistema/Skills/`** com `_catalogo.md` listando as 3 skills atuais (catalogo-datalake,
  limpeza-banco, catalogo-skills) + 4 planejadas (transcript-extractor, popular-conhecimento,
  sincronizar-conhecimento, onboard-gateway).
- `Sistema/` é o início da nova arquitetura ("sistema" separado de "conhecimento"). Proposta de
  reorganização completa de pastas em discussão (não executada). Ainda não commitado no git.

## 2026-06-04 — EDIT (Buygoods: doc técnica da camada silver)
- Criada `Documentações Fontes de Dados/Buygoods/doc_silver_buygoods.md` (CURADO): regras e processo
  para gerar a **silver unificada** `tb_gex_buygoods_unified` a partir das 2 silvers no Athena/S3 —
  **webhook** (`tb_buygoods_physical_new`, fonte da verdade) + **API** (`tb_silver_buygoods_orders`,
  complemento de `transaction_id` faltante via LEFT ANTI JOIN). Documenta de-para `subid*→utm_*`,
  `cancel_reason` só-API, fluxo do job `gex-buygoods-unified-to-mysql-prod` (8 passos + swap atômico +
  salvaguarda 90%) e o schema real de 62 colunas (origem por coluna). Fecha pendência do [[Buygoods]].
  Acrescentado **§6 Dicionário de campos campo a campo** (representa / cálculo·origem do payload webhook|API /
  particularidades), com domínios perfilados na tabela real (transaction_type, payment_status, sales_type,
  câmbio ~5,0, cobertura utm/cancel_reason por data_source) — read-only.
- Atualizado `Buygoods.md` (links + pendência marcada). Baseado no script `silver_to_mysql_buygoods_unified.py`
  e no schema lido do MySQL (read-only). Ainda não commitado no git.

## 2026-06-04 — EDIT (Calls: resumo da call de consultoria Teddy × GEX)
- Criada `Conhecimento/Calls/2026-06-03 - Alinhamento Teddy (consultoria de dados).md` (CURADO):
  resumo da call (78 min, Fathom) com a consultoria **Teddy/TED** (responsável Flávio Vieira;
  Diego Pinto eng., Gabriel Ferreira BI). Estrutura: resumo executivo, pontos por tema (arquitetura,
  orquestração, modelagem, governança, Lovable/IA), comparativo GEX×Teddy, action items e
  **10 planos de ação priorizados** (esforço × impacto).
- Gerada via **workflow** (5 agentes extraindo temas + síntese); revisada à mão para preencher
  Orquestração e corrigir IaC/versionamento (a GEX já usa Terraform+GitHub via Léo).
- Índice `Conhecimento/Calls/_sobre.md` atualizado. Ainda não commitado no git.

## 2026-06-04 — EDIT (reorganização: pasta `Limpeza e Migração/`)
- Criada `DB_instituto_experience/Limpeza e Migração/` reunindo tudo de limpeza + migração.
- **Migração mantida separada** dentro da pasta: `migracao-data_team-mapa.md` (movida via git mv).
- **3 markdown fundidos em 2:** os antigos `_checklist-limpeza.md`, `limpeza-views-nao-utilizadas.md`
  e `limpeza-tabelas-vazias.md` viraram **`Regras de Exclusão.md`** (princípio read-only, regras
  invioláveis, passo a passo de tabelas e views, limites/janela de 9d, buckets, histórico de execução)
  e **`Checklist de Limpeza.md`** (só o checklist 356 tabelas + 92 views com coluna *Excluir?*).
- Scripts `.sql` movidos para a pasta e renomeados p/ clareza: `limpeza-tabelas-quarentena.sql`,
  `limpeza-tabelas-drop-datado.sql`, `limpeza-views-quarentena.sql`, `limpeza-views-drop-datado.sql`.
- Wikilinks do checklist reapontados p/ [[Regras de Exclusão]]. Nada commitado no git ainda.

## 2026-06-04 — EDIT (checklist mestre de limpeza: 356 tabelas + 92 views)
- Criado `DB_instituto_experience/_checklist-limpeza.md` (CURADO): todas as **356 tabelas** e **92 views**
  em tabelas markdown, agrupadas por análise (vazia/com dados/referenciada/swap; quebrada/sem uso/em uso),
  com coluna **Excluir?** para o usuário marcar (`x`). Linhas geradas via SQL CONCAT (read-only) p/ evitar erro.
- ⚠️ Anotado no doc: janela de uso = ~9 dias (uptime); estimador de linhas mente; leitura externa invisível →
  quarentena; e que a re-sondagem de views poluiu o digest (classificação usa o snapshot pré-sondagem).
- Próximo: usuário marca a coluna Excluir? → eu gero quarentena/DROP só com o marcado. Nada commitado no git.

## 2026-06-04 — LINT (limpeza de views: 64 candidatas de 92, 5 quebradas)
- Análise read-only das **92 views** de `instituto_experience` (skill `limpeza-banco`).
  Sinais usados: referência estática (procedure/event/view) + uso em runtime
  (`performance_schema.events_statements_summary_by_digest`) + integridade (`SELECT ... LIMIT 0`).
- **28 mantidas** (uso em runtime e/ou ref. estática — ex.: `vw_enriquecimento_buygoods` 89.870 exec,
  `affiliate_nutra`, `affiliate_nutra_usd`, `internal_sales`). **5 quebradas** (DROP direto):
  `unified_data_view`, `v_team_performance`, `view_nutra_eua_acompanhamento`,
  `view_unified_data_all_with_upsell`, `vw_enriquecimento_dados` (substituída pela `_buygoods`).
  **59 válidas-porém-paradas** (sem uso ≥9 dias) → quarentena.
- ⚠️ **Janela curta:** `performance_schema` cobre só ~8,9 dias (uptime; restart 26/05) e `general_log`
  está OFF — "sem uso" = "não usada em ~9 dias", não "nunca". Por isso a recomendação é
  **quarentena por RENAME `_zzdrop_`** antes do DROP (teste reversível p/ pegar leitura externa/Looker).
- Cruzado com `Dashboards/` — nenhuma candidata referenciada (notas ainda em rascunho).
- Artefatos: `DB_instituto_experience/limpeza-views-nao-utilizadas.md`,
  `limpeza-views-quarentena.sql`, `limpeza-views-drop-datado.sql`.
- **Nenhum DDL executado** (MCP read-only); execução pelo DBA/admin. Ainda não commitado no git.

## 2026-06-03 — EDIT (Entrevistas: transcripts + avaliação de 2 candidatos Data View/BI)
- Nova pasta **`entrevistas/`** (CURADO) com 2 notas de entrevista (vaga Analista de Dados / BI, Sênior→pode virar Pleno):
  **`Kleriston.md`** e **`Júlio.md`**. Cada uma: frontmatter (`candidato`, `gravacao` Fathom, `nota_case`,
  `nivel_case`, `recomendacao`), action items da gravação, **transcript bruto** formatado e uma seção
  **🧭 Resumo / Avaliação** cruzando a nota do case (Looker Studio) com a performance na entrevista.
- Notas do case via `data-talent-quest.lovable.app` (WebFetch, somente leitura):
  **Kleriston 6.7** (forte em viz/storytelling/UX) e **Júlio 6.4** (forte em engenharia/modelagem/API) — ambos **Pleno**,
  nenhum recomendado p/ Sênior (gap em maturidade executiva, integridade de dados e Cloud Code pago em produção).
- ⚠️ Conforme pedido: **ainda não commitado no git.**

## 2026-06-03 — EDIT (Dashboards: estrutura das 6 notas do Looker Studio)
- Criadas 6 notas em `Dashboards/` (CURADO): **SMS Marketing, E-mail Marketing, Auditoria de Leads,
  Afiliados, Vendas Internas, Reembolso e Atendimento**. Frontmatter padrão (`looker_url`, `report_id`).
- **Status: rascunho** — fontes de dados **inferidas** pela linhagem do mapa de migração (wikilinks p/ as
  tabelas-fonte + nome 🔜 no `data_team`). Marcado ⚠️ tudo que depende de abrir o relatório: páginas,
  métricas, dono, fuso/moeda e as **fontes exatas** (*Recurso → Gerenciar fontes de dados*).
- Índice `Dashboards/_sobre.md` ganhou a tabela dos 6 com fontes principais e nome futuro.
- Pendente: conectar extensão Claude in Chrome p/ abrir cada dashboard e trocar ⚠️ por dados verificados.

## 2026-06-03 — EDIT (migração data_team: escopo ampliado p/ as fontes + padrão de nomes)
- `DB_instituto_experience/migracao-data_team-mapa.md` (CURADO): definido o **padrão de nomenclatura**
  `tb_<camada>_<dominio>[_<assunto>][_<grão>]` (snake_case, domínio em inglês, sem `_v2`) e proposto
  o **novo_nome de todas as tabelas** que vão para o `data_team`.
- **Dropado o `gex_`** do padrão (a pedido): o schema `data_team` já é o namespace — `tb_gex_` repetiria o time.
  Mantido o `tb_` (distingue tabela de `vw_`). Find/replace por camada p/ não tocar no nome real `tb_gex_buygoods_unified` (origem).
- **Reversão de premissa** (a pedido: *"as só lidas também precisam ser migradas"*): as **24 fontes**
  (antes mantidas no `instituto_experience`) entram na migração. Novas seções **H) bronze** (19 feeds crus)
  e **I) dim** (5 lookups). Camada nova **`bronze`** introduzida p/ feeds ingeridos por pipelines externos.
- **Camadas finais (lineage real, não pelo nome antigo):** 4 silver · 14 gold · 14 mart · 5 dim (37 finais).
  **Total do banco: 61 tabelas** → 19 bronze · 4 silver · 14 gold · 14 mart · 10 dim.
- ⚠️ **Peso:** migração sobe de ~7 GB (finais) p/ **~44 GB**. 3 fontes = 99% do extra:
  `unified_lead_events_new` 26.9 GB, `meta_ad_id` 5.6 GB, `cw_messages_mat` 3.8 GB.
- **9 decisões a confirmar** registradas — destaque p/ §6 (repontar produtores externos das bronze:
  jobs Glue `*-to-mysql`/lambdas/n8n) e §7 (migrar gigantes inteiras vs. recorte).
- Só edição de markdown; **nenhuma escrita no MySQL** (DDL/INSERT só serão gerados após aprovação).
- ⚠️ Conforme pedido: **ainda não commitado no git.**

## 2026-06-03 — INGEST (Data Lake: agendamentos — EventBridge rules cron/rate + EventBridge Scheduler)
- `catalogo-datalake/scripts/gerar_datalake.py` agora também cataloga os **agendamentos** que disparam o lake.
  Duas fontes (somente leitura): regras EventBridge com `ScheduleExpression` (`events.list_rules`) **e** o
  serviço novo **EventBridge Scheduler** (`scheduler.list_schedules`/`get_schedule`, com fallback se indisponível).
- **49 agendamentos** mapeados (**21 ativos**, 28 desabilitados). Para cada: **status** (🟢/⚪),
  **horário legível** (cron/rate traduzido p/ pt, em **UTC**), **expressão** crua e o **alvo**
  (SFN/job/crawler/lambda). Universal targets `aws-sdk:glue:startJobRun` resolvidos p/ o nome real do job via `Input`.
- Saídas:
  - Nova seção **`## Agendamentos (EventBridge)`** em `00-Orquestracao.md` (tabela completa) e resumo no `00-Data-Lake.md`.
  - Cada nota de **Step Function** disparada por agenda ganhou o bloco **"Agendada (EventBridge schedule)"**
    no Encadeamento — ex.: `gex-bronze-to-silver-buygoods-prod` roda `cron(30 0/2 * * ? *)` (a cada 2h no min 30 UTC),
    batendo com o histórico de execuções (01:30, 03:30, 05:30…).
- Tudo **somente leitura** (`events.list_rules`, `scheduler.list_schedules/get_schedule` add às permissões na SKILL.md;
  `put_rule`/`enable_rule`/`disable_rule`/mutações seguem proibidos). `SKILL.md` e `CLAUDE.md` atualizados.
- ⚠️ Conforme pedido anterior: **ainda não commitado no git.**

## 2026-06-03 — INGEST (Data Lake: orquestração — Step Functions + Crawlers + EventBridge)
- `catalogo-datalake/scripts/gerar_datalake.py` ampliado p/ documentar **como os jobs são orquestrados**.
  Novos clients (somente leitura): `stepfunctions` e `events` (EventBridge).
- Nova pasta **`Data Lake/Orquestracao/`** (GERADA, espelho da AWS):
  - **20 Step Functions** — 1 nota cada, com: **Fluxo** passo a passo do ASL (jobs ▶️, crawlers 🕷️,
    SFN aninhadas ⤵️, descendo em `Parallel`/`Map`), **Encadeamento** (quem dispara / o que dispara),
    alvos, **últimas execuções** (`list_executions`) e a **definição ASL** embutida.
  - **17 crawlers** — 1 nota cada (database/target alvo + último estado).
  - **`00-Orquestracao.md`** — mapa geral: cadeias a partir de cada raiz, **grafo mermaid**,
    alertas de falha (EventBridge→SNS) e lista de crawlers.
- **Descoberta-chave**: o encadeamento *entre* SFNs NÃO está no ASL — está nas **regras EventBridge**
  (`source: aws.glue`, `detail.state=SUCCEEDED` → `startExecution` da próxima SFN). Regras
  `FAILED/TIMEOUT/STOPPED → SNS` viram alertas. O grafo é reconstruído parseando esses `EventPattern`.
- Cadeia buygoods reconstruída automaticamente, batendo com o diagrama do usuário:
  `gex-bronze-to-silver-buygoods-prod` →(job ✓)→ `gex-buygoods-unified-to-mysql-prod` →(✓)→
  `gex-buygoods-gold-prod`, e em paralelo →(✓)→ `gex-silver-to-mysql-buygoods-prod`.
- Tudo **somente leitura** (`sfn.list/describe/list_executions`, `events.list_rules/list_targets_by_rule`,
  `glue.get_crawlers/batch_get_crawlers` adicionados às permissões na SKILL.md; nenhuma mutação).
- `SKILL.md` e `CLAUDE.md` atualizados (estrutura `Orquestracao/` + permissões de leitura SFN/EventBridge).
- ⚠️ Conforme pedido: **ainda não commitado no git.**

## 2026-06-03 — INGEST/SYNC (rotinas/eventos do MySQL: + seção Execuções via performance_schema)
- **Corpo SQL já era embutido** nas notas de rotina/evento — análogo do "script" dos Jobs, nada a fazer ali.
- Novo análogo de "últimas execuções": o `performance_schema` **voltou a ficar acessível** para
  `events_statements_summary_by_program`. `1_extrair_rotinas.py` agora dumpa `program_stats.json`
  (procedures/functions/events: `count_star`, tempos médio/máx/total, erros, warnings, linhas afetadas).
  Com `try/except` — em ambiente sem acesso, grava `[]` e o pipeline não quebra.
- `3_gerar_vault.py`: nova seção **`Execuções (performance_schema)`** nas notas de **Rotina** e **Evento**,
  + `execucoes` no frontmatter (útil p/ Dataview). Timer convertido de picosegundos p/ legível.
- ⚠️ Esses contadores **zeram a cada restart** do MySQL → rotulados como "desde o último restart",
  não histórico absoluto. MySQL não tem log por-execução de procedure/evento (diferente do Glue `get_job_runs`).
- Regerado: 355 tabelas / 92 views / 54 rotinas / 31 eventos = 532 notas; 46 linhas de stats; 0 órfãs.
- `CLAUDE.md` atualizado (frontmatter `execucoes`; perf_schema agora acessível p/ execuções de programas).

## 2026-06-03 — INGEST (notas de Job do Data Lake: + script ETL embutido + últimas execuções)
- `catalogo-datalake/scripts/gerar_datalake.py` ampliado: cada nota de **Job** agora traz
  - **Últimas execuções** (8 mais recentes via `glue.get_job_runs`): início, estado, duração, erro;
    e `ultima_execucao` + `ultimo_estado` no frontmatter (útil p/ Dataview).
  - **Script ETL embutido**: baixado do S3 (`s3.get_object` na `ScriptLocation`) num bloco ```` ````python ````.
- Tudo **somente leitura** (acrescentei `get_job_runs` e `s3.get_object`-só-do-script às permissões na SKILL.md;
  put/start_job_run/mutações seguem proibidos). Erros de acesso a um script não derrubam a geração.
- Regerado: 40 tabelas / 63 jobs, 0 órfãs. Mirror da AWS mantido (tudo continua `.md`).

## 2026-06-03 — QUERY/VALIDAÇÃO (gold buygoods: MySQL × Athena → **TABELAS IGUAIS**)
- Reconciliação completa entre `instituto_experience.dashboard_gold_buygoods` (gerada por procedure)
  e `gex_db_prod_gold.tb_gex_gold_buygoods` (gold do data lake / Athena). Somente leitura nas duas pontas.
- Script `Validações/validacao_gold_buygoods.py`; relatório `Validações/validacao-gold-buygoods-2026-06-03.md`.
- **Resultado: ✅ idênticas** em todos os ângulos checados:
  - Linhas (grão): 226.001 = 226.001; `transaction_id` distintos: 226.001 = 226.001.
  - Reconciliação de conjunto: 0 só-no-MySQL, 0 só-no-Athena (interseção = total).
  - Somas das **46 medidas numéricas** (total_price_usd, iva_usd, taxes_usd, commission_usd, upsells/downsells,
    total_collected_usd, etc.): diferença +0.0000% em todas.
  - Quebra por dia: todos os dias batem em contagem e em `SUM(total_price_usd)`.
- Nota: `COUNT(DISTINCT created_at_date)`=65 vs `GROUP BY`=66 — a data NULL conta como grupo no GROUP BY
  mas é ignorada pelo COUNT(DISTINCT). As **duas pontas concordam** nos dois números → não é divergência.
- Schema: 75 colunas de mesmo nome; tipos diferem só na representação (`text/date` no MySQL × `string`/partição no Athena).

## 2026-06-03 — INGEST (Data Lake AWS catalogado + skill `catalogo-datalake` criada)
- **Conexão AWS estabelecida** (AWS CLI v2 instalado; perfil `buygoods`, conta 406933028738, `us-east-1`).
  Validado read-only: `sts get-caller-identity`, `s3 ls`, Glue (Data Catalog + Jobs), Athena workgroup `primary`.
- Skill **`catalogo-datalake`** criada em `.claude/skills/catalogo-datalake/` (SKILL.md + `scripts/gerar_datalake.py`):
  introspecta a **AWS Glue via boto3** (somente `get_*`/`list_*` — nunca muta nada) e gera a pasta `Data Lake/`.
  Re-rodável; remove notas órfãs (espelho do lake).
- **Pasta `Data Lake/` gerada**: **40 tabelas** em 7 databases Glue (`gex_db_<develop|prod>_<bronze|silver|gold>`)
  + **63 ETL Jobs**. 1 nota por tabela (formato/location S3/partições/colunas) e por job (worker, script, role,
  parâmetros de negócio `--source/target_bucket`, `--DATABASE_NAME`, `--read_mode`). Índice `00-Data-Lake.md`
  agrupa tabelas por database e jobs por fluxo (`landing→bronze→silver→gold→mysql`).
- Arquitetura **medallion** confirmada: o lake alimenta o `instituto_experience` via jobs `*-to-mysql` — elo
  entre `DB_instituto_experience` (MySQL) e o `Data Lake/` (AWS). `CLAUDE.md` atualizado (Data Lake = GERADO).
- Pendência: ligar à mão (em `Conhecimento/`) os jobs `*-to-mysql` às tabelas-fonte que eles escrevem no MySQL.

## 2026-06-03 — INGEST/SYNC (inventário regenerado do banco após o DROP das 28; +limpeza de órfãos)
- Rodado `1_extrair_rotinas.py` → `3_gerar_vault.py` → `4_gerar_indice.py` contra o banco vivo.
  Estado atual do `instituto_experience`: **355 tabelas, 92 views, 54 rotinas, 31 eventos** (532 notas).
  Conferido: as 28 tabelas dropadas **não** aparecem mais (json e pasta `Tabelas/`); comparação
  arquivo-a-arquivo vs. banco = 0 órfãos, 0 faltando.
- **Robustez adicionada:** `3_gerar_vault.py` agora **remove notas órfãs** ao final (qualquer `.md`
  em Tabelas/Views/Rotinas/Eventos que não corresponda a um objeto atual do banco). Antes os scripts só
  escreviam, nunca apagavam — um drop futuro deixaria nota velha + `[[link]]` quebrado. Agora a geração é
  espelho do banco. Seguro porque essas pastas são 100% geradas (conteúdo curado mora em `Conhecimento/`).
- Pendência: LINT de `[[wikilinks]]` em notas CURADAS que ainda apontam p/ as 28 dropadas (links mortos).

## 2026-06-03 — EDIT (pipeline do vault agora é DB-driven: Tabelas/Views vêm do banco, não do xlsx)
- **Problema:** `3_gerar_vault.py` lia a lista de Tabelas/Views do `inventario_banco_instituto_experience.xlsx`,
  um snapshot **órfão** (nenhum script da pasta o regenera — o `2_gerar_excel.py` só faz Excel de rotinas/eventos).
  Resultado: dropar tabela no banco não se refletia no vault; regenerar até **recriava** os notes a partir do xlsx velho.
- **Correção (fonte da verdade = banco vivo):**
  - `1_extrair_rotinas.py` agora também gera `_mapdata/tables.json` e `views.json` do `information_schema`
    (Linhas, Tamanho MB, Colunas, Índices, Tem PK, Engine, Criada em, Comentário; `Categoria` por heurística de
    prefixo; `Alertas` derivado `sem PK`/`vazia`). Chaves iguais às da antiga aba do xlsx → mínimo remapeamento.
  - `3_gerar_vault.py` lê Tabelas/Views desses json (não abre mais o xlsx; `import openpyxl` removido).
    `Leituras/Escritas (3d)` exigem `performance_schema` (sem acesso) → renderizam `n/d`.
  - **xlsx aposentado como fonte.** `CLAUDE.md` (seções 2, 5-INGEST, 7) atualizado.
- **Efeito:** rodar `1_ → 3_ → 4_` agora reflete o banco automaticamente. As 28 tabelas dropadas somem do vault
  na próxima geração, sem editar nada à mão. Próximo passo após gerar: LINT de `[[wikilinks]]` quebrados p/ as 28.

## 2026-06-03 — EDIT (DROP do lote 1 EXECUTADO pelo time — 28 tabelas removidas)
- O time rodou `DB_instituto_experience/limpeza-drop-datado.sql` (backup `mysqldump` + DROP FK-safe).
  **As 28 tabelas do lote 1 não existem mais** no `instituto_experience`. Registro do que foi removido:
  Django/auth (7), Temp/scratch (4), Clickbank affiliate (3), Exports campanhas (3), Features de app (11)
  — lista completa em `[[limpeza-tabelas-vazias]]` e no script. Backup gerado pelo PASSO 0 é o ponto de retorno.
- **Histórico**: fica nesta entrada (append-only) + na doc curada `[[limpeza-tabelas-vazias]]` + nos `.sql`.
  As notas GERADAS (`DB_instituto_experience/Tabelas/…`) só refletem o estado atual e serão sobrescritas na regeração.
- **Pendência de regeração** (não é automática): `3_gerar_vault.py` lê a lista de tabelas do **xlsx**
  (`inventario_banco_instituto_experience.xlsx`), que ainda lista as 28. Regenerar sem atualizar o xlsx
  **recria** os 28 notes. Passo correto: remover as 28 linhas da aba `Tabelas` do xlsx → `1_extrair_rotinas.py`
  → `3_gerar_vault.py` → `4_gerar_indice.py`. Depois, LINT de wikilinks quebrados apontando p/ as 28.

## 2026-06-03 — LINT (limpeza lote 2: quarentena de 5 órfãs dashboard/gold + armadilha `_aws_new`)
- **Lote 1 (as 28)**: decisão do time = **DROP direto** (sem quarentena), conjunto conhecido/baixo risco.
  `limpeza-drop-datado.sql` reescrito p/ dropar os nomes originais (PASSO 0 = backup `mysqldump` obrigatório,
  PASSO 1 = DROP FK-safe com `FOREIGN_KEY_CHECKS=0`, PASSO 2 = conferência). Doc com `status: drop-direto-aprovado-28`.
- **Armadilha nova registrada — sufixo `_aws_new` é alvo de swap atômico** (igual a `_stage`/`_old`):
  `clickbank_physical_new_aws_new` (criada hoje 13:01, 0 linhas), `gold_clickbank_aws_new` e
  `dashboard_channels_marketing_aws_new` estavam vazias só porque são o ALVO do swap — as irmãs vivas
  `clickbank_physical_new_aws` (330k, escrita hoje 13:39), `gold_clickbank_aws` (216k, escrita hoje 13:41) e
  `dashboard_channels_marketing_aws` (47k) estão ativas. **Nunca entram em limpeza.** (Regra a refletir na skill.)
- **Lote 2 (quarentena por RENAME → `_zzdrop_`)**: 5 órfãs dashboard/gold, todas confirmadas vazias por `COUNT(*)`,
  sem irmão de swap vivo, sem ref. estática (proc/func/event/view), sem FK apontando, sem trigger, `UPDATE_TIME` NULL.
  Incógnita = leitura externa (Looker/n8n) → quarentena testa o uso real. Script: `limpeza-quarentena.sql` (reescrito
  do lote 1, agora com as 5): `clickbank_physical_v2`, `dashboard_cartpanda_pais_diario`, `dashboard_dim_gestorl`,
  `dashboard_gerenciador_unificado`, `dashboard_partner_affiliates`. Observar até ~2026-06-17, reverter se quebrar.

## 2026-06-03 — LINT (limpeza: 27 tabelas vazias candidatas + criação da skill `limpeza-banco`)
- Skill `limpeza-banco` criada em `.claude/skills/limpeza-banco/` (SKILL.md + `references/queries.sql`):
  procedimento versionado p/ achar tabelas/views excluíveis com segurança e gerar scripts (nunca executa DDL).
- Rodada ao vivo no `instituto_experience`: **28 tabelas** confirmadas vazias (`COUNT(*)` real, não estimativa),
  sem ref. em procedure/function/event/view, sem FK externa/trigger, sem escrita (`UPDATE_TIME` NULL, uptime ~7,7d).
- **Leitura externa NÃO confirmável** (`tadeu_lopes` sem `performance_schema`) → plano de **quarentena por RENAME**
  (`_zzdrop_`) antes do DROP. Artefatos: `DB_instituto_experience/limpeza-tabelas-vazias.md`,
  `limpeza-quarentena.sql`, `limpeza-drop-datado.sql`. Execução pelo DBA (MCP é read-only).
- Armadilhas registradas na skill (descobertas nesta limpeza): estimador InnoDB mente (10 "vazias" tinham 1 linha);
  `_old`/`_stage` são transitórios de swap de tabelas vivas (a `tb_gex_buygoods_unified_old` sumiu no meio da sessão);
  `clickbank_physical_new_aws_new` criada hoje (build em andamento) ficou de fora; view vazia ≠ view morta.

## 2026-06-02 — INGEST (documentação da fonte Buygoods: gold + amostras webhook/api)
- Pasta `Documentações Fontes de Dados/Buygoods/` (renomeada pelo time, era `Fontes de Dados/`).
- Recebidos 3 arquivos crus e **convertidos para Markdown nativo** (versionável/pesquisável):
  - `doc_gold_buygoods.docx` → **`doc_gold_buygoods.md`** (espec. técnica da camada gold v2.0: 75 colunas,
    agrupamento por janela temporal de 240min, fonte `tb_gex_buygoods_unified` → `dashboard_gold_buygoods`).
    Convertido via parse stdlib do .docx (sem pandoc/python-docx instalados).
  - `amostra_webhook_buygoods.csv` → **`amostra_webhook_buygoods.md`** (92 colunas; action_type: neworder,
    newcustomer, cancel, refund, abandon).
  - `amostra_api_buygoods.csv` → **`amostra_api_buygoods.md`** (130 colunas; inclui subid/cogs/merchant_commission).
- Arquivos crus (.csv/.docx) mantidos na pasta como backup. Nota-índice `[[Buygoods]]` atualizada com os links.
- Pendência: receber os docs das **silver** (webhook e api) p/ fechar o pipeline webhook/api → silver → gold.

## 2026-06-02 — EDIT (2 eventos affiliate_nutra desabilitados — redundantes com sp_master_run_all)
- `evt_refresh_dashboard_affiliate_nutra` e `evt_refresh_dashboard_affiliate_nutra_usd` (rodavam a cada 10min)
  **desabilitados pelo time** via `ALTER EVENT ... DISABLE`. **Status confirmado via MCP: ambos DISABLED.**
- Motivo: as procedures que eles chamam já são chamadas por `sp_master_run_all` (evento `ev_master_dashboard_refresh`,
  60min) — verificado que é a única rotina que as referencia. Trade-off aceito: refresh desses 2 dashboards passa de 10→60min.
- Notas geradas em `DB_instituto_experience/Eventos/` tiveram o status corrigido p/ DISABLED (regeração relê do banco).
- Decisão registrada (curada, sobrevive a regeração): `[[Decisao-2026-06-02-desabilita-eventos-affiliate-nutra]]`.

## 2026-06-02 — EDIT (pasta `Fontes de Dados/` — documentação de plataformas + onboarding)
- Criada pasta curada `Fontes de Dados/` (transversal, no root) para documentar as **fontes/plataformas**.
- Artefatos-chave: `_template-fonte.md` (modelo) e `_onboarding-nova-fonte.md` (checklist passo a passo)
  — objetivo é **onboarding rápido** de fontes novas usando o que sabemos das atuais como gabarito.
- Subpastas das 3 fontes atuais, cada uma com `<Plataforma>.md` (índice) + `API.md` + `Webhook.md` +
  `Mapeamento.md` + `exemplos/` (arquivos crus: api-response.json, webhook-payload.json, pull_script.py):
  **Clickbank** (principal), **Buygoods** (principal, recente), **Cartpanda** (legado).
- Notas-índice já linkadas via `[[wikilinks]]` às tabelas reais que cada fonte alimenta
  (ex.: Clickbank→`[[clickbank_physical_new_aws]]`/`[[dashboard_gold_clickbank]]`; Cartpanda→`[[cartpanda_physical]]`).
- `CLAUDE.md` atualizado (estrutura de pastas inclui `Fontes de Dados/` e `Dashboards/`; `API/` removida).

## 2026-06-02 — INGEST/EDIT (análise de tabelas essenciais + mapa de migração + pasta Dashboards)
- **Análise das tabelas essenciais** (geradas pelas procedures dos 7 eventos ATIVOS): script
  `Inventario MSQL/5_essenciais.py` + derivação de finais via detecção de `RENAME TABLE` (swap atômico).
  Resultado: **37 tabelas finais** (27 via swap `_stage`→final, 10 por write direto). As `_stage`
  são scratch do swap e NÃO migram; as 37 tabelas-fonte (só leitura) ficam no instituto_experience.
  Saídas: `_mapdata/essenciais.json` e `_mapdata/finais.json`.
- **Mapa de migração** para o `data_team` criado e movido para dentro da pasta-banco:
  `DB_instituto_experience/migracao-data_team-mapa.md` (coluna `novo_nome` a preencher pelo time;
  total ≈ 7 GB). Próximo passo: gerar script `CREATE TABLE … LIKE` + `INSERT … SELECT` (executado pelo DBA).
- **Pasta `API/` removida** (soft-delete → `.trash/API`, recuperável).
- **Pasta `Dashboards/` criada** (curada) com `_sobre.md`: documentar os dashboards do Looker Studio
  (link, fontes de dados como `[[wikilinks]]`, evento/procedure que atualiza, métricas).

## 2026-06-02 — EDIT (padrão de pastas-banco DB_<schema> + índice por banco)
- Pastas-banco renomeadas para o padrão `DB_<schema>`: `instituto_experience/`→`DB_instituto_experience/`,
  `data_team/`→`DB_data_team/`.
- Cada banco passou a ter o **seu próprio `00-Indice.md`** dentro da pasta:
  `00-Indice.md` (root) → `DB_instituto_experience/00-Indice.md`; `00-data_team.md` → `DB_data_team/00-Indice.md`.
- Convenção: como há vários `00-Indice.md`, links sempre com caminho (`[[DB_data_team/00-Indice]]`).
- Dataview e referências atualizadas; scripts ajustados (`3_gerar_vault.py` e `4_gerar_indice.py` usam `DBDIR='DB_'+DB`
  e escrevem o índice dentro da pasta-banco). `CLAUDE.md` atualizado.

## 2026-06-02 — INGEST (banco data_team criado)
- Banco `data_team` criado no RDS (marts/tabelas próprias do time). Confirmado via MCP: visível e legível.
- Estado: **vazio** (0 tabelas/views/procedures/eventos).
- Criada pasta `data_team/` + nota-índice [[00-data_team]]. Índice geral [[00-Indice]] agora lista os 2 bancos.
- Pendência: parametrizar os scripts (`1_extrair_rotinas.py`, `3_gerar_vault.py`) para multi-schema
  quando o primeiro objeto do `data_team` existir.

## 2026-06-02 — EDIT (remoção de Runbooks)
- Removidos `Conhecimento/Runbooks/` e o template `Templates/runbook.md` (soft-delete → `.trash/`, recuperável).
- Referências limpas em `CLAUDE.md` e `_sobre-esta-pasta.md`.

## 2026-06-02 — EDIT (pastas curadas promovidas ao root)
- Movidas para o ROOT (artefatos de trabalho): `Fluxos-N8N/`, `Epicos/`, `Incidentes/`.
- Permanecem em `Conhecimento/` (saber sobre os dados): `Dossies/`, `Calls/`, `Decisoes/`, `Runbooks/`.
- Criadas 3 pastas novas no root, cada uma com `_sobre.md`: `Pipelines/`, `API/`, `Planilhas Manuais/`.
- `CLAUDE.md` reescrito com a regra mestra: única divisão que importa é GERADO (pasta-banco) vs CURADO (resto).
- `_sobre-esta-pasta.md` atualizado.

## 2026-06-02 — EDIT (pastas de destino em Conhecimento/)
- Criadas 7 subpastas curadas (uma por tipo de template), cada uma com `_sobre.md`:
  `Conhecimento/Dossies, Fluxos-N8N, Epicos, Calls, Decisoes, Incidentes, Runbooks`.
- Esclarecimento: templates (em `Templates/`) são modelos; as notas reais moram nessas subpastas.
- `_sobre-esta-pasta.md` atualizado com tabela de subpastas × template.

## 2026-06-02 — EDIT (reorganização por banco + mais templates)
- Importados +3 templates do VaultForge: `call.md`, `epico.md`, `fluxo-n8n.md` (total: 9 em `Templates/`).
  `fluxo-n8n` mantém os enums reais da BHG (plataformas, hosts n8n) e aponta o MySQL para `instituto_experience`.
- **Reorganização por banco**: notas geradas movidas de `Tabelas/Views/Rotinas/Eventos/` para
  `instituto_experience/Tabelas|Views|Rotinas|Eventos/`. Prepara o vault para o futuro `data_team/`.
- Transversais (`Templates/`, `Conhecimento/`, `CLAUDE.md`, `log.md`, `00-Indice.md`) ficam no root.
- Scripts ajustados: `3_gerar_vault.py` (var `DB`/`GEN`, escreve sob a pasta-banco) e `4_gerar_indice.py`
  (Dataview `FROM "instituto_experience/..."`). `00-Indice.md` atual também corrigido.
- Wikilinks `[[...]]` não quebram: resolvem por nome de arquivo em todo o vault.

## 2026-06-02 — EDIT (templates curados)
- Importados e adaptados 4 templates do VaultForge (davioliveeira/obsidian-vaults-templater) para `Templates/`:
  `dossie-tabela.md`, `runbook.md`, `decisao.md`, `incidente.md`.
- Adaptações: português, schema `instituto_experience` (era `leads_pipeline`), frontmatter compatível com o Dataview do vault,
  links para as notas geradas (`[[...]]`) e destino na camada curada `Conhecimento/`.
- Objetivo: dar profundidade narrativa às páginas curadas sem mexer nas notas geradas (Tabelas/Views/Rotinas/Eventos).

## 2026-06-02 — INGEST (baseline)
- Geração inicial do vault a partir do banco `instituto_experience`.
- Fontes: inventário `.xlsx` (382 tabelas + 92 views) e `_mapdata/*.json` (54 procedures, 1 function, 31 eventos).
- Criadas 559 notas com dependências como `[[links]]`; índice `00-Indice.md` gerado.
- Adotado o padrão LLM Wiki: criados `CLAUDE.md` (schema), este `log.md` e a pasta `Conhecimento/`.
