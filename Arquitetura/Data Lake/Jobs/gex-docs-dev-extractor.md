---
tipo: job-glue
ambiente: 
fluxo: 
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-01 06:00
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-docs-dev-extractor

> Glue ETL · fluxo **—** · ambiente **?**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x2 |
| Timeout (min) | 30 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-docs-dev-glue-role` |
| Script | `s3://gex-docs-dev-406933028738/scripts/extractor_entrypoint.py` |
| Criado | 2026-05-14 18:35:10.951000-03:00 |
| Modificado | 2026-05-15 12:10:51.873000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--CONNECTION_NAME` | gex-docs-dev-mysql-readonly |
| `--MYSQL_SCHEMA` | instituto_experience |
| `--OUTPUT_BUCKET` | gex-docs-dev-406933028738 |
| `--OUTPUT_KEY_PREFIX` | snapshots/ |
| `--extra-py-files` | s3://gex-docs-dev-406933028738/scripts/extract_mysql_metadata.py,s3://gex-docs-dev-406933028738/wheels/PyMySQL-1.1.0-py3-none-any.whl |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-01 06:00 | SUCCEEDED | 1m59s | — |
| 2026-05-25 06:00 | SUCCEEDED | 1m47s | — |
| 2026-05-18 06:00 | SUCCEEDED | 1m40s | — |
| 2026-05-15 15:49 | SUCCEEDED | 1m7s | — |
| 2026-05-15 12:11 | SUCCEEDED | 1m13s | — |
| 2026-05-14 20:37 | SUCCEEDED | 1m2s | — |
| 2026-05-14 20:32 | STOPPED | 3m35s | — |
| 2026-05-14 20:27 | SUCCEEDED | 24s | — |

## Script

> Fonte: `s3://gex-docs-dev-406933028738/scripts/extractor_entrypoint.py` — baixado do S3 (read-only).

````python
"""
Glue Spark job: gex-docs-<env>-extractor.

UNICA RESPONSABILIDADE: conectar no MySQL via VPC (Glue Connection),
extrair todos os metadados do schema, e salvar um snapshot JSON em S3
no formato que o Lambda publisher (deserialize_data) consegue consumir.

Histórico de descobertas (14-15/05/2026):
  - Lambda em VPC sem NAT não alcança Secrets Manager → dividir em
    Glue (na VPC) + Lambda (fora da VPC, via S3 trigger).
  - Glue Python Shell tem bug com args customizados / connection-names
    sendo interpretados como pacotes pip → trocar por Glue Spark.
  - mysql.connector / pymysql instalados via --additional-python-modules
    falham porque a VPC do Glue não alcança pypi.org → wheel pré-baixado
    no S3 via --extra-py-files (mas não usamos mais aqui).
  - boto3.client("glue").get_connection(...) trava porque a VPC não
    alcança o endpoint glue.us-east-1.amazonaws.com → usar o método
    interno glueContext.extract_jdbc_conf() que não faz chamada AWS.
  - glueContext.create_dynamic_frame.from_options não aceita subqueries
    + erro "Unsupported type NULL" em INFORMATION_SCHEMA → usar
    spark.read.format("jdbc").option("query", ...) com CAST AS CHAR
    em colunas que podem ter tipo ambíguo.

Fluxo:
    1. extract_jdbc_conf → URL / user / password (sem chamada AWS API)
    2. Spark JDBC → 8 queries no INFORMATION_SCHEMA:
        - ROUTINES (procedures + functions)
        - PARAMETERS
        - EVENTS
        - TABLES
        - COLUMNS
        - STATISTICS (índices)
        - KEY_COLUMN_USAGE + REFERENTIAL_CONSTRAINTS (FKs)
        - TRIGGERS
        - VIEWS
    3. Reconstroi CREATEs a partir dos metadados (não usamos SHOW CREATE
       porque é 1 query por objeto via JDBC, custoso e Spark JDBC só
       aceita SELECT em .option("query")).
    4. Monta dict no formato {schema, procedures, functions, events,
       tables, triggers, views} que serialize_data() produz.
    5. boto3 s3.put_object → snapshot em
       s3://<bucket>/<prefix>/<YYYY-MM-DD>.json

Argumentos esperados (Glue --args):
    --JOB_NAME           (Glue injeta)
    --CONNECTION_NAME    (nome da aws_glue_connection)
    --MYSQL_SCHEMA       (ex: instituto_experience)
    --OUTPUT_BUCKET      (bucket S3)
    --OUTPUT_KEY_PREFIX  (ex: snapshots/)
"""

import json
import sys
from datetime import datetime

import boto3
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

args = getResolvedOptions(sys.argv, [
    "JOB_NAME", "CONNECTION_NAME", "MYSQL_SCHEMA",
    "OUTPUT_BUCKET", "OUTPUT_KEY_PREFIX",
])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

print(f"[1] start job={args['JOB_NAME']} schema={args['MYSQL_SCHEMA']}", flush=True)

# Resolve creds via Glue interno (sem chamada AWS API)
jdbc_conf = glueContext.extract_jdbc_conf(args["CONNECTION_NAME"])
JDBC_URL = jdbc_conf["url"]
USER = jdbc_conf["user"]
PASSWORD = jdbc_conf["password"]
SCHEMA = args["MYSQL_SCHEMA"]
print("[2] creds resolved via extract_jdbc_conf", flush=True)


def jdbc(sql: str):
    """Helper: roda SQL no MySQL via Spark JDBC, retorna DataFrame."""
    return (spark.read.format("jdbc")
            .option("url", JDBC_URL)
            .option("query", sql)
            .option("user", USER)
            .option("password", PASSWORD)
            .option("driver", "com.mysql.cj.jdbc.Driver")
            .load())


def rows_as_dicts(df) -> list:
    """Coleta DataFrame como lista de dicts puros (string-friendly)."""
    return [r.asDict(recursive=True) for r in df.collect()]


# ---------------------------------------------------------------------------
# 1. Procedures + Functions (ROUTINES) + Parameters
# ---------------------------------------------------------------------------

print("[3] reading ROUTINES", flush=True)
routines_rows = rows_as_dicts(jdbc(f"""
    SELECT
        ROUTINE_NAME, ROUTINE_TYPE,
        CAST(CREATED AS CHAR)      AS CREATED,
        CAST(LAST_ALTERED AS CHAR) AS LAST_ALTERED,
        DEFINER, SECURITY_TYPE, SQL_DATA_ACCESS,
        DATA_TYPE,
        CAST(ROUTINE_DEFINITION AS CHAR) AS ROUTINE_DEFINITION
    FROM INFORMATION_SCHEMA.ROUTINES
    WHERE ROUTINE_SCHEMA = '{SCHEMA}'
"""))

print("[4] reading PARAMETERS", flush=True)
params_rows = rows_as_dicts(jdbc(f"""
    SELECT
        SPECIFIC_NAME, PARAMETER_NAME, PARAMETER_MODE,
        DATA_TYPE, ORDINAL_POSITION
    FROM INFORMATION_SCHEMA.PARAMETERS
    WHERE SPECIFIC_SCHEMA = '{SCHEMA}'
    ORDER BY SPECIFIC_NAME, ORDINAL_POSITION
"""))
params_by_routine = {}
for p in params_rows:
    if p["PARAMETER_NAME"] is None:
        # ORDINAL_POSITION 0 = retorno de função, sem nome — ignora
        continue
    params_by_routine.setdefault(p["SPECIFIC_NAME"], []).append({
        "nome": p["PARAMETER_NAME"],
        "modo": p["PARAMETER_MODE"] or "IN",
        "tipo": p["DATA_TYPE"],
        "ordem": p["ORDINAL_POSITION"],
    })

procedures = []
functions = []
for r in routines_rows:
    name = r["ROUTINE_NAME"]
    kind = r["ROUTINE_TYPE"]  # PROCEDURE | FUNCTION
    body = r["ROUTINE_DEFINITION"] or ""
    params = params_by_routine.get(name, [])
    args_str = ", ".join(f"{p['modo']} `{p['nome']}` {p['tipo']}" for p in params)
    if kind == "FUNCTION":
        ddl = f"CREATE FUNCTION `{SCHEMA}`.`{name}`({args_str}) RETURNS {r['DATA_TYPE']}\n{body}"
    else:
        ddl = f"CREATE PROCEDURE `{SCHEMA}`.`{name}`({args_str})\n{body}"
    meta = {
        "tipo": kind,
        "nome": name,
        "status": "ATIVO",
        "criado_em": r["CREATED"],
        "atualizado_em": r["LAST_ALTERED"],
        "definer": r["DEFINER"],
        "security_type": r["SECURITY_TYPE"],
        "sql_data_access": r["SQL_DATA_ACCESS"],
        "return_type": r["DATA_TYPE"] if kind == "FUNCTION" else None,
        "codigo": ddl,
        "parametros": params,
    }
    (procedures if kind == "PROCEDURE" else functions).append(meta)

print(f"[5] procedures={len(procedures)} functions={len(functions)}", flush=True)

# ---------------------------------------------------------------------------
# 2. Events
# ---------------------------------------------------------------------------

print("[6] reading EVENTS", flush=True)
events_rows = rows_as_dicts(jdbc(f"""
    SELECT
        EVENT_NAME, STATUS,
        INTERVAL_VALUE, INTERVAL_FIELD, EVENT_TYPE,
        CAST(STARTS AS CHAR)        AS STARTS,
        CAST(ENDS AS CHAR)          AS ENDS,
        CAST(LAST_EXECUTED AS CHAR) AS LAST_EXECUTED,
        CAST(CREATED AS CHAR)       AS CREATED,
        CAST(LAST_ALTERED AS CHAR)  AS LAST_ALTERED,
        DEFINER,
        CAST(EVENT_DEFINITION AS CHAR) AS EVENT_DEFINITION
    FROM INFORMATION_SCHEMA.EVENTS
    WHERE EVENT_SCHEMA = '{SCHEMA}'
"""))

events = []
for r in events_rows:
    intervalo = None
    if r["INTERVAL_VALUE"] and r["INTERVAL_FIELD"]:
        intervalo = f"{r['INTERVAL_VALUE']} {r['INTERVAL_FIELD']}"
    body = r["EVENT_DEFINITION"] or ""
    schedule = f"EVERY {intervalo}" if intervalo else "AT NOW()"
    ddl = f"CREATE EVENT `{SCHEMA}`.`{r['EVENT_NAME']}`\nON SCHEDULE {schedule}\nDO\n{body}"
    events.append({
        "nome": r["EVENT_NAME"],
        "status": r["STATUS"],
        "intervalo": intervalo,
        "event_type": r["EVENT_TYPE"],
        "starts": r["STARTS"],
        "ends": r["ENDS"],
        "last_executed": r["LAST_EXECUTED"],
        "criado_em": r["CREATED"],
        "atualizado_em": r["LAST_ALTERED"],
        "definer": r["DEFINER"],
        "codigo": ddl,
    })
print(f"[7] events={len(events)}", flush=True)

# ---------------------------------------------------------------------------
# 3. Tables + Columns + Indexes + FKs
# ---------------------------------------------------------------------------

print("[8] reading TABLES", flush=True)
tables_rows = rows_as_dicts(jdbc(f"""
    SELECT
        TABLE_NAME, ENGINE, TABLE_COLLATION, TABLE_ROWS,
        CAST(CREATE_TIME AS CHAR) AS CREATE_TIME,
        CAST(UPDATE_TIME AS CHAR) AS UPDATE_TIME,
        CAST(TABLE_COMMENT AS CHAR) AS TABLE_COMMENT
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = '{SCHEMA}' AND TABLE_TYPE = 'BASE TABLE'
"""))

print("[9] reading COLUMNS", flush=True)
columns_rows = rows_as_dicts(jdbc(f"""
    SELECT
        TABLE_NAME, COLUMN_NAME, ORDINAL_POSITION,
        CAST(COLUMN_DEFAULT AS CHAR) AS COLUMN_DEFAULT,
        IS_NULLABLE,
        CAST(COLUMN_TYPE AS CHAR) AS COLUMN_TYPE,
        COLUMN_KEY, EXTRA,
        CAST(COLUMN_COMMENT AS CHAR) AS COLUMN_COMMENT
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '{SCHEMA}'
    ORDER BY TABLE_NAME, ORDINAL_POSITION
"""))
cols_by_table = {}
for c in columns_rows:
    cols_by_table.setdefault(c["TABLE_NAME"], []).append({
        "nome": c["COLUMN_NAME"],
        "tipo": c["COLUMN_TYPE"],
        "nulo": c["IS_NULLABLE"],
        "default": c["COLUMN_DEFAULT"],
        "chave": c["COLUMN_KEY"] or "",
        "extra": c["EXTRA"] or "",
        "comentario": c["COLUMN_COMMENT"] or "",
    })

print("[10] reading INDEXES", flush=True)
indexes_rows = rows_as_dicts(jdbc(f"""
    SELECT
        TABLE_NAME, INDEX_NAME, NON_UNIQUE,
        SEQ_IN_INDEX, COLUMN_NAME, INDEX_TYPE
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = '{SCHEMA}'
    ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX
"""))
idx_acc = {}
for r in indexes_rows:
    key = (r["TABLE_NAME"], r["INDEX_NAME"])
    entry = idx_acc.setdefault(key, {
        "nome": r["INDEX_NAME"],
        "unico": r["NON_UNIQUE"] == 0,
        "tipo": r["INDEX_TYPE"],
        "colunas": [],
    })
    entry["colunas"].append(r["COLUMN_NAME"])
idx_by_table = {}
for (table, _), entry in idx_acc.items():
    idx_by_table.setdefault(table, []).append(entry)

print("[11] reading FKs", flush=True)
fks_rows = rows_as_dicts(jdbc(f"""
    SELECT
        kcu.TABLE_NAME, kcu.CONSTRAINT_NAME,
        kcu.COLUMN_NAME,
        kcu.REFERENCED_TABLE_NAME, kcu.REFERENCED_COLUMN_NAME,
        rc.UPDATE_RULE, rc.DELETE_RULE
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
    INNER JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
        ON kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
       AND kcu.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA
    WHERE kcu.TABLE_SCHEMA = '{SCHEMA}'
      AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
    ORDER BY kcu.TABLE_NAME, kcu.CONSTRAINT_NAME, kcu.ORDINAL_POSITION
"""))
fk_by_table = {}
for r in fks_rows:
    fk_by_table.setdefault(r["TABLE_NAME"], []).append({
        "nome": r["CONSTRAINT_NAME"],
        "coluna": r["COLUMN_NAME"],
        "tabela_referenciada": r["REFERENCED_TABLE_NAME"],
        "coluna_referenciada": r["REFERENCED_COLUMN_NAME"],
        "update_rule": r["UPDATE_RULE"],
        "delete_rule": r["DELETE_RULE"],
    })

tables = []
for t in tables_rows:
    name = t["TABLE_NAME"]
    cols = cols_by_table.get(name, [])
    # Reconstrói CREATE TABLE básico a partir de COLUMNS.
    col_defs = []
    for c in cols:
        nullable = "" if c["nulo"] == "YES" else " NOT NULL"
        default = f" DEFAULT {c['default']}" if c["default"] is not None else ""
        extra = f" {c['extra']}" if c["extra"] else ""
        cmnt = f" COMMENT '{c['comentario']}'" if c["comentario"] else ""
        col_defs.append(f"  `{c['nome']}` {c['tipo']}{nullable}{default}{extra}{cmnt}")
    ddl = (
        f"CREATE TABLE `{SCHEMA}`.`{name}` (\n"
        + ",\n".join(col_defs)
        + f"\n) ENGINE={t['ENGINE']} DEFAULT COLLATE={t['TABLE_COLLATION']};"
    )
    tables.append({
        "nome": name,
        "engine": t["ENGINE"],
        "charset": t["TABLE_COLLATION"],
        "linhas_estimadas": t["TABLE_ROWS"],
        "create_time": t["CREATE_TIME"],
        "update_time": t["UPDATE_TIME"],
        "comentario": t["TABLE_COMMENT"] or None,
        "ddl": ddl,
        "colunas": cols,
        "indices": idx_by_table.get(name, []),
        "fks": fk_by_table.get(name, []),
    })
print(f"[12] tables={len(tables)}", flush=True)

# ---------------------------------------------------------------------------
# 4. Triggers
# ---------------------------------------------------------------------------

print("[13] reading TRIGGERS", flush=True)
triggers_rows = rows_as_dicts(jdbc(f"""
    SELECT
        TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE,
        ACTION_TIMING,
        CAST(ACTION_STATEMENT AS CHAR) AS ACTION_STATEMENT,
        CAST(CREATED AS CHAR) AS CREATED,
        DEFINER
    FROM INFORMATION_SCHEMA.TRIGGERS
    WHERE TRIGGER_SCHEMA = '{SCHEMA}'
"""))
triggers = []
for r in triggers_rows:
    body = r["ACTION_STATEMENT"] or ""
    ddl = (
        f"CREATE TRIGGER `{SCHEMA}`.`{r['TRIGGER_NAME']}`\n"
        f"{r['ACTION_TIMING']} {r['EVENT_MANIPULATION']} "
        f"ON `{r['EVENT_OBJECT_TABLE']}`\n"
        f"FOR EACH ROW\n{body}"
    )
    triggers.append({
        "nome": r["TRIGGER_NAME"],
        "tabela": r["EVENT_OBJECT_TABLE"],
        "evento": r["EVENT_MANIPULATION"],
        "timing": r["ACTION_TIMING"],
        "action": r["ACTION_STATEMENT"],
        "criado_em": r["CREATED"],
        "definer": r["DEFINER"],
        "codigo": ddl,
    })
print(f"[14] triggers={len(triggers)}", flush=True)

# ---------------------------------------------------------------------------
# 5. Views
# ---------------------------------------------------------------------------

print("[15] reading VIEWS", flush=True)
views_rows = rows_as_dicts(jdbc(f"""
    SELECT
        TABLE_NAME AS VIEW_NAME,
        CAST(VIEW_DEFINITION AS CHAR) AS VIEW_DEFINITION,
        CHECK_OPTION, IS_UPDATABLE, DEFINER
    FROM INFORMATION_SCHEMA.VIEWS
    WHERE TABLE_SCHEMA = '{SCHEMA}'
"""))
views = []
for r in views_rows:
    body = r["VIEW_DEFINITION"] or ""
    ddl = f"CREATE VIEW `{SCHEMA}`.`{r['VIEW_NAME']}` AS\n{body};"
    views.append({
        "nome": r["VIEW_NAME"],
        "definicao": body,
        "check_option": r["CHECK_OPTION"],
        "is_updatable": r["IS_UPDATABLE"],
        "definer": r["DEFINER"],
        "codigo": ddl,
    })
print(f"[16] views={len(views)}", flush=True)

# ---------------------------------------------------------------------------
# 6. Monta snapshot final + upload pro S3
# ---------------------------------------------------------------------------

snapshot = {
    "schema": SCHEMA,
    "procedures": procedures,
    "functions":  functions,
    "events":     events,
    "tables":     tables,
    "triggers":   triggers,
    "views":      views,
    "_run": {
        "job_name": args["JOB_NAME"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "schema": SCHEMA,
    },
}

prefix = args["OUTPUT_KEY_PREFIX"].rstrip("/")
date_str = datetime.utcnow().strftime("%Y-%m-%d")
key = f"{prefix}/{date_str}.json"

body = json.dumps(snapshot, ensure_ascii=False, default=str).encode("utf-8")
print(f"[17] uploading {len(body)} bytes to s3://{args['OUTPUT_BUCKET']}/{key}", flush=True)

boto3.client("s3").put_object(
    Bucket=args["OUTPUT_BUCKET"],
    Key=key,
    Body=body,
    ContentType="application/json",
)
print(f"[18] OK: s3://{args['OUTPUT_BUCKET']}/{key}", flush=True)

job.commit()
````

## Relacionados
[[00-Data-Lake]]
