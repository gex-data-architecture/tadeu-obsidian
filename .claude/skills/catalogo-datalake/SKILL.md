---
name: catalogo-datalake
description: >-
  Cataloga o Data Lake da AWS (Glue Data Catalog + ETL Jobs + Crawlers + Step Functions +
  regras EventBridge) e gera/atualiza a pasta `Data Lake/` no vault Obsidian — uma nota por
  tabela (bronze/silver/gold, develop/prod), por job de ETL, por crawler e por Step Function,
  mais o índice e o mapa de orquestração. Use SEMPRE que o usuário falar em "data lake",
  "catálogo de tabelas/jobs", "glue", "athena", "bronze/silver/gold", "camadas medallion",
  "atualizar o data lake", "documentar os jobs", "step functions", "orquestração",
  "como os jobs são encadeados", "crawlers", "agendamentos", "schedules", "cron",
  "horário dos jobs", "o que roda e quando", "EventBridge", "pipeline de dados na AWS", ou pedir o
  inventário do lake — mesmo sem dizer a palavra "skill". É SOMENTE LEITURA na AWS
  (glue/sfn/events get_/list_/describe_), nunca cria/edita/dropa nada lá; só escreve markdown.
  Conta/região padrão: 406933028738 / us-east-1, perfil AWS `buygoods`.
---

# catalogo-datalake

Mantém a documentação do **Data Lake da AWS** dentro do vault, em sincronia com a
realidade do AWS Glue. É o equivalente, para o lake, do que `3_gerar_vault.py` é para o
MySQL: lê a fonte da verdade (aqui, o Glue Data Catalog + os ETL Jobs) e regenera as
notas. Tabela/job que sumiu na AWS some do vault na próxima geração.

## Princípio de segurança (inviolável)
- **Somente leitura na AWS.** Use exclusivamente chamadas de leitura:
  `glue.get_databases`, `glue.get_tables`, `glue.get_jobs`, `glue.get_job_runs`,
  `glue.get_crawlers`/`batch_get_crawlers`, `sfn.list_state_machines`/`describe_state_machine`/
  `list_executions`, `events.list_rules`/`list_targets_by_rule`,
  `scheduler.list_schedules`/`get_schedule` (EventBridge Scheduler), e `s3.get_object` (apenas o
  **script** ETL na `ScriptLocation`) — e congêneres `get_*`/`list_*`/`describe_*`. **NUNCA**
  `create_*`, `update_*`, `delete_*`, `put_object`, `start_job_run`, `start_execution`,
  `put_rule`, `put_targets`, `enable_rule`/`disable_rule`, nem qualquer mutação. A skill não roda
  jobs/crawlers/SFN, não liga/desliga agendamentos nem altera o catálogo ou as regras — só descreve.
- No S3 ela só **lê o arquivo do script** do job; **não toca nos dados** (não baixa
  parquet, não move, não apaga objetos) e nunca escreve no bucket.
- O único efeito colateral é **escrever markdown** na pasta `Data Lake/` do vault.

## Pré-requisitos
- `boto3` instalado e AWS CLI configurado.
- Perfil AWS com permissão de leitura no Glue (padrão `buygoods`). Para usar outro:
  `set AWS_PROFILE=<perfil>` antes de rodar (PowerShell: `$env:AWS_PROFILE="<perfil>"`).
- Região `us-east-1` (sobrescreva com `AWS_REGION` se necessário).

## Como rodar
```powershell
$env:AWS_PROFILE = "buygoods"
python "C:\Users\tadeu\DataTeamDocs\.claude\skills\catalogo-datalake\scripts\gerar_datalake.py"
```
O script (`scripts/gerar_datalake.py`):
1. Lista os **databases** do Glue (`gex_db_<develop|prod>_<bronze|silver|gold>`).
2. Para cada database, lista as **tabelas** e gera uma nota por tabela com: database,
   camada, ambiente, formato (parquet/…), location no S3, partições, e a lista de colunas.
3. Lista os **ETL Jobs** e gera uma nota por job com: tipo (glueetl/pythonshell), Glue
   version, worker/quantidade, role, script (S3), timeout/retries e os **parâmetros de
   negócio** (`--DATABASE_NAME`, `--source_bucket`, `--target_bucket`, `--read_mode`, …).
   Além disso, cada nota de job traz as **últimas execuções** (`glue.get_job_runs` — início,
   estado, duração e erro; e `ultima_execucao`/`ultimo_estado` no frontmatter) e o **script
   ETL embutido**, baixado do S3 (`s3.get_object` na `ScriptLocation`) num bloco de código.
   Tudo somente leitura.
4. Lista os **crawlers** do Glue (`glue.get_crawlers`/`batch_get_crawlers`) e gera uma nota
   por crawler em `Orquestracao/`, com o database/target alvo e o último estado.
5. Lista as **Step Functions** (`sfn.list_state_machines`/`describe_state_machine`) e gera
   uma nota por SFN em `Orquestracao/`, com: o **Fluxo** passo a passo do ASL (jobs ▶️,
   crawlers 🕷️, SFN aninhadas ⤵️ — descendo em `Parallel`/`Map`), o **Encadeamento**
   (quem dispara esta SFN e o que ela dispara ao concluir), os alvos (jobs/crawlers/SFN),
   as **últimas execuções** (`list_executions`) e a **definição ASL** embutida.
6. Lê as **regras do EventBridge** (`events.list_rules`/`list_targets_by_rule`) e parseia o
   `EventPattern` (`source: aws.glue`, `detail.jobName`+`state`): regras `SUCCEEDED → startExecution`
   viram **arestas de encadeamento** entre SFNs; regras `FAILED/TIMEOUT/STOPPED → SNS` viram
   **alertas de falha**. É assim que o encadeamento *entre* SFNs é reconstruído (ele NÃO mora
   no ASL — mora nas regras EventBridge).
6b. Lê os **agendamentos (cron/rate)** das duas fontes: regras EventBridge com `ScheduleExpression`
   e o serviço novo **EventBridge Scheduler** (`scheduler.list_schedules`/`get_schedule`). Para cada um
   resolve status (ENABLED/DISABLED), horário (traduzido p/ legível em **UTC**), expressão e o **alvo**
   (SFN/job/crawler/lambda) — inclusive os *universal targets* `aws-sdk:glue:startJobRun`, cujo nome real
   do job vem do `Input` JSON. São esses agendamentos que **iniciam as cadeias** na hora marcada; quando
   um deles dispara uma SFN, isso aparece na seção *Agendada* da nota da SFN.
7. Gera o índice `00-Data-Lake.md` (databases, tabelas, jobs, Step Functions, crawlers, agendamentos)
   e o mapa `Orquestracao/00-Orquestracao.md` (cadeias a partir de cada raiz, grafo mermaid,
   alertas de falha, **tabela de agendamentos** com status/horário/expressão/alvo, lista de crawlers).
8. **Remove notas órfãs**: qualquer `.md` que não corresponda mais a um objeto da AWS é
   apagado, e subpastas de database vazias são removidas. A pasta vira espelho do lake.

## Estrutura gerada
```
Data Lake/
├── 00-Data-Lake.md                  (índice — gerado)
├── Tabelas/
│   └── <database>/<tabela>.md        (1 por tabela do Glue Catalog)
├── Jobs/
│   └── <job>.md                      (1 por ETL Job)
└── Orquestracao/
    ├── 00-Orquestracao.md            (mapa: cadeias + grafo mermaid + alertas)
    ├── <step-function>.md            (1 por Step Function: Fluxo/Encadeamento/ASL)
    └── <crawler>.md                  (1 por crawler do Glue)
```
Tudo aqui é **GERADO** (sobrescrito a cada rodada). Conhecimento curado sobre o lake
(decisões, contexto de negócio, runbooks) vai em `Conhecimento/`, nunca dentro de `Data Lake/`.

## Convenções do lake (BHG) — para ler as notas
- **Medallion**: `landing → bronze → silver → gold → MySQL`. Fluxo refletido nos nomes
  dos jobs (`landing-to-bronze-*`, `bronze-to-silver-*`, `silver-to-gold-*`, `*-to-mysql`).
- **Ambientes paralelos** `develop` e `prod`: cada camada/job costuma ter as duas versões.
- O lake **alimenta o `instituto_experience`** (MySQL): os jobs `*-to-mysql` escrevem as
  tabelas-fonte que o vault `DB_instituto_experience` documenta. É o elo entre os dois mundos.
- Tabelas silver/gold normalmente são **parquet particionado** (ex.: por `dt_proc`).

## Após gerar
- Acrescente uma linha no `log.md` (append-only) registrando a sincronização.
- Se algum job `*-to-mysql` aponta para uma tabela do `instituto_experience`, vale criar
  o `[[wikilink]]` curado ligando os dois catálogos (feito à mão, em `Conhecimento/`).
