---
name: limpeza-banco
description: >-
  Identifica com SEGURANÇA tabelas (e, à parte, views) que podem ser excluídas de
  um banco MySQL/RDS e gera os scripts de limpeza (quarentena por RENAME + DROP
  datado) sem nunca executar DDL. Use SEMPRE que o usuário falar em "limpar o
  banco", "dropar/excluir tabelas", "tabelas vazias", "tabelas órfãs", "tabelas
  que não são usadas", "candidatas a exclusão", "liberar espaço no RDS", "o que
  posso apagar", "tabelas mortas/obsoletas/legadas", ou pedir uma faxina/limpeza
  de schema — mesmo que não diga a palavra "skill". Acessa o MySQL via MCP
  read-only (servidor `mysql`, ferramenta `mcp__mysql__mysql_query`). Schema
  padrão: `instituto_experience` (mas pergunte/parametrize se houver outro).
---

# Limpeza de banco — caça a tabelas/views excluíveis

## Por que esta skill existe

Decidir se uma tabela pode ser apagada parece trivial ("está vazia? apaga") e
**não é**. Esta skill encapsula uma metodologia que foi depurada na marra, errando
e corrigindo, contra um banco de produção real. Cada regra aqui existe porque a
ausência dela já causou um quase-acidente. Leia as **Armadilhas conhecidas** antes
de relaxar qualquer passo — elas são o coração da skill, não um apêndice.

## Princípio de segurança inviolável

O MCP `mysql` é **READ-ONLY** por design. Esta skill **NUNCA executa `DROP`,
`RENAME`, `TRUNCATE`, `ALTER` ou qualquer DDL/DML**. Ela apenas:

1. **Lê** o banco para investigar.
2. **Gera scripts** (`.sql`) que o usuário ou o DBA executam com a conta de admin.
3. **Documenta** a análise no vault.

Se em algum momento você sentir vontade de "só rodar o DROP pra adiantar" — pare.
A separação entre quem analisa (você) e quem executa (humano com conta privilegiada)
é a rede de segurança. Respeite-a sempre.

## Regras invioláveis (a lista de "nunca")

- **NUNCA** inclua tabelas com sufixo de swap (`_stage`, `_old`, `_new`, `_aws_new`).
  São pontas do **swap atômico**: `_stage`/`_new` recebem o `INSERT`/build, `_old` é
  o backup do `RENAME`. Ficam vazias **entre os ciclos** do refresh — emptiness ali é
  estado normal, não morte. Filtre os óbvios (`NOT LIKE '%\_stage' AND NOT LIKE
  '%\_old' AND NOT LIKE '%\_new'`) **e** aplique o teste do irmão vivo abaixo.
- **NUNCA** declare morta uma tabela vazia sem checar o **irmão vivo**. Tire um
  sufixo de build do nome (`_new`, `_aws_new`, `_stage`, `_old`, e às vezes só `_aws`)
  e veja se existe uma irmã com o nome-base **cheia e/ou escrita recentemente**. Se
  existir, a vazia é o **alvo do próximo swap**, não lixo. Caso real: `gold_clickbank_aws_new`
  (0 linhas) parecia órfã, mas `gold_clickbank_aws` (216k, escrita hoje) é a viva — a
  `_aws_new` é só o alvo do swap. O mesmo valeu para `clickbank_physical_new_aws_new`
  e `dashboard_channels_marketing_aws_new`. **Empty + irmão vivo = mantém.**
- **NUNCA** confie em `information_schema.TABLES.TABLE_ROWS` para afirmar "vazia".
  É uma **estimativa** do InnoDB e mente: já apareceu `0` para tabelas com linhas e
  vice-versa. Use **`COUNT(*)` real** em cada candidata antes de afirmar qualquer coisa.
- **NUNCA** dê um "confirmo que não é lida/escrita" que você não consegue provar.
  Referência estática (procedure/view) **não cobre** leitura externa (n8n, Looker,
  app). Se faltar o sinal de runtime, diga isso explicitamente e use a quarentena.
- **NUNCA** trate view por "estar vazia" (ver seção Views).

## O procedimento (tabelas)

Rode os passos via `mcp__mysql__mysql_query`. As queries completas e prontas pra
copiar estão em `references/queries.sql` — leia esse arquivo e adapte o nome do
schema. Aqui vai a lógica de cada etapa e como interpretar.

### Passo 0 — Parâmetro de schema
Confirme o schema-alvo (padrão `instituto_experience`). Tudo abaixo é filtrado por
`TABLE_SCHEMA = '<schema>'`.

### Passo 1 — Candidatas brutas (filtro estático)
Liste base tables que: estimativa `TABLE_ROWS = 0`, **não** `_stage`/`_old`/`_new`, e
**não** aparecem (substring `LIKE '%nome%'`, que é conservador — na dúvida conta
como usado) em nenhuma:
- procedure/function (`information_schema.ROUTINES.ROUTINE_DEFINITION`)
- event (`information_schema.EVENTS.EVENT_DEFINITION`)
- view (`information_schema.VIEWS.VIEW_DEFINITION`)

Depois desse filtro, rode o **teste do irmão vivo** (Passo 1b): para cada candidata,
procure tabelas com o mesmo prefixo-base (`LIKE 'base%'`) e veja se alguma está cheia
ou com `UPDATE_TIME` recente. Se sim, a candidata vazia é alvo de swap → descarte.

> Por que substring conservador: se o nome de uma tabela é trecho do nome de outra
> que é usada, ela é marcada como "usada" e **fica de fora**. Erramos para o lado de
> **não apagar**. É o lado certo de errar.

### Passo 2 — Confirmar vazio DE VERDADE
Para **cada** candidata do passo 1, rode `COUNT(*)`. Monte um `UNION ALL` de
`SELECT '<tabela>', COUNT(*)`. Só seguem as que derem **0**. As que tiverem 1+
linha saem (e isso vai acontecer — o estimador erra bastante).

### Passo 3 — Integridade referencial e triggers
- **FK apontando para as candidatas** (`KEY_COLUMN_USAGE.REFERENCED_TABLE_NAME IN
  (...)`): se houver FK vinda de **fora** do grupo, a candidata-pai não pode ser
  dropada sem tratar o filho. FK **interna ao grupo** só define **ordem** (drope o
  filho antes do pai).
- **Triggers** na candidata (`information_schema.TRIGGERS.EVENT_OBJECT_TABLE`): se
  houver, investigue antes de incluir.

### Passo 4 — Escrita (DML recente)
- `SHOW GLOBAL STATUS LIKE 'Uptime'` → há quanto tempo os contadores acumulam.
- `information_schema.TABLES.UPDATE_TIME` por candidata. `NULL` = **sem escrita
  desde o último restart**. Combine com o uptime para saber o tamanho da janela.
- `CREATE_TIME` **recente (hoje/ontem)** é bandeira vermelha: tabela nova + vazia
  cheira a **build em andamento** (mesma família das `_old`). Tire da lista e
  investigue quem a criou antes de qualquer coisa.

### Passo 5 — Leitura real (o passo que exige privilégio)
Referência estática não pega quem lê de fora. O sinal real é o `performance_schema`:
- Tente `performance_schema.table_io_waits_summary_by_table` (`COUNT_READ`,
  `COUNT_WRITE`, `COUNT_FETCH`) filtrando pelas candidatas.
- Opcionalmente `performance_schema.events_statements_summary_by_digest` (texto das
  queries) para ver quem leu.
- **Se vier "SELECT command denied"**: o usuário do MCP não tem privilégio. **Não
  invente.** Informe o usuário e ofereça o GRANT (em `references/queries.sql`,
  seção GRANT) para ele pedir ao DBA — depois disso você roda e crava. Enquanto não
  houver leitura confirmada, **a quarentena por RENAME é o caminho** (ver Saídas).

### Passo 6 — Classificar e entregar
Agrupe as sobreviventes por natureza (framework/django, temp/scratch, exports
antigos, dashboards órfãos, features de app desativadas, etc.) e gere as Saídas.

## Views — tratamento à parte (NÃO por emptiness)

Uma view vazia **não** é candidata por estar vazia. Muitas ficam vazias **por
design**: views de alerta (`vw_*_alert` — vazia = está tudo bem) e de estado atual
(`v_*_current` — vazia = nada pendente). E views alimentam o **Looker Studio**
direto, consumo que o `information_schema` não enxerga.

O sinal certo para view morta é **estar quebrada**: referenciar tabela/coluna que
não existe mais, fazendo o `SELECT` falhar. Detecte assim:
- Liste views não referenciadas por procedure/event/outra view.
- Para cada uma, tente um `SELECT * FROM <view> LIMIT 0` (resolve as colunas sem
  varrer dados). **Erro** = view quebrada = forte candidata a DROP. **Sucesso** =
  view resolve; emptiness é irrelevante, **não** é candidata.
- Cruze as quebradas com a pasta `Dashboards/` do vault antes de sugerir o DROP.

## Saídas (o que a skill produz)

Sempre gere os três artefatos abaixo. Os scripts vão para um local que o usuário
escolha (sugestão: junto da doc, ou área de scripts do time) — **nunca** execute.

### 1. Relatório classificado (no chat)
Tabela das candidatas com: nome, grupo/natureza, `COUNT(*)`, `UPDATE_TIME`,
`CREATE_TIME`, e o status de cada critério (vazio / sem ref / sem escrita / leitura
confirmada-ou-não). Deixe claríssimo o que está **confirmado** vs **pendente**.

### 2. Script de quarentena por RENAME (preferido antes do DROP)
Em vez de apagar, renomeie para um prefixo `_zzdrop_` (ou um schema-lixeira). Se
algo externo lê a tabela, **quebra na hora e visível** → o usuário renomeia de
volta. Passada 1–2 semanas sem reclamação, o DROP é trivial. Isso transforma a
incerteza de leitura num **teste real**, sem depender do `performance_schema`.
```sql
RENAME TABLE <schema>.<tabela> TO <schema>._zzdrop_<tabela>;
```

### 3. Script de DROP datado (FK-safe)
Cabeçalho com data, schema, e a contagem. Um passo de **backup antes**
(`mysqldump` só das candidatas, ou `CREATE TABLE _bkp LIKE`+`INSERT`). Os `DROP` na
ordem FK-safe (filhos antes de pais). Tudo comentado para o DBA revisar.

### 4. Documentação no vault
- Cria/atualiza `DB_<schema>/limpeza-tabelas-vazias.md` com a análise, a lista, os
  critérios e a data.
- Acrescenta no **topo** de `log.md` uma entrada **append-only** no padrão LLM Wiki:
  `## <data> — LINT (limpeza: N tabelas candidatas, M views quebradas)` resumindo o
  que foi analisado e gerado (não reescreva linhas antigas).

## Armadilhas conhecidas (leia antes de confiar em si mesmo)

- **O estimador mente.** `TABLE_ROWS` é chute. Toda afirmação de "vazia" passa por
  `COUNT(*)`. (Custou 10 falsos-positivos numa rodada real — tinham 1 linha.)
- **`_old` e `_stage` são vivos.** São transitórios do swap atômico de tabelas
  **vivas**. Uma `tb_..._old` apareceu vazia e **sumiu** entre duas queries da mesma
  sessão — porque o pipeline (n8n) reconstruiu a tabela viva e refez o swap. Regra:
  um `X_old` só seria lixo se o `X` vivo também fosse — e tabelas vivas têm centenas
  de MB. **Nunca inclua `_old`/`_stage`.**
- **`_new`/`_aws_new` também são swap (e o sufixo nem sempre denuncia).** O alvo do
  swap pode ter nomes criativos (`X_aws_new`, `X_v2`). O teste que nunca falha é o
  **irmão vivo**: se existe uma tabela de nome-base parecido cheia/escrita hoje, a
  vazia é o alvo do próximo ciclo. Três tabelas `_aws_new` (clickbank_physical,
  gold_clickbank, dashboard_channels_marketing) caíram nessa — todas tinham irmã viva
  de 40k–330k linhas. **Sempre faça o teste do irmão vivo antes de incluir.**
- **Leitura externa é invisível à referência estática.** A própria tabela-fonte de
  um dashboard pode não ser citada por nenhuma procedure (o ETL é n8n). "Não está em
  procedure" **não** é "não é usada". Só `performance_schema` ou a quarentena fecham
  isso.
- **`CREATE_TIME` de hoje = perigo.** Tabela nova e vazia costuma ser build em
  andamento, não lixo.
- **View vazia ≠ view morta.** Emptiness é estado válido (alertas, estado atual).
  Use "quebrada", não "vazia".

## Checklist final antes de entregar

- [ ] Nenhuma `_stage`/`_old`/`_new`/`_aws_new` na lista; teste do irmão vivo feito.
- [ ] Todas as candidatas com `COUNT(*) = 0` real (não estimativa).
- [ ] Sem referência em procedure/function/event/view; FK/trigger tratados.
- [ ] `UPDATE_TIME` NULL (sem escrita) + janela de uptime conhecida.
- [ ] Leitura: confirmada via `performance_schema` **ou** declarada como pendente
      com quarentena recomendada.
- [ ] Três artefatos gerados; nenhum DDL executado por mim.
- [ ] `log.md` recebeu entrada append-only no topo.
