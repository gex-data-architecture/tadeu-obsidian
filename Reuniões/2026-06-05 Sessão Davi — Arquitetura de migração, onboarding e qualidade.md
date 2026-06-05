---
tipo: call
tipo_reuniao: sessão técnica (mentoria/alinhamento)
data: 2026-06-05
participantes: [Davi, Tadeu]
fonte: "resumo do calendário (sem transcript bruto)"
tags: [call, reuniao, conhecimento, migracao, onboarding, qualidade, mcp]
---
# 📞 Sessão Davi × Tadeu — Arquitetura de migração, onboarding e qualidade

> [!info] Resumo
> **Data**: 2026-06-05 (13:45–14:05 UTC) · **Tipo**: sessão técnica (alinhamento).
> Sem dado bruto/transcript — esta ata foi destilada a partir do resumo do calendário.
> Davi orientou sobre **migração `instituto_experience` → Data Team**, a **skill de onboarding de
> fontes (agnóstica a gateway)**, **MCP**, **hooks do Claude Code** e **qualidade de métricas (mediana)**.

## TL;DR
Discussão de arquitetura/estrutura do projeto de **migração de dados do Instituto Experience para o Data Team**:
nomenclatura de tabelas, **skill de onboarding de novas fontes** (BuyGoods/CartPanda/ClickBank → agnóstico a
qualquer gateway), padronização de eventos nos dashboards e **qualidade de dados (mediana vs média)**.
Davi recomendou como próximos passos: explorar **integrações MCP**, finalizar a **skill de onboarding** e
configurar **hooks no Claude Code** para automação do workflow.

## 🧱 Discussão detalhada (pontos + porquês)
- **Migração de dados oficiais** do Instituto Experience → **Data Team**. Criar **mapa de migração + de-para de
  tabelas**. Tabelas-alvo: **`tb_gold_clickbank`**, **`tb_gold_buygoods`** (derivadas da Gold). *Porquê:* organizar
  melhor a estrutura de dados na base consolidada.
- **Skill de onboarding de novas fontes (objetivo principal).** Cobrir o ciclo completo: **requisição na API →
  validação dos dados → montagem do de-para → bronze → silver → Gold**. Fontes atuais: **BuyGoods, CartPanda,
  ClickBank**. *Porquê:* tornar o processo **agnóstico a qualquer gateway de pagamento** (o gargalo 80/20 já
  apontado pelo Gabriel → [[2026-06-04 Sessão de trabalho — Estrutura e governança do vault (Gabriel)]]).
- **Documentação no Obsidian para o onboarding.** Criar **pasta de onboard com glossário de tabelas e
  palavras-chave**; manter **histórico atualizado de queries e ETLs**. *Porquê:* contexto reaproveitável e
  rastreável a cada nova fonte.
- **Qualidade de dados / dashboards.** Usar **mediana no lugar de média** em cálculos de eventos — médias são
  distorcidas por exceções (outliers). **Padronizar eventos** entre **SMS, e-mail e call center** (nem todo evento
  faz sentido em todo canal — ex.: *average time* de tag não faz sentido no e-mail). Revisar métricas nos
  **dashboards de auditoria**.
- **Ferramentas.** Claude Code no terminal para consultas; **N8N** para integrações; **MCP (Model Context
  Protocol)** para integração com o banco; Claude no Chrome para auditoria do BuyGoods.

## ✅ Decisões / direcionamentos
- A **skill de onboarding** é a prioridade e deve ser **agnóstica a gateway** (API → validação → de-para → bronze →
  silver → Gold).
- Adotar **mediana** como métrica padrão de eventos onde média distorce (auditoria de links/eventos).
- Avançar em **MCP** (já temos o MCP MySQL read-only) e em **hooks** do Claude Code para automação.

## 📌 Action items
| Ação | Responsável | Status |
|---|---|---|
| **Skill `onboard-gateway`** completa e agnóstica (API → validação → de-para → bronze → silver → Gold) | Tadeu | ⏳ a fazer |
| Criar **pasta de onboard** (glossário de tabelas + palavras-chave; histórico de queries/ETLs) | Tadeu | ⏳ a fazer |
| **Estudar e implementar integrações MCP** no projeto (ref.: GitHub do Davi — "Ponto Cloud"/Pontocloud) | Tadeu | ⏳ a fazer |
| **Configurar hooks do Claude Code** (executar skills automaticamente ao editar arquivos; exemplo no projeto do Davi) | Tadeu | ⏳ a fazer |
| **Atualizar cálculos de eventos** para **mediana** (auditoria de links/eventos) | Tadeu | ⏳ a fazer |
| **Padronizar eventos** nos dashboards de **SMS, e-mail e call center** (definir o que faz sentido por canal) | Tadeu | ⏳ a fazer |
| **Mapa de migração + de-para** `instituto_experience` → Data Team (`tb_gold_clickbank`, `tb_gold_buygoods`) | Tadeu | ⏳ a fazer |

## ⚠️ Pontos em aberto / riscos
- **Sem transcript bruto** desta call — ata baseada só no resumo do calendário (não há `_raw_files` para reprocessar).
- Falta a **referência concreta** do projeto do Davi para MCP e hooks (GitHub "Ponto Cloud" / exemplo de hooks).
- Padronização de eventos depende de **definir o catálogo de eventos por canal** (SMS/e-mail/call center).

## 🔗 Relacionados
- Call anterior: [[2026-06-04 Sessão de trabalho — Estrutura e governança do vault (Gabriel)]]
- Fontes: [[Fontes de Dados/Buygoods/doc_silver_buygoods]] · ClickBank · CartPanda
- Schema: [[CLAUDE]] · Diário: [[log]]
