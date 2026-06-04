---
tipo: call
tags: [call, conhecimento, consultoria, dados]
categoria: consultoria-externa
data: 2026-06-03
duracao: 78min
participantes: [Flávio Vieira (Teddy), Diego Pinto (Teddy), Gabriel Ferreira (Teddy), Carlos Tadeu (GEX), Diretoria/CTO (GEX)]
owner_nota: Tadeu
status: rascunho
gravacao: https://fathom.video/share/uYdPNasX91rq2hSYRz2x6VrAdMy3Pqfo
---
# 📞 Alinhamento Teddy × GEX — Arquitetura de Dados

> [!info] Resumo
> **Data**: 2026-06-03 · **Duração**: 78min · **Categoria**: consultoria externa (Teddy/TED, responsável **Flávio Vieira**)
> Benchmark de arquitetura de dados: confrontar o estado atual da GEX com as práticas da Teddy e definir próximos passos.

## 🎯 Resumo executivo
- A GEX se reuniu com a consultoria **Teddy/TED** (responsável Flávio Vieira) para comparar arquiteturas e colher recomendações de evolução.
- Ambas seguem **medallion** sobre `S3` com `Athena`; principal divergência: GEX usa `parquet` particionado por data, Teddy migrou para **`Apache Iceberg`** (time travel).
- A GEX depende do `MySQL` como **ponte** para o `Looker Studio` (não há conector nativo `Athena`↔`Looker`).
- Gap mais citado: **falta de orquestrador** na GEX (hoje `Lambda` + filas + schedule do `Glue`). Teddy recomenda **`Airflow`** para governança, retries, alertas e observabilidade.
- Modelagem: **tabelões vs star schema** (fato/dimensão) + **padrões de nomenclatura** (`VL_`, `DIM_`, `NM_`) — impacto em performance, governança e custo de tokens para IA.
- Governança da Teddy: **Data Contracts** (assinados no `ClickSign`), catálogo/linhagem com **`DataHub`**, `OLS`/`RLS` via `IAM`/`Lake Formation`, classificação de relatórios e deduplicação.
- Visualização: movimento **Power BI/Looker → Lovable**, com **MCP customizado** (`Cognito`+`Lake Formation`) para mitigar o risco de vazamento do Lovable.
- Combinados: workshop de modelagem Gold, link do `Great Expectations`, deep-dive Obsidian/RAG/vetorial e **bucket `S3` isolado + IAM key** para POC do Lovable.

## 👥 Participantes
| Nome | Papel na call |
|---|---|
| **Flávio Vieira** (Teddy) | responsável/consultor — conduziu |
| **Diego Pinto** (Teddy) | lead de engenharia de dados |
| **Gabriel Ferreira** (Teddy) | lead de BI |
| **Carlos Tadeu** (GEX) | tech lead de dados |
| **Diretoria/CTO** (GEX) | diretor / CTO |

## Contexto
A estrutura de dados da GEX está crescendo e o time quer garantir que a arquitetura é robusta para escalar com governança. A Teddy (que já presta consultoria à GEX via Flávio) apresentou como organiza seus dados, para servir de benchmark.

## 🧱 Principais pontos por tema

### Arquitetura
- **GEX hoje:** Data Lake AWS em `parquet` particionado por data (ano/mês/dia); `MySQL` com tabelas/views que alimentam o `Looker Studio`; `Athena` como warehouse, **sem conector nativo** para o `Looker` → o `MySQL` é a **ponte**. Camadas `bronze`/`silver`/`gold` + **tabelões**. Fonte principal: gateways de pagamento (alto volume, histórico via API + novos dados via Webhook). Processamento que rodava a cada 5–15 min foi para **a cada 2h** por custo. A infra do Léo está em **`Terraform` (IaC)** com **versionamento no `GitHub`**.
- **Teddy:** `RAW → Silver → Gold` no `S3`; migrou para **`Apache Iceberg`** (time travel — "como o dado estava ontem" com uma query); `Athena`/`Trino` como engine; `PySpark` na transformação; `Terraform`/IaC + `GitHub`.
- **Convergência:** medallion sobre `S3` + `Athena`. **Divergências:** formato (`parquet` × `Iceberg`), ponte via `MySQL` (só GEX), e a Gold real de fato/dimensão (Teddy) vs tabelões (GEX).

### Orquestração & Observabilidade
- **GEX não tem orquestrador.** Usa `Lambda` + filas (`SQS`) + **schedule do `Glue`**; arquitetura voltada a evento/quase-stream. O Léo criou **retries e uma DLQ (fila morta)** paliativos para reprocessar falhas.
- ⚠️ **Risco de reprocessamento fora de ordem** levantado pelo Diego: um evento que morreu e é reprocessado **depois** de outro mais novo já ter passado vira **dado datado**. A GEX hoje basicamente não trata isso (jobs a cada 2h).
- **Teddy usa `Airflow` (MWAA gerenciado).** Recomendações:
  - Orquestrador traz **governança, retries automáticos, alerta por e-mail/DAG, observabilidade** e **abstração de DAGs por fonte de dados** (cresce de forma controlável — hoje a GEX tem ~20 fontes, vai aumentar).
  - **MWAA é caro** → pode rodar `Airflow` em **`ECS`/`EC2`** mais barato; e nem tudo precisa ser `Glue Job` (custo alto).
  - **Data Quality:** framework **`Great Expectations`** (config em JSON, valida campos — ex.: "nunca nulo" — gera relatório/PDF e alerta). A Teddy também usa **Glue Data Quality** postando no **Teams**, comparando Gold/Silver com as fontes para detectar atraso.

### Modelagem de dados
- Debate central: **tabelões** (wide tables, dezenas de colunas, milhões de linhas) **× star schema** (fato/dimensão).
- Modelar fato/dimensão **dentro** do `Looker`/`Power BI` deixa o dash **lento** e **sobrecarrega o Data View**; o engenheiro modela uma vez em estrela e o Data View não recria dimensões a cada dash.
- **Redução de tokenização para IA:** usar `ID` + dimensão em vez de repetir descrições (ex.: produto) — facilita carregar em IA e baixa custo. A Teddy mantém também uma **tabela de métricas** (já calculada por linha, ex.: receita/qtd por campanha) para o Data View consumir pronto.
- **Padrões de nomenclatura** (negociáveis, mas **tem que ter padrão**): valor `VL_`, dimensão `DIM_`, nome `NM_`. Crítico para governança/acesso e para a IA não "alucinar" qual é o campo de valor (`valor`/`VR`/`VLR`).

### Governança & Padrões
- **Data Contracts:** contrato entre áreas; mudança de schema precisa ser avisada e ter impacto analisado; formalizado por assinatura no **`ClickSign`** (não trava o dev, mas é política/aviso). Teddy tem 12–14 squads mexendo na origem.
- **Catálogo/Linhagem:** **`DataHub`** (open source, tipo Purview) para catalogação, documentação, contratos e **linhagem** — motivado por consultas de 700+ linhas e linhagem "na cabeça das pessoas".
- **Acesso:** `OLS`/`RLS` + **silos por área/empresa** (grupo com várias empresas, indicadores e acessos distintos), restrição via `IAM`/`Lake Formation`.
- **Relatórios:** classificar em **estratégico/tático/operacional** (big numbers = estratégico; deep do deep = operacional) e **deduplicar** — a Teddy reduziu de **59 → ~31** relatórios.
- **Higiene de campos:** rodar IA mensal para achar colunas não usadas (ex.: uma tabela com **182 campos** onde **<70** eram necessários) e cortar; comparar script do `Glue` × `Power BI` (PBIP) para achar obsoletos em minutos.
- **Processo:** code review, priorização por impacto, **não subir nada na sexta** (sem time 24x7).

### Visualização (Lovable) & IA
- **Movimento:** `Power BI`/`Looker` → **Lovable** (CEO da Teddy já cria os próprios dashes). Looker/Power BI vistos como engessados.
- **Pontos fortes do Lovable:** front-end rico, prototipagem rápida (mudança que levava 4–5h no Power BI sai em <2 min), **insights automáticos por IA**, **alertas por e-mail/WhatsApp**, **knowledge base** (sobe o conhecimento de negócio) e **referência entre painéis com `@`**.
- **Segurança:** Lovable é "famoso por vazamento". A Teddy criou um **MCP customizado** (ponte AWS↔Lovable, ~20 dias de dev): em vez de passar Secret/Access Key direto, audita vazamento; **`Cognito`** (usuário só vê certas tabelas) + **`Lake Formation`** (governança fina); **skills** no MCP definem os tipos de gráfico. Para começar rápido, o Lovable tem **Connectors** diretos (S3/banco) via Secret — recomenda-se **bucket isolado + IAM key dedicada**.
- **IA-first:** `Cloud Code`, agentes com contexto de negócio, **`PBIX → PBIP`** para o Claude documentar relatório como código; lema "**turbinar com IA, não escalar o time**".
- **Obsidian (alerta de escala):** bom para pequeno/médio porte, mas a **indexação fica lenta em volume** (não é banco vetorial). A Teddy teve gargalo com agentes consumindo Obsidian (alucinação/lentidão) e migrou para **RAG / banco vetorial / `SQLite`**.

## ⚖️ Comparativo GEX × Teddy
| Tema | GEX hoje | Teddy / recomendado |
|---|---|---|
| Formato do lake | `parquet` particionado por data | `Apache Iceberg` (time travel) |
| Camadas | `bronze`/`silver`/`gold` + tabelões | `RAW`/`Silver`/`Gold` (fato/dimensão) |
| Engine de query | `Athena` | `Athena`/`Trino` |
| Orquestração | **nenhuma** (`Lambda`+filas+schedule `Glue`) | `Airflow` (MWAA, ou ECS/EC2 + barato) |
| Retry/observabilidade | retries+DLQ paliativos (Léo) | retries/alertas nativos + Data Quality |
| Data Quality | — | `Great Expectations` + Glue DQ → Teams |
| IaC / Versionamento | `Terraform` + `GitHub` (via Léo) | `Terraform` + `GitHub` |
| Modelagem analítica | tabelões | star schema + nomenclatura (`VL_`/`DIM_`/`NM_`) |
| Governança/Catálogo | não possui | `DataHub`, Data Contracts (`ClickSign`) |
| Acesso | — | `OLS`/`RLS` via `IAM`/`Lake Formation` |
| Visualização | `Looker Studio` via ponte `MySQL` | `Lovable` via MCP customizado |

## ✅ Action items
- [ ] @Tadeu + Teddy — **Workshop de modelagem Gold** com Diego + Gabriel; GEX leva uma Gold para modelar junto (análise exploratória). · destino: [[[novo épico]]]
- [ ] @Diego — **Enviar link do `Great Expectations`** ao Tadeu.
- [ ] @Tadeu + Flávio/Diego — **Deep-dive Obsidian × RAG/banco vetorial** (limites de indexação e alternativas).
- [ ] @Tadeu — **Criar bucket `S3` isolado + IAM key dedicada** e carregar dados de amostra para **POC do Lovable**.

> [!warning] Action item virou trabalho real?
> O workshop de Gold e a POC do Lovable provavelmente viram [[Épicos]] — criar e linkar bidirecional.

## 🚀 Planos de ação recomendados para a GEX
1. **Bucket `S3` isolado + IAM key dedicada para POC do Lovable** · contém o risco de vazamento e isola do produtivo · esforço **baixo** · impacto **alto**.
2. **Padrões de nomenclatura (`VL_`/`DIM_`/`NM_`) + workshop de modelagem Gold (fato/dimensão)** · governança, performance e menos tokens/alucinação na IA · esforço **médio** · impacto **alto**.
3. **Introduzir orquestrador (`Airflow` em ECS/EC2)** · governança, retries, alertas, observabilidade e fim das soluções paliativas; resolve o reprocessamento fora de ordem · esforço **alto** · impacto **alto**.
4. **Data Quality com `Great Expectations`** · observabilidade de qualidade (hoje ausente) · esforço **médio** · impacto **alto**.
5. **Catálogo + linhagem com `DataHub`** · tira a linhagem "da cabeça das pessoas"; documenta consultas longas · esforço **alto** · impacto **alto**.
6. **Formalizar Data Contracts** (aviso de mudança de schema; política via `ClickSign`) · previne relatório zerado por mudança na origem · esforço **médio** · impacto **médio**.
7. **`OLS`/`RLS` + silos via `IAM`/`Lake Formation`** · segrega acesso por área/empresa · esforço **médio** · impacto **médio**.
8. **Deduplicar e classificar relatórios** (estratégico/tático/operacional) + cortar campos não usados · menos manutenção/custo · esforço **baixo** · impacto **médio**.
9. **Avaliar `parquet` → `Apache Iceberg`** · time travel e evolução de schema · esforço **alto** · impacto **médio**.
10. **Avançar IA-first** (agentes com contexto, `PBIX→PBIP`, RAG/banco vetorial além do Obsidian) · escala sem crescer o time · esforço **médio** · impacto **médio**.

## ⚠️ Pontos de atenção / riscos
- **Vazamento no Lovable:** não conectar a dados produtivos sem isolamento (bucket + IAM dedicados; idealmente MCP com `Cognito`/`Lake Formation`).
- **Reprocessamento fora de ordem** (dado datado sobrescrevendo o mais novo): tratar com controle de watermark/ordem ao introduzir orquestração.
- **Dependência do `MySQL` como ponte** lake↔`Looker`: ponto único de acoplamento.
- **Tabelões:** degradam performance e inflam custo de tokens para IA; remodelar tem esforço.
- **Escala do Obsidian:** planejar RAG/banco vetorial antes de crescer o volume.
- **MCP customizado:** ~20 dias de dev na Teddy — orçar prazo/recurso se a POC avançar.

## Próxima call
- **Foco**: call técnica de laboratório para modelar uma **Gold (fato/dimensão)** junto com Diego/Gabriel; e (separada) deep-dive Obsidian × RAG/vetorial.

## Relacionados
[[migracao-data_team-mapa]] · [[Regras de Exclusão]] · [[Conhecimento/Calls/_sobre]]
