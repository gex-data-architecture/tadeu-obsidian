---
name: catalogo-skills
description: >-
  Mantém o catálogo de skills do vault em `_Sistema/Skills/_catalogo.md` — varre
  `.claude/skills/*/SKILL.md`, lê o `name`/`description` de cada uma e gera uma tabela
  única com "o que faz" e "quando usar". Use SEMPRE que o usuário falar em "catálogo de
  skills", "quais skills eu tenho", "listar/atualizar as skills", "force update do catálogo",
  ou logo após **criar/editar/renomear/remover uma skill** (para o catálogo não ficar
  desatualizado) — mesmo sem dizer a palavra "skill". É só leitura de arquivos + escrita do
  catálogo; não altera as skills existentes.
---

# catalogo-skills

Resolve um problema simples e real: conforme as skills crescem, ninguém lembra o que cada
uma faz nem quando usar. Esta skill gera um **índice único** das skills instaladas, para o
humano (e o próprio Cloud) consultarem rápido.

## Quando rodar
- O usuário pede o catálogo / quer ver as skills.
- **Logo após** criar, editar, renomear ou apagar uma skill (mantém o catálogo em sincronia).
- Pedido de `force update`.

## Procedimento
1. **Listar** as pastas em `.claude/skills/` (cada subpasta com um `SKILL.md` é uma skill).
2. Para cada `SKILL.md`, ler o **frontmatter YAML**: `name` e `description`. Da `description`,
   separar mentalmente em duas partes:
   - **O que faz** (a ação/capacidade);
   - **Quando usar** (os gatilhos — geralmente a parte "Use … quando …").
3. **Classificar** por natureza (ajuste conforme o vault evolui):
   - `Catalogação / Documentação` (ex.: `catalogo-datalake`, `catalogo-skills`)
   - `Manutenção / Qualidade` (ex.: `limpeza-banco`)
   - `Ingestão de conhecimento` (ex.: transcrição de call, popular documento, sincronizar memória)
   - `Onboarding de fontes`
   - `Análise`
4. **Escrever** `_Sistema/Skills/_catalogo.md` (sobrescrever — é GERADO) no formato abaixo.
5. Acrescentar uma linha no topo de `log.md`: `## <data> — EDIT (catálogo de skills atualizado: N skills)`.

> Não invente skills. Liste apenas o que existe em `.claude/skills/`. Se uma `description`
> estiver vazia/ruim, sinalize "⚠️ descrição a melhorar" em vez de adivinhar.

## Formato do catálogo (`_Sistema/Skills/_catalogo.md`)
```markdown
---
tipo: indice
gerado_por: skill/catalogo-skills
tags: [sistema, skills, moc]
---
# 🧩 Catálogo de Skills

> GERADO por `catalogo-skills`. Não editar à mão — rode a skill de novo.
> Skills ficam em `.claude/skills/<nome>/SKILL.md`.

## Por categoria
### <Categoria>
| Skill | O que faz | Quando usar (gatilhos) |
|---|---|---|
| `nome-da-skill` | … | … |

## Como criar / editar uma skill
- Crie a pasta `.claude/skills/<nome>/SKILL.md` com frontmatter `name` + `description`.
- A `description` é o que dispara a skill — seja específico nos gatilhos.
- Rode `catalogo-skills` depois para atualizar este índice.
```

## Boas práticas (ao revisar uma skill no catálogo)
- `description` deve dizer **o que faz** E **quando usar** (gatilhos concretos), senão a skill
  "não dispara" na hora certa.
- Uma skill por responsabilidade; nomes em `kebab-case`.
- Mantenha o catálogo curto e escaneável — é um índice, não a documentação completa.
