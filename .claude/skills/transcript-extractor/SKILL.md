---
name: transcript-extractor
description: Use when turning a meeting transcript (Loom or Fathom export) into a structured note in this vault — after a 1:1, FCA, brainstorm, planning session, working/mentoring session, comitê, or partner call, or when asked to process a transcript from "Sistema/_raw_files/reuniões/pendente/".
---

# Transcript Extractor

## Overview
Turns a raw call transcript (Loom or Fathom) into a structured meeting note in the right vault folder, links every participant as a `[[wikilink]]`, and updates the related entities (pessoas, áreas, parceiros, projetos). Built for the GEX strategic vault.

**Core principle:** never file anything until the allocation metadata — participantes, data, tipo, área(s)/parceiros, destino — is confirmed with the user.

## When to use
- The user runs `/transcript-extractor`, usually with a short free-text context ("brainstorm de atendimento e produto com a Tati e o Gustavo, ~20/mai").
- A transcript lands in `"Sistema/_raw_files/reuniões/pendente/"` and needs structuring.
- After any recorded meeting: 1:1, FCA, brainstorm, planejamento, sessão de trabalho, comitê, parceiro.

## Workflow
1. **Get the transcript** — from the path/context the user gave; else the newest file in `"Sistema/_raw_files/reuniões/pendente/"`; else pasted text.
2. **Detect format & parse** — Loom vs Fathom differ a lot; see `references/formats.md`. Normalize noisy entity names (e.g. "Ebolêvis"→Eagle Labs, "Byroots"→MyRoots).
3. **Resolve allocation metadata** in this order: (a) user context → (b) inference from the transcript → (c) **ask the user**. Required: participantes, data, tipo, área(s)/parceiros, destino.
4. **CONFIRM before writing** — show the allocation plan (destino + entidades a criar/atualizar). Anything missing or uncertain → ask, never guess. Wait for explicit OK.
5. **Write** — create the note (structure below), `[[link]]` every participant, create/update related entities from their `_Modelo`/`_Template`. **Sempre retenha o cru:** se o transcript veio como arquivo em `pendente/`, mova-o para `"Sistema/_raw_files/reuniões/processado/"`; se veio como **texto colado**, salve-o verbatim em `"Sistema/_raw_files/reuniões/processado/"` como `YYYY-MM-DD <Tipo> — <Tema>.md` (mesmo nome-base da nota). **Nunca destile sem guardar o cru** — vale para toda reunião, mesmo as coladas.

## Routing (tipo → pasta)

A nota destilada mora na **entidade dona** da reunião (mesma régua do vault: casa = dono). Não existe mais pasta global de Reuniões.

| Tipo | Destino |
|---|---|
| 1:1 individual | `Pessoas/<Nome>/1on1/` |
| FCA / performance de squad (líder + time apresentam a área) | `<área>/Reuniões/` (linka o líder e os participantes; **não** vai na pasta da pessoa) |
| Brainstorm (tático) | `<área dona>/Reuniões/` (se gerar decisão, a decisão vira nota própria em `<área>/Decisões/`) |
| Planejamento de uma área | `<área>/Reuniões/` |
| Sessão de trabalho (mentoria/build — alguém mostra/ensina ou constrói junto; **não é feedback**) | `<área>/Reuniões/` |
| Comitê / transversal sem dono de área | `Empresa/Comitês/` |
| Parceiro | `Parceiros/<nome>/Reuniões/` |

`<área>` = `BUs/<área>/` ou `Departamentos/<área>/`. **Multi-área:** armazene sob a **área primária** (1ª da lista) e mantenha as demais em `areas:`/`impacta:` no frontmatter. Se a reunião teve um roteiro de prep, feche o loop: marque o Guia em `Guias de Reunião/` como `status: realizada` e aponte `resultou_em: [[esta nota]]`.

Naming: `YYYY-MM-DD <Tipo> — <Tema>.md`.

## Output structure (note body)
Frontmatter (`tipo`, `data`, `participantes` as wikilinks, `areas`, `fonte`/URL, `tags`) + sections:
1. **Resumo executivo**
2. **Discussão detalhada (pontos + porquês)** — sempre traga o PORQUÊ de cada ponto; é o que dá contexto pra decidir no futuro.
3. **Decisões**
4. **Action items** — tabela `ação · responsável · área · âncora`. Em Fathom, use os `ACTION ITEM` nativos e os links `?timestamp=` como âncora.
5. **Pontos em aberto / riscos**

## Entity updates
- **Pessoas:** acrescenta os action items dela + link da reunião. Reuniões coletivas dependem do `[[link]]` na nota → o histórico da pessoa aparece nos **backlinks**.
- **Áreas (hub):** acrescenta em "Decisões recentes" / "FCAs recentes" / "Projetos".
- **Parceiros:** atualiza status/regras.
- Cria entidade ausente a partir do `_Modelo`/`_Template` — sempre no passo de confirmação.

## Common mistakes
- Arquivar antes de confirmar metadados. Sempre confirme.
- Loom: inventar quem falou. Loom não tem locutor — infira com cautela e confirme os participantes.
- Cortar os "porquês" — é a parte mais valiosa.
- Esquecer de `[[linkar]]` os participantes — quebra o histórico de reuniões por pessoa.
- **Destilar transcript colado sem salvar a versão crua no `_raw_files`.** Toda reunião deixa cópia crua — texto colado também (materialize como arquivo).
