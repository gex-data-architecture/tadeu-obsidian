---
title: Home
tags:
  - home
  - indice
---

# 🏠 Vault — Time de Dados GEX

Ponto de partida do vault. Base de conhecimento viva do time/plataforma de dados do banco `instituto_experience` (MySQL/RDS) e do Data Lake AWS (Glue/Athena).

> [!info] Quem somos
> Time de Dados GEX: ingestão, arquitetura medalhão (Bronze/Silver/Gold no S3), modelagem e visualização dos dados de gateways de venda (BuyGoods, Clickbank, Cartpanda) e Ads (Facebook, Google).
> **Eng. de dados**: Léo · **Data viz / docs**: Tadeu · **Lambda Ads (externo)**: Victor · **CTO**: Gabriel
> Detalhe em [[Sistema/Onboarding/Quem-Faz-O-Que|Quem faz o quê]].

---

## 🚦 Por onde começar

> [!tip] Primeira vez aqui?
> Vai direto pro [[Sistema/Onboarding/_index|Onboarding]]. Em ~30min você entende a stack, o glossário e quem faz o quê.

| Você quer...                                       | Vai pra                                                                  |
| -------------------------------------------------- | ------------------------------------------------------------------------ |
| Entender a stack e a arquitetura medalhão          | [[Sistema/Onboarding/_index\|Onboarding]] · `Arquitetura/`               |
| Ver o schema de um banco MySQL                     | [[Banco de Dados/MySQL/instituto_experience/00-Indice\|instituto_experience]] |
| Navegar o Data Lake (Glue/Athena, bronze/silver/gold) | [[Arquitetura/Data Lake/00-Data-Lake\|Data Lake]]                     |
| Entender uma fonte de dados / gateway              | `Fontes de Dados/<Plataforma>/`                                          |
| Ver uma regra de negócio ou indicador              | `Operação/`                                                              |
| Conferir uma validação de conta/plataforma         | `Operação/Validações/`                                                   |
| Ler uma decisão (ADR)                              | `Decisões/`                                                              |
| Ver o que o time está construindo                  | `Projetos/`                                                              |
| Saber o significado de um termo                    | [[Sistema/Onboarding/Glossario\|Glossário]]                             |
| Saber quais skills/comandos existem                | [[Sistema/Onboarding/Skills-e-Comandos\|Skills e Comandos]]             |

---

## 🗺️ Mapa rápido da plataforma

- **MySQL/RDS** `instituto_experience` (analítico, fonte da verdade hoje) → [[Banco de Dados/MySQL/instituto_experience/00-Indice|Índice instituto_experience]]
- **MySQL** `data_team` (em migração) → [[Banco de Dados/MySQL/data_team/00-Indice|Índice data_team]]
- **Data Lake AWS** (S3 + Glue + Athena, medalhão Bronze/Silver/Gold) → [[Arquitetura/Data Lake/00-Data-Lake|Data Lake]]
- **Fontes conectadas no S3**: BuyGoods, Clickbank · **pendente**: Cartpanda (retroativo)
- **Fontes híbridas (N8N legado)**: Facebook Ads, Google Ads (Lambda do Victor → migrar pro S3)
- **Visualização**: migração Looker → Lovable (conexão direta ao S3)

---

## 📐 Como o vault é organizado

Duas regras mestras (detalhe no [[CLAUDE]]):

- **GERADO vs CURADO** — `Banco de Dados/MySQL/<db>/{Tabelas,Views,Rotinas,Eventos}` e `Arquitetura/Data Lake/` são **sobrescritos** por scripts/skills. Não escreva conhecimento manual neles. Insight/decisão/narrativa vão na **entidade dona** (`Decisões/`, `Reuniões/`, `Fontes de Dados/`).
- **Casa = dono** — a nota mora na entidade que a possui (pessoa, parceiro, projeto, banco, domínio), não num balde por tipo.

> [!warning] Fonte da verdade = banco vivo
> O MCP `mysql` é **read-only**. O inventário de tabelas/views vem do banco (`information_schema`), não de planilha. Tabela dropada some do vault na próxima regeração.

---

## 📂 Pastas

| Pasta | O quê |
|---|---|
| `Banco de Dados/MySQL/<db>/` | Schema por banco (Tabelas/Views/Rotinas/Eventos) — **GERADO** |
| `Arquitetura/` | Stack, medalhão, Data Lake (**GERADO**), Migração data_team |
| `Fontes de Dados/<Plataforma>/` | BuyGoods, Clickbank, Cartpanda… + onboarding de gateway |
| `Dashboards/` | Looker Studio (em migração p/ Lovable) |
| `Operação/` | Regras de negócio · indicadores · `Validações/` · N8N · Planilhas · Lints |
| `Decisões/` | ADRs e decisões datadas |
| `Reuniões/` · `Pessoas/<Nome>/1on1/` | Reuniões internas e 1on1s |
| `Parceiros/<empresa>/` | Consultorias/fornecedores |
| `Projetos/` · `Incidentes/` | Épicos e postmortems |
| `Sistema/` | A máquina do vault: templates, raw files, skills, base de conhecimento, onboarding |

**Legenda de status**: 🟢 ativo · 🟡 a criar · 🔴 backlog · ⚪ rascunho
