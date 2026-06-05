---
name: populate
description: Use when turning a solo knowledge dump into structured vault notes — raw text, a transcribed brainstorm/voice idea, or a consolidated .md area document — to be distilled and distributed across the GEX vault entities. Triggered by /populate or "popula o vault com isso". NOT for recorded multi-speaker meetings (use transcript-extractor).
---

# Populate

## Overview
Pega um dump de conhecimento solo (texto cru, ideia gravada+transcrita, ou um `.md` consolidado de área) e popula o vault GEX: cria uma **nota-âncora Captura de Contexto**, preserva o raw no staging, e **destila e distribui** o conhecimento nas entidades (Áreas, Pessoas, Parceiros, Projetos, Decisões, Regras, Playbooks, Indicadores, OKRs), tudo `[[linkado]]` de volta à Captura.

**Princípio central:** enriquecer entidades que já existem é livre; **criar qualquer nota nova é sempre uma proposta que passa pela sua confirmação**. Nunca crie nem arquive nada antes do OK. Isso protege o minimalismo deliberado do vault (`Painel/Sobre este Vault.md`).

**REQUIRED BACKGROUND:** esta skill reusa as convenções da `transcript-extractor` (normalização de nomes, `[[wikilinks]]`, fluxo raw→processado, preservar os porquês). Leia-a para o que é compartilhado; aqui está só o **delta**.

## Isto NÃO é o transcript-extractor
A falha #1 é tratar o dump como uma reunião. **Não é.**

| | transcript-extractor | populate (esta) |
|---|---|---|
| Input | Conversa gravada (Loom/Fathom, vários locutores) | Dump solo: texto, ideia transcrita, doc consolidado |
| Artefato central | Nota de **reunião** roteada pra entidade (`<área>/Reuniões/`, `Pessoas/<nome>/1on1/`, etc.) | **Captura de Contexto** em `_Sistema/Capturas (log de populate)/` |
| Foco | Logar a reunião | Distribuir conhecimento nas entidades |

**Guardrail:** se o conteúdo tiver timestamps + locutores, cabeçalho Fathom, ou for claramente uma conversa entre pessoas → **pare e sugira `transcript-extractor`**.

## When to use
- Você roda `/populate` e cola/aponta um contexto.
- Um doc consolidado de área (`.md`) precisa virar canon distribuído.
- Uma ideia/brainstorm solo gravado e transcrito.
- Texto cru geral que carrega conhecimento a estruturar.

## Workflow
1. **Obter & classificar** — pegue o contexto (texto colado ou caminho) e classifique o modo: `documento` · `brainstorm` · `texto`.
2. **Guardrail** — parece transcript de reunião? → sugira `transcript-extractor` e pare.
3. **Destilar** — extraia o conhecimento preservando o **PORQUÊ** de cada ponto. Case cada item contra entidade existente **primeiro** (normalize nomes). Detalhes de roteamento e regras: `references/routing.md`.
4. **Montar o plano de alocação** — agrupado por tipo: a Captura + entidades a **atualizar** (existentes) + notas a **criar** (cada uma marcada como proposta).
5. **CONFIRMAR** — mostre o plano completo. **Nada é escrito antes do OK explícito.** Item incerto → pergunte, nunca invente.
6. **Executar** — crie a Captura; **salve o raw verbatim como arquivo** em `pendente/` (mesmo se o conteúdo foi **colado** — nada é destilado sem reter o cru; nome `YYYY-MM-DD <Tema>.md`); crie/atualize cada nota a partir do template; `[[linke]]` tudo de volta à Captura (e a Captura para tudo); mova o raw para `…/processado/`.

## Input → staging
| Modo | Staging do raw |
|---|---|
| `documento` (.md consolidado) | `"_Sistema/_raw_files/documentos/pendente/"` → `"…/documentos/processado/"` |
| `brainstorm` / `texto` | `"_Sistema/_raw_files/notas/pendente/"` → `"…/notas/processado/"` |

**Nunca** stageie em `"_Sistema/_raw_files/reuniões/"` — essa pasta é só para transcrições de **reunião**.

## A âncora: Captura de Contexto
- Local: `_Sistema/Capturas (log de populate)/` (maquinário, não conteúdo). Nome: `YYYY-MM-DD Captura — <Tema>.md`.
- Template: `"_Sistema/_Templates/_Template Captura.md"` (`tipo: captura`, `origem`, `fonte`→raw, `areas`, `participantes`, `tags: [captura]`).
- Seção **Conhecimento destilado** lista, por tipo, links de tudo que a Captura populou — é o índice de rastreabilidade.

## Regras de entidade (o delta que falha sem a skill)
- **Existente primeiro:** sempre case contra a nota existente antes de propor uma nova (ex.: hub `Dados` já existe → atualiza, não cria).
- **Pessoa externa → Parceiro, não Pessoa.** Alguém de fora (consultor, parceiro) vira/atualiza a nota em `Parceiros/<empresa>/`, referenciada por `[[wikilink]]`. **Não** crie uma pasta de Pessoa interna para externos. Crie o Parceiro se não existir.
- **Camada operacional sob demanda:** Regras/Playbooks/Indicadores vão para `<área>/Operação/{Regras de Negócio,Playbooks,Indicadores}/`. A subpasta `Operação/` nasce sob demanda — **propor criar a nota operacional faz parte do plano**, nunca silenciosamente. Sem aprovação, registre no hub da Área.
- **Gabriel é o dono do vault.** Não crie nota de Pessoa para ele. Em capturas solo ele é o autor implícito, não um "participante" a `[[linkar]]` — deixe `participantes` vazio se só houver ele.

## Common mistakes
- **Criar nota de reunião em `Reuniões/`** em vez de Captura em `Capturas/`. É o erro mais comum — releia "Isto NÃO é o transcript-extractor".
- **Executar sem confirmar.** Criou Pessoa/Projeto/Decisão sem plano aprovado = violação do princípio central.
- **Stagear o raw junto das transcrições de reunião.** Use `notas/` ou `documentos/`.
- **Destilar texto colado sem salvar o cru no `_raw_files`.** Todo dump deixa cópia crua — colado também (materialize como arquivo antes de destilar).
- **Transformar pessoa externa em Pessoa interna** e esquecer de criar o Parceiro.
- **Absorver indicador/regra em silêncio** sem propor a nota (ou a camada operacional).
- **Cortar os porquês** ao destilar — é a parte mais valiosa.
- **Esquecer de `[[linkar]]` de volta à Captura** — quebra a rastreabilidade do dump.
