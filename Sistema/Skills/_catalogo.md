---
tipo: indice
gerado_por: skill/catalogo-skills
atualizado_em: 2026-06-09
tags: [sistema, skills, moc]
---
# 🧩 Catálogo de Skills

> GERADO por `catalogo-skills`. Não editar à mão — rode a skill de novo.
> As skills ficam em `.claude/skills/<nome>/SKILL.md`. Total atual: **7**.

## Por categoria

### Catalogação / Documentação
| Skill | O que faz | Quando usar (gatilhos) |
|---|---|---|
| `catalogo-datalake` | Cataloga o Data Lake da AWS (Glue + ETL Jobs + Crawlers + Step Functions + EventBridge) e gera/atualiza a pasta `Arquitetura/Data Lake/` — 1 nota por tabela/job/crawler/SFN + índice + mapa de orquestração. Só leitura na AWS. | "data lake", "glue", "athena", "bronze/silver/gold", "documentar os jobs", "orquestração", "crawlers", "agendamentos", "atualizar o data lake". |
| `catalogo-skills` | Varre `.claude/skills/` e gera este catálogo (o que faz / quando usar por skill). | "catálogo de skills", "quais skills eu tenho", "atualizar catálogo"; **após criar/editar uma skill**. |

### Manutenção / Qualidade
| Skill | O que faz | Quando usar (gatilhos) |
|---|---|---|
| `limpeza-banco` | Metodologia para caçar tabelas/views excluíveis com segurança (read-only): investiga, gera scripts `.sql` de quarentena/DROP e documenta — nunca executa DDL. | "limpeza de banco", "tabelas/views não usadas", "o que posso apagar", "tabela vazia", "view quebrada". |
| `organizar-eventos` | Separa as notas de eventos do MySQL em `Eventos/ENABLE` (ativos) e `Eventos/DISABLE` (inativos), lendo o STATUS real em `information_schema.EVENTS`. Read-only no banco; só move `.md`. | "separar/organizar eventos", "eventos ativos/inativos", "ENABLE/DISABLE", "quais events estão rodando"; após ligar/desligar um event no banco. |

### Ingestão de conhecimento
| Skill | O que faz | Quando usar (gatilhos) |
|---|---|---|
| `transcript-extractor` | Transforma transcrição de reunião (Loom/Fathom) em nota estruturada na entidade dona; linka participantes e atualiza entidades. Confirma metadados antes de salvar. | `/transcript-extractor`; após 1:1, FCA, brainstorm, planejamento, sessão de trabalho, comitê ou call de parceiro; transcript em `pendente/`. ⚠️ ver compatibilidade abaixo. |
| `populate` | Destila um dump **solo** (texto, brainstorm transcrito, doc `.md` de área) numa **Captura de Contexto** e distribui o conhecimento nas entidades. NÃO é para reunião com vários locutores. | `/populate`, "popula o vault com isso". ⚠️ ver compatibilidade abaixo. |

> ⚠️ **Compatibilidade (instaladas como o CTO enviou):** `transcript-extractor` e `populate` foram
> escritas para o **vault estratégico do Gabriel** e assumem caminhos/estrutura diferentes dos seus
> (`Sistema/_raw_files/`, `BUs/`, `Departamentos/`, `Parceiros/`, `Pessoas/<Nome>/1on1/`, `_Templates`,
> "Gabriel é o dono"). Também dependem de arquivos `references/formats.md` e `references/routing.md`
> **ainda não recebidos**. Ver [[Decisao-2026-06-04-reorganizacao-pastas-vault]] — adaptar após alinhar a estrutura.

### Sincronização / Memória
| Skill | O que faz | Quando usar (gatilhos) |
|---|---|---|
| `sincronizar-conhecimento` | Espelha o conhecimento **de empresa** da memória local do Claude (`~/.claude/.../memory/`) para a base versionada no repo, para viajar no git. Não espelha o que é pessoal/segredo. Não commita. | `/sincronizar-conhecimento`, "sincronizar conhecimento", "atualizar a base de conhecimento", "passar a memória pro Obsidian"; após sessão com aprendizado novo de empresa. ⚠️ compatibilidade abaixo. |

> ⚠️ **Compatibilidade:** assume `Sistema/Base de Conhecimento (Claude)/`, a **regra de espelhamento no `CLAUDE.md`** e uma skip-list específica do Gabriel (Gabriel/Gustavo/diretoria). Adaptar ao nosso vault na reorg.

## Como criar / editar uma skill
- Crie a pasta `.claude/skills/<nome>/SKILL.md` com frontmatter `name` + `description`.
- A `description` é o que **dispara** a skill — seja específico nos gatilhos (o Cloud lê isso antes de responder).
- Rode `catalogo-skills` depois para atualizar este índice.

## 🔜 Skills planejadas / pendentes
> Ainda **não instaladas**.
- `onboard-gateway` — onboarding padronizado de uma nova fonte/gateway (amostra → de-para → bronze/silver/gold). (A construir — prioridade nº 1 das calls Gabriel + Davi.)
- **`references/` pendentes:** `transcript-extractor/references/formats.md` e `populate/references/routing.md` (citados pelas skills, ainda não recebidos).
