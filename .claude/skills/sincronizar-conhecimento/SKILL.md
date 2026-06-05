---
name: sincronizar-conhecimento
description: Espelha o conhecimento de EMPRESA da memória local do Claude (~/.claude/.../memory/) para a base versionada no repo (Sistema/Base de Conhecimento (Claude)/), pra que viaje no git e deixe o vault inteligente pra qualquer pessoa que clona. Use quando o Tadeu pedir pra "sincronizar/transferir conhecimento", "atualizar a base de conhecimento", "passar a memória pro Obsidian", ou após uma sessão em que aprendeu fatos novos de empresa. Triggered by /sincronizar-conhecimento.
---

# Sincronizar Conhecimento (memória local → repo)

## Overview
A inteligência do Claude mora em **dois lugares** e só um viaja no git:
- **Memória local** `~/.claude/projects/<slug>/memory/` — fica na máquina de cada pessoa, NÃO vai pro repo.
- **Base de conhecimento** `Sistema/Base de Conhecimento (Claude)/` — **versionada no repo**, então qualquer pessoa que clona (hoje: diretoria — Tadeu + Léo) recebe.

Esta skill **espelha o que é conhecimento de EMPRESA** da memória local pra base versionada, pra que o repo fique cada vez mais inteligente e o nível de resposta seja o mesmo pra todo mundo. Roda em qualquer máquina (a do Tadeu ou a do Léo) — o que cada um aprende flui pro repo e, via `git pull`, chega no outro.

**Princípio:** a base de conhecimento é *espelho*, não original. A memória local é a fonte; esta skill propaga.

## Critério de sensibilidade (a regra-mãe)
**Conhecimento de EMPRESA → espelha. Coisa do indivíduo → NÃO espelha (fica só local).**
- ✅ **Espelha:** banco/dados, métricas, processos, ferramentas, ClickUp, pessoas da empresa, remuneração, comissionamento, dashboards, normalizações, decisões — tudo que ajuda alguém a trabalhar no negócio. O vault é da diretoria; não há nada de empresa pra esconder.
- ❌ **NÃO espelha (mantém só na memória local):**
  - Pessoal de um indivíduo: pasta/conteúdo pessoal (saúde, fono, finanças pessoais), perfil/preferências de estilo de uma pessoa específica (ex.: "o Tadeu prefere X", "o perfil técnico do Tadeu é Y").
  - One-off não-reutilizável: uma avaliação individual pontual, uma nota pessoal.
  - **Segredos/credenciais** (tokens, senhas) e **caminhos de máquina** como conteúdo — nunca. (Conhecimento sobre uma ferramenta tudo bem; o segredo em si, não.)
- **Skip-list conhecida (jun/2026):** `vault-pasta-pessoal`, `gabriel-perfil-tecnico-git`, `feedback-recomendacao-vs-menu`, `feedback-recap-pos-reuniao`. Na dúvida sobre um arquivo novo, pergunte ao Tadeu antes de espelhar.

## Processo

### 1. Localizar as duas pastas
- **Base (destino):** `Sistema/Base de Conhecimento (Claude)/` na raiz do vault.
- **Memória (origem):** a pasta de memória do Claude desta máquina. É `~/.claude/projects/<slug>/memory/`, onde `<slug>` é o caminho absoluto do projeto com `/` virando `-` (ex.: projeto `/Users/gabrielbngomes/gabriel-gex` → `-Users-gabrielbngomes-gabriel-gex`). Liste `~/.claude/projects/` e ache a que casa com o vault atual. Leia o `MEMORY.md` dela (índice).

### 2. Diferenciar
- Liste os `.md` da memória (fora `MEMORY.md`) e os `.md` da base (fora `_index.md`).
- **A espelhar** = memórias que (a) passam no critério de EMPRESA, (b) não estão na skip-list, e (c) ainda não existem na base **ou** estão desatualizadas (conteúdo da memória mudou). Para detectar desatualização, compare o corpo.

### 3. Portar cada uma (fidelidade total)
Para cada memória a espelhar, escreva um arquivo de MESMO nome na base, com:
1. Remova o frontmatter original (name/description/metadata/node_type/originSessionId) e qualquer `<system-reminder>` injetado.
2. Frontmatter novo mínimo: `---\ntags: [base-de-conhecimento]\n---`
3. Título `# <Título>` derivado do `description` original.
4. O **corpo verbatim** — não resuma, não corte. Mantenha `[[wikilinks]]`, tabelas, blocos de código, ⚠️.

### 4. Atualizar o índice
- Em `_index.md`, seção "## Notas já nesta base": garanta que a tabela lista TODAS as notas presentes (uma linha `| [[nome]] | descrição curta |` por arquivo).

### 5. Recibo
Reporte ao Tadeu: o que espelhou (novas + atualizadas), o que pulou e por quê (skip-list / pessoal / dúvida). **Não commite nem dê push** — isso é decisão do Tadeu (lembre que só chega no Léo após `commit` + `push`).

## Relação com a regra automática do CLAUDE.md
O `CLAUDE.md` já tem a **regra de espelhamento**: ao salvar uma memória de empresa, o Claude deve gravá-la também na base. Esta skill é a **rede de segurança** — reconcilia tudo de uma vez e pega o que passou batido (memórias antigas, ou salvas por um Claude que não seguiu a regra). Rode periodicamente ou ao fim de sessões com aprendizado novo.
