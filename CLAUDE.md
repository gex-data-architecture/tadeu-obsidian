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
  CLAUDE.md · log.md                         # schema + diário (raiz)

  _Sistema/                                  # MÁQUINA do vault ("_" agrupa no topo)
    _raw_files/{reuniões,documentos,notas}/{pendente,processado}/   # camada BRONZE do conhecimento (cru, reprocessável)
    Capturas (log de populate)/              # âncoras da skill populate
    Base de Conhecimento (Claude)/           # espelho da memória do Claude (skill sincronizar-conhecimento)
    _Templates/                              # modelos de nota
    Skills/_catalogo.md                      # catálogo de skills (skill catalogo-skills)

  # --- GERADO (sobrescrito por scripts/skills) ---
  Banco de Dados/MySQL/<db>/                 # instituto_experience, data_team (← MySQL)
    00-Indice.md · Tabelas/ Views/ Rotinas/ Eventos/
  Arquitetura/Data Lake/                     # ← AWS Glue (skill catalogo-datalake): Tabelas/ Jobs/ Orquestracao/ Crawlers/

  # --- CURADO (nunca sobrescrito) — "casa = dono" ---
  Arquitetura/                               # stack, medalhão, Migração data_team/
  Fontes de Dados/<Plataforma>/              # Buygoods, Clickbank, Cartpanda… + onboarding
  Dashboards/                                # Looker Studio
  Pessoas/<Nome>/ (1on1/) · Pessoas/Recrutamento/   # time, negócio, candidatos
  Parceiros/<empresa>/Reuniões/              # consultorias/fornecedores (ex.: Teddy)
  Reuniões/                                  # reuniões internas do time
  Decisões/                                  # ADRs
  Projetos/ · Incidentes/
  Operação/                                  # regras de negócio · indicadores · Validações · N8N · Planilhas
```

> **Regra mestra:** **GERADO** (sobrescrito por scripts/skills) vs **CURADO** (nunca tocado).
> GERADO = `Banco de Dados/MySQL/<db>/{Tabelas,Views,Rotinas,Eventos}` (← MySQL, `Inventario MSQL/`) e
> `Arquitetura/Data Lake/` (← AWS Glue, skill `catalogo-datalake`). CURADO = todo o resto.
> Princípio de organização do CURADO: **"casa = dono"** — a nota mora na **entidade que a possui**
> (pessoa, parceiro, projeto, banco, domínio), não num balde por tipo. Pasta só existe quando há conteúdo.

### 📂 Regra de organização por banco
- Cada banco relacional vira **`Banco de Dados/<engine>/<db>/`** (`Banco de Dados/MySQL/instituto_experience`,
  `…/data_team`), com APENAS as notas **geradas** + o seu **`00-Indice.md`**. Mesma estrutura por banco (Postgres/futuros idem).
- **`_Sistema/`** é a máquina (templates, raw files, skills, base de conhecimento). O conteúdo curado mora nas pastas por domínio/dono.
- Dataview: `FROM "Banco de Dados/MySQL/instituto_experience/Tabelas"`.

> **Padrão do índice:** vários `00-Indice.md` → **linke com o caminho**:
> `[[Banco de Dados/MySQL/instituto_experience/00-Indice]]` (não `[[00-Indice]]`, que fica ambíguo).

### ⚠️ Regra de ouro sobre regeneração
As pastas **Tabelas / Views / Rotinas / Eventos** são **geradas** pelos scripts e
**sobrescritas** numa regeração. **Não coloque conhecimento manual nelas** — ele se perde.
Insight, narrativa, decisão e dossiê vão para a **entidade dona** (`Decisões/`, `Reuniões/`,
`Fontes de Dados/`, dossiê junto da tabela). Linke das curadas para as geradas com `[[wikilinks]]`.

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
   regeração sobrescreve; insight de negócio vai na entidade dona — `Decisões/`, `Reuniões/`, etc.)
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
- **Órfãos**: notas curadas sem nenhum link de/para objetos.
- **Links quebrados**: `[[...]]` apontando para objeto que não existe mais (pode ser tabela dropada).
- Gere um relatório em `Operação/Lint-YYYY-MM-DD.md` e registre no `log.md`.

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

## 8. Memória do Claude → Base de Conhecimento (regra de espelhamento)
A inteligência do Claude mora em dois lugares: a **memória local** (`~/.claude/.../memory/`, **não** versionada)
e a **`_Sistema/Base de Conhecimento (Claude)/`** (versionada, viaja no git). **Ao salvar uma memória de
conhecimento de EMPRESA** (banco, métricas, processos, ferramentas, decisões), grave-a **também** na Base de
Conhecimento, para quem clona o repo herdar. **Não espelhe** conteúdo pessoal/perfil de indivíduo nem
segredos/credenciais — esses ficam só na memória local. A skill **`sincronizar-conhecimento`** é a rede de
segurança que reconcilia tudo. Dono do vault: **Tadeu**.
