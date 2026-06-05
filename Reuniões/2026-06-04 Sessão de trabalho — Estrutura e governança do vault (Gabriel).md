---
tipo: call
tipo_reuniao: sessão de trabalho (mentoria)
data: 2026-06-04
participantes: [Gabriel (CTO), Tadeu]
fonte: "[[2026-06-04 Sessão — Estrutura do Vault (Gabriel)]]"
tags: [call, reuniao, conhecimento, vault, governanca]
resultou_em: "[[Decisao-2026-06-04-reorganizacao-pastas-vault]]"
---
# 📞 Sessão Gabriel × Tadeu — Estrutura e governança do vault

> [!info] Resumo
> **Data**: 2026-06-04 · **Tipo**: sessão de trabalho/mentoria (Gabriel mostra o vault dele e orienta).
> Transcript cru: [[2026-06-04 Sessão — Estrutura do Vault (Gabriel)]]. Decisão gerada: [[Decisao-2026-06-04-reorganizacao-pastas-vault]] (ADR-001).

## TL;DR
Gabriel revisou a organização do vault do Tadeu, apontou que está "muito centralizada/desorganizada" e
mostrou o padrão dele: **separar Sistema de conteúdo**, **camada bronze de conhecimento (`_raw_files`)**,
**"casa = dono"**, **Pessoas/Parceiros**, e **só criar pasta com conteúdo**. Passou 3 skills (transcript-extractor,
populate, sincronizar-conhecimento) e recomendou plugins (superpowers, obsidian-cli). Plano: instalar skills →
reorganizar pastas → construir skill de **onboarding de gateway** → testar reonboard do ClickBank.

## 🧱 Discussão detalhada (pontos + porquês)
- **Separar "Sistema" de conhecimento.** Tudo que faz o vault rodar (CLAUDE.md, templates, skills, raw files)
  vai em `Sistema/`. *Porquê:* a árvore fica navegável e a IA acha a informação mais fácil.
- **`_raw_files` = camada bronze do conhecimento** (3 categorias: reuniões, documentos, notas; cada uma
  `pendente`/`processado`). *Porquê:* preservar o cru permite **reprocessar** (ex.: numa reorganização) — o
  conhecimento não fica preso só na versão destilada. (Foi exatamente o que faltou: esta call não tinha sido salva.)
- **Memória do Cloud Code × base de conhecimento.** O Claude fica "mais inteligente" não só pelo vault, mas pela
  **memória local** (`~/.claude/.../memory/`). Como ela não viaja no git, é preciso **espelhá-la** numa base
  versionada (`Sistema/Base de Conhecimento (Claude)/`) — senão quem clona (Léo) recebe um Claude "burro".
  *Porquê:* nivelar o resultado entre as máquinas do time.
- **"Casa = dono".** A nota mora na entidade que a possui (Pessoa, Parceiro, Projeto, domínio), não num balde
  por tipo. *Porquê:* contexto junto do dono ajuda análise/modelagem; evita duplicar BUs/departamentos.
- **Unificar bancos.** Não faz sentido `DB_instituto_experience` e `DB_data_team` na raiz (mesma natureza) →
  `Banco de Dados/<engine>/<db>` com estrutura padrão (Postgres futuro idem).
- **"Pessoas" no lugar de "Entrevistas"** (time + negócio + candidatos); entrevistas viram subpasta (triagem,
  teste técnico, aprovados).
- **Pasta só com conteúdo** (sem pasta vazia/desbalanceada). Teste-guia: "navegando, acho fácil?".
- **Onboarding como skill.** O gargalo 80/20 é onboardar novas fontes (gateways). Construir `onboard-gateway`
  (amostra → de-para/discovery → bronze → silver → gold), reusando BuyGoods/ClickBank já documentados.
- **Disciplina:** gravar **toda** reunião; usar IA pelo terminal pra tudo; "turbinar com IA, não fazer sozinho".

## ✅ Decisões
- Adotar a estrutura no padrão do Gabriel (`Sistema`, `_raw_files`, "casa = dono", Pessoas/Parceiros) → **ADR-001**.
- Usar **ingestão estruturada** (skills) em vez de jogar transcript solto no chat.
- Espelhar conhecimento de empresa na base versionada (regra no `CLAUDE.md`).

## 📌 Action items
| Ação | Responsável | Status |
|---|---|---|
| **superpowers** (plugin Claude Code) | Tadeu | ✅ instalado (v5.1.0, user) — reiniciar sessão p/ carregar |
| **obsidian-cli** — confirmar qual (npm `obsidian-cli` é não-verificado; o do Yakitrak é Go) | Tadeu / Davi | ⏳ a confirmar |
| Instalar as 3 skills (transcript-extractor, populate, sincronizar-conhecimento) | Tadeu | ✅ feito |
| Reorganizar a arquitetura de pastas | Tadeu | ✅ feito (ADR-001) |
| Construir skill **`onboard-gateway`** (onboarding de fontes) | Tadeu | ⏳ a fazer |
| Marcar call com o **Davi** para review de skills/plugins | Tadeu | ⏳ a fazer |
| Testar **reonboard do ClickBank** do zero (medir ganho de tempo) | Tadeu | ⏳ a fazer |
| Receber do Gabriel os `references/` das skills (`formats.md`, `routing.md`) | Gabriel | ⏳ pendente |
| Gravar todas as reuniões (disciplina) | Tadeu | 🔁 contínuo |

## ⚠️ Pontos em aberto / riscos
- Plugins externos (superpowers/obsidian-cli) dependem do Davi — não instalados.
- Skills do CTO assumiam a estrutura dele; adaptadas ao nosso vault, mas faltam os `references/`.
- Geradores GERADO (`Inventario MSQL/*.py`, `gerar_datalake.py`) ainda apontam para caminhos antigos.

## Relacionados
[[Decisao-2026-06-04-reorganizacao-pastas-vault]] · [[2026-06-04 Sessão — Estrutura do Vault (Gabriel)]] · [[Sistema/Skills/_catalogo]]
