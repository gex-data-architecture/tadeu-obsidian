# CLAUDE.md — Schema do vault (Documentação do Time de Dados)

> Este arquivo é o **schema** da base de conhecimento, no padrão *LLM Wiki* (Karpathy).
> Qualquer agente (Claude Code) que abrir este vault deve ler este arquivo primeiro e
> seguir as convenções abaixo. Linguagem das notas: **português**.

## 1. Propósito
Documentar de forma viva e navegável o time/plataforma de dados do banco MySQL/RDS
`instituto_experience` (e, no futuro, o **Athena**). A wiki é um **artefato persistente
que se acumula** — não regeramos conhecimento do zero a cada pergunta; nós **integramos**
informação nova nas páginas existentes.

## 2. Arquitetura em 3 camadas
1. **Raw Sources (fontes cruas, imutáveis)** — não editar à mão:
   - **O banco vivo é a fonte da verdade.** `1_extrair_rotinas.py` lê o
     `information_schema` e gera `Inventario MSQL\_mapdata\*.json`
     (`routines`, `events`, `objects`, **`tables`**, **`views`**). Tabela/view
     dropada no banco some do json e, na próxima geração, some do vault — automático.
   - O próprio banco via **MCP `mysql`** (read-only) e, futuramente, **Athena**.
   - ⚠️ **`inventario_banco_instituto_experience.xlsx` está APOSENTADO como fonte.**
     Era um snapshot órfão (nenhum script da pasta o regenera) e ficava velho. O
     `3_gerar_vault.py` não o lê mais — Tabelas/Views agora vêm do banco (json).
2. **A Wiki (este vault)** — markdown gerado/mantido pelo agente. Ver pastas na seção 3.
3. **O Schema** — este `CLAUDE.md`.

## 3. Estrutura de pastas
```
DataTeamDocs/
  CLAUDE.md                 # este schema
  log.md                    # diário append-only de mudanças
  Templates/                # modelos de nota (transversal)

  # --- GERADO (sobrescrito pelos scripts) — uma pasta por banco: DB_<schema> ---
  DB_instituto_experience/
    00-Indice.md            # índice DESTE banco (GERADO)
    Tabelas/  Views/  Rotinas/  Eventos/   # 1 nota por objeto (não editar à mão)
  DB_data_team/             # marts do time (vazio por enquanto)
    00-Indice.md            # índice deste banco
  Data Lake/                # GERADO da AWS Glue pela skill `catalogo-datalake`
    00-Data-Lake.md         # índice do lake (databases, tabelas, jobs, SFN, crawlers)
    Tabelas/<database>/     # 1 nota por tabela do Glue Catalog (bronze/silver/gold × dev/prod)
    Jobs/                   # 1 nota por ETL Job do Glue (com script S3 + últimas execuções)
    Orquestracao/           # 1 nota por Step Function e por crawler + 00-Orquestracao.md
                            #   (Fluxo ASL, encadeamento via EventBridge, grafo mermaid,
                            #    agendamentos cron/rate com status/horário/alvo)

  # --- CURADO (NUNCA sobrescrito) — manual, humano + LLM ---
  Conhecimento/             # saber sobre os dados
    Dossies/  Calls/  Decisoes/
  Fontes de Dados/          # plataformas (Clickbank, Buygoods, Cartpanda…) + onboarding
    _template-fonte.md  _onboarding-nova-fonte.md
    <Plataforma>/  ( <Plataforma>.md  API.md  Webhook.md  Mapeamento.md  exemplos/ )
  Dashboards/               # dashboards do Looker Studio
  Fluxos-N8N/               # automações n8n          (artefato de trabalho)
  Epicos/                   # épicos de projeto
  Incidentes/               # post-mortems
  Pipelines/                # pipelines de dados ponta a ponta
  Planilhas Manuais/        # fontes mantidas à mão (Sheets/Excel)
```

> **Regra mestra:** existe SÓ uma divisão que importa — **GERADO** (as pastas-banco `DB_<schema>`
> e a `Data Lake/`, sobrescritas a cada regeração pelos scripts/skills) vs. **CURADO** (todo o resto,
> nunca tocado pelos scripts). A organização das pastas curadas é só navegação.
> Fontes do GERADO: `DB_<schema>` ← MySQL (`Inventario MSQL/`); `Data Lake/` ← AWS Glue (skill `catalogo-datalake`).

### 📂 Regra de organização por banco
- Cada **banco** vira uma pasta no padrão **`DB_<schema>`** (`DB_instituto_experience`, `DB_data_team`),
  contendo APENAS as notas **geradas** daquele banco + o seu próprio **`00-Indice.md`**.
- O que é **transversal** — `Templates/`, `Conhecimento/`, pastas curadas, `CLAUDE.md`, `log.md` —
  fica no **root** (conhecimento curado pode cruzar bancos).
- Nas queries Dataview, o `FROM` usa o caminho com a pasta-banco: `FROM "DB_instituto_experience/Tabelas"`.

> **Padrão do índice:** cada `DB_<schema>/` tem um `00-Indice.md`. Como há vários com o mesmo nome,
> **sempre linke com o caminho**: `[[DB_instituto_experience/00-Indice]]` (e não `[[00-Indice]]`, que fica ambíguo).

### ⚠️ Regra de ouro sobre regeneração
As pastas **Tabelas / Views / Rotinas / Eventos** são **geradas** pelos scripts e
**sobrescritas** numa regeração. **Não coloque conhecimento manual nelas** — ele se perde.
Todo insight, narrativa, decisão e dossiê de negócio vai em **`Conhecimento/`** (e em MOCs),
que os scripts não tocam. Linke das notas curadas para as notas geradas com `[[wikilinks]]`.

## 4. Convenções de nota
- **Nome do arquivo = nome do objeto** (ex.: `Tabelas/cartpanda_physical.md`). Isso faz o
  `[[cartpanda_physical]]` resolver de qualquer lugar e alimenta o Graph View.
- **Frontmatter (YAML)** por tipo:
  - Tabela: `tipo: tabela`, `categoria`, `linhas`, `tamanho_mb`, `colunas`, `tem_pk`, `alertas`, `criada_em`, `tags: [tabela, "categoria/<cat>"]`
  - View: `tipo: view`, `definer`, `security_type`, `colunas`, `tags: [view]`
  - Rotina: `tipo: procedure|function`, `definer`, `acesso_sql`, `security`, `criada_em`, `execucoes`, `tags: [rotina, <tipo>]`
  - Evento: `tipo: evento`, `status`, `intervalo`, `unidade`, `ultima_execucao`, `execucoes`, `tags: [evento]`
  - Rotinas e eventos trazem, além do **Corpo SQL** embutido, uma seção **`Execuções (performance_schema)`**
    (nº de execuções, tempo médio/máx/total, erros, warnings, linhas afetadas). É o análogo MySQL do
    histórico dos Glue Jobs — porém **acumulado desde o último restart**, não histórico absoluto.
  - Conhecimento: `tipo: dossie|moc|decisao`, `tags: [...]`, e linke os objetos relacionados.
- **Dependências** sempre como `[[links]]` (LÊ / ESCREVE / CRIA / TRUNCA / DROPA / CHAMA).

## 5. Operações (o que fazer quando pedirem)

### INGEST / SYNC (refletir o estado atual do banco)
Sempre que o banco mudar (tabela criada/dropada, rotina alterada, etc.), rode a
sequência abaixo na pasta `Inventario MSQL/` — ela relê o banco e regenera o vault:
1. `python 1_extrair_rotinas.py`  → atualiza `_mapdata/*.json` (inclui `tables`/`views`).
2. `python 3_gerar_vault.py`      → regenera Tabelas/Views/Rotinas/Eventos.
3. `python 4_gerar_indice.py`     → regenera o `00-Indice.md`.
   (Para mudanças pequenas, pode editar só a nota afetada — mas lembre que a próxima
   regeração sobrescreve; insight de negócio vai em `Conhecimento/`, que não é tocado.)
4. Toda ingestão **deve** adicionar uma linha no `log.md`.
5. Após DROP de tabelas: rode o **LINT de links quebrados** — notas curadas que linkam
   `[[<tabela_dropada>]]` viram links mortos e precisam de ajuste.

### QUERY (responder com base na wiki)
- Responda primeiro a partir das notas do vault; cite as notas usadas com `[[links]]`.
- Se faltar informação, consulte o **MCP `mysql`** (read-only), traga o dado e **persista**
  numa nota (não deixe a resposta só no chat).

### LINT (saúde da wiki) — rode quando pedirem "lint" ou periodicamente
- **Contradições**: números/afirmações divergentes entre notas curadas e notas geradas.
- **Dados velhos**: `criada_em`/`ultima_execucao` muito antigos; eventos `DISABLED` ainda referenciados.
- **Órfãos**: notas em `Conhecimento/` sem nenhum link de/para objetos.
- **Links quebrados**: `[[...]]` apontando para objeto que não existe mais (pode ser tabela dropada).
- Gere um relatório em `Conhecimento/Lint-YYYY-MM-DD.md` e registre no `log.md`.

## 6. Fonte de verdade / cuidado
- O **MCP `mysql` é read-only**. Nunca proponha escrita no banco a partir daqui.
- Métricas de uso (leituras/escritas) vêm do `performance_schema` e **zeram a cada restart**
  do MySQL — trate como "janela recente", não histórico absoluto.
- `linhas` é estimativa do otimizador; `Atualizada em` costuma vir vazia no MySQL 8.

## 7. Scripts (em `Inventario MSQL/`, fora do vault)
| Script | Função |
|---|---|
| `1_extrair_rotinas.py` | Extrai rotinas/eventos/objetos **+ tabelas + views + execuções de programas** (`program_stats.json`, do `performance_schema`) do RDS para `_mapdata/*.json` |
| `2_gerar_excel.py` | (Opcional) Excel de rotinas/eventos com dependências |
| `3_gerar_vault.py` | Gera Tabelas/Views/Rotinas/Eventos neste vault **a partir do `_mapdata/*.json`** (não usa mais o xlsx) |
| `4_gerar_indice.py` | Gera `00-Indice.md` + templates + `.gitignore` |

> **Nota sobre métricas de tabela:** `Linhas` é estimativa do otimizador; `Leituras (3d)`/`Escritas (3d)`
> ainda aparecem como `n/d` (viriam de `table_io_waits_summary_by_table` — ainda não extraídas); `Categoria` é
> heurística por prefixo do nome (navegação); `Alertas` é derivado (`sem PK`, `vazia (estim.)`).
>
> **Execuções de rotinas/eventos:** o `performance_schema` **está acessível** para
> `events_statements_summary_by_program` — daí saem as execuções de procedures/functions/events
> (`program_stats.json`). Lembre que esses contadores **zeram a cada restart** do MySQL.
