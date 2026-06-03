---
tipo: job-glue
ambiente: develop
fluxo: to-mysql
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: —
ultimo_estado: —
tags: [datalake, glue-job]
---

# gex-buygoods-unified-to-mysql-develop

> Glue ETL · fluxo **to-mysql** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x4 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-develop` |
| Script | `s3://gex-datalake-bronze-develop/scripts/buygoods_unified/jobs/silver_to_mysql_buygoods_unified.py` |
| Criado | 2026-06-01 17:37:15.472000-03:00 |
| Modificado | 2026-06-01 17:37:15.472000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--API_LOCATION` | s3://gex-datalake-silver-develop/buygoods_orders_dev/ |
| `--DB_TABLE` | tb_gex_buygoods_unified_dev |
| `--GLUE_CONNECTION_NAME` | gex-mysql-connection-develop |
| `--MIN_ROWS_THRESHOLD` | 1 |
| `--TARGET_DATABASE` | instituto_experience |
| `--WEBHOOK_LOCATION` | s3://gex-datalake-silver-develop/buygoods_physical_new/ |

## Últimas execuções

> Sem histórico de execuções (job nunca rodou ou sem acesso ao histórico).

## Script

> Fonte: `s3://gex-datalake-bronze-develop/scripts/buygoods_unified/jobs/silver_to_mysql_buygoods_unified.py` — baixado do S3 (read-only).

````python
"""
Glue Job: silver_to_mysql_buygoods_unified
==========================================
Unifica a fonte unica da verdade BuyGoods a partir das DUAS silvers (lidas do
S3/Data Lake) e publica no MySQL instituto_experience.tb_gex_buygoods_unified
usando SWAP ATOMICO de tabela (mesmo padrao dos demais jobs *-to-mysql do repo).

Fontes (Athena/S3, gex_db_<env>_silver):
  - API/historico : tb_silver_buygoods_orders     (pasta buygoods_orders[_dev])
  - Webhook       : tb_buygoods_physical_new       (pasta buygoods_physical_new)

Regra de unificacao (WEBHOOK tem prioridade):
  - todos os registros do webhook
  - + registros do historico cujo transaction_id NAO existe no webhook
  - coluna data_source = 'webhook' | 'api'

Reconciliacao de schema (decisao do time): subid*/utm_* sao o MESMO dado com
nomes diferentes. O webhook usa subid..subid5; renomeamos para os utm_*
equivalentes para a tabela unificada ter colunas unicas:
  subid->utm_source, subid2->utm_content, subid3->utm_campaign,
  subid4->utm_term, subid5->utm_medium
cancel_reason existe so na API; no lado webhook entra como NULL.

=== CREDENCIAIS ===
  Lidas da Glue Connection via glue_context.extract_jdbc_conf() (sem Secrets Manager).

=== FLUXO ===
  [1] Le API silver e Webhook silver (parquet, direto do LOCATION no S3)
  [2] Reconcilia colunas e monta o UNION (webhook + api_only)
  [3] Carrega credenciais da Glue Connection
  [4] Escreve no staging (overwrite) -> Spark cria a tabela pelo schema do DF
  [5] CREATE TABLE IF NOT EXISTS <final> LIKE <staging> (auto-bootstrap 1a run)
  [6] Valida contagem do staging
  [7] RENAME TABLE atomico (final<->backup, staging->final)
  [8] Limpa backup

Parametros (--CHAVE valor):
  --JOB_NAME             (req, injetado pelo Glue)
  --GLUE_CONNECTION_NAME (req)   ex: gex-mysql-connection-prod
  --API_LOCATION         (req)   ex: s3://gex-datalake-silver-prod/buygoods_orders/
  --WEBHOOK_LOCATION     (req)   ex: s3://gex-datalake-silver-prod/buygoods_physical_new/
  --DB_TABLE             (opt)   default: tb_gex_buygoods_unified
  --TARGET_DATABASE      (opt)   default: instituto_experience
  --MIN_ROWS_THRESHOLD   (opt)   default: 1000
"""

import re
import sys
import time

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import functions as F


def get_optional_arg(name: str, default: str) -> str:
    token = f"--{name}"
    if token in sys.argv:
        idx = sys.argv.index(token)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return default


# ---------------------------------------------------------------------------
# Schema da tabela unificada (de-para subid->utm ja reconciliado)
# ---------------------------------------------------------------------------
# Colunas comuns as duas silvers (sem utm_*/subid*/cancel_reason).
COMMON_COLS = [
    "transaction_id", "transaction_type", "payment_status", "platform",
    "client_name", "client_email", "client_phone", "client_zip",
    "client_country", "client_state", "client_city", "client_street",
    "product_name", "product_sku", "product_codename", "product_id",
    "offer_name", "quantity", "sales_type", "vendor_name", "product_cost",
    "product_cost_usd", "total_collected_usd", "total_price_usd", "iva_usd",
    "taxes_usd", "affiliate_amount_usd", "exchange_rate", "total_price",
    "taxes", "iva", "affiliate_amount", "commission_usd", "commission",
    "total_refund_usd", "total_refund", "refund_fee_usd", "refund_fee",
    "chargeback_fee_usd", "chargeback_fee", "date_refunded",
    "datetime_refunded_platform", "affiliate_id", "account_id",
    "affiliate_name", "is_house_traffic", "upsell_parent_receipt",
    "created_at_date", "created_at_hour", "datetime_platform", "created_at",
    "updated_at", "pipeline_updated_at", "dt_proc",
]
# Colunas reconciliadas (utm_* preenchidas das duas fontes; cancel_reason so API).
UTM_COLS = ["utm_source", "utm_content", "utm_campaign", "utm_term", "utm_medium"]
# de-para subid -> utm (ordem importa)
SUBID_TO_UTM = {
    "subid": "utm_source",
    "subid2": "utm_content",
    "subid3": "utm_campaign",
    "subid4": "utm_term",
    "subid5": "utm_medium",
}
# Ordem final das colunas de dados (sem id/data_source, que sao adicionadas depois).
UNIFIED_COLS = COMMON_COLS + ["cancel_reason"] + UTM_COLS

# --- parametros ---
MYSQL_TABLE = get_optional_arg("DB_TABLE", "tb_gex_buygoods_unified")
STAGING_TABLE = f"{MYSQL_TABLE}_old"
BACKUP_TABLE = f"{MYSQL_TABLE}_backup"
DEFAULT_DATABASE = get_optional_arg("TARGET_DATABASE", "instituto_experience")
API_LOCATION = get_optional_arg("API_LOCATION", "")
WEBHOOK_LOCATION = get_optional_arg("WEBHOOK_LOCATION", "")


def quote_ident(name: str) -> str:
    return f"`{name.replace('`', '``')}`"


def parse_jdbc_url(url: str):
    with_db = re.match(r"jdbc:mysql://([^:/]+):(\d+)/([^?]+)", url or "")
    if with_db:
        return with_db.group(1), int(with_db.group(2)), with_db.group(3)
    without_db = re.match(r"jdbc:mysql://([^:/]+):(\d+)$", url or "")
    if without_db:
        return without_db.group(1), int(without_db.group(2)), DEFAULT_DATABASE
    raise ValueError(f"Cannot parse JDBC URL: {url!r}")


def build_jdbc_url(host: str, port: int, database: str) -> str:
    return (
        f"jdbc:mysql://{host}:{port}/{database}"
        "?useSSL=true"
        "&serverTimezone=UTC"
        "&rewriteBatchedStatements=true"
    )


class JdbcExecutor:
    """Executa DDL/DML no MySQL via JDBC (Py4J)."""

    def __init__(self, spark, jdbc_url: str, user: str, password: str):
        self._jvm = spark._jvm
        props = self._jvm.java.util.Properties()
        props.setProperty("user", user)
        props.setProperty("password", password)
        self._jvm.java.lang.Class.forName("com.mysql.cj.jdbc.Driver")
        self._conn = self._jvm.java.sql.DriverManager.getConnection(jdbc_url, props)

    def execute(self, sql: str) -> None:
        stmt = self._conn.createStatement()
        try:
            stmt.execute(sql)
        finally:
            stmt.close()

    def fetch_scalar_int(self, sql: str) -> int:
        stmt = self._conn.createStatement()
        try:
            rs = stmt.executeQuery(sql)
            try:
                return int(rs.getLong(1)) if rs.next() else 0
            finally:
                rs.close()
        finally:
            stmt.close()

    def table_exists(self, database: str, table: str) -> bool:
        count = self.fetch_scalar_int(
            "SELECT COUNT(*) FROM information_schema.tables "
            f"WHERE table_schema = '{database}' AND table_name = '{table}'"
        )
        return count > 0

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass


args = getResolvedOptions(sys.argv, ["JOB_NAME", "GLUE_CONNECTION_NAME"])

start = time.time()

_conf = SparkConf()
_conf.set("spark.sql.files.ignoreMissingFiles", "true")
_conf.set("spark.sql.session.timeZone", "America/Sao_Paulo")
sc = SparkContext(conf=_conf)
glue_context = GlueContext(sc)
spark = glue_context.spark_session

job = Job(glue_context)
job.init(args["JOB_NAME"], args)

glue_connection_name = args["GLUE_CONNECTION_NAME"]
min_rows_threshold = int(get_optional_arg("MIN_ROWS_THRESHOLD", "1000"))

if not API_LOCATION or not WEBHOOK_LOCATION:
    raise RuntimeError("--API_LOCATION e --WEBHOOK_LOCATION sao obrigatorios.")


def align_to_unified(df):
    """Garante que o DF tenha exatamente UNIFIED_COLS (faltantes viram NULL string)."""
    existing = set(df.columns)
    for col in UNIFIED_COLS:
        if col not in existing:
            df = df.withColumn(col, F.lit(None).cast("string"))
    return df.select(*UNIFIED_COLS)


print(f"[STEP 1] Lendo API silver de {API_LOCATION} ...")
api_raw = spark.read.option("ignoreMissingFiles", "true").parquet(API_LOCATION)
# API ja possui utm_* e cancel_reason; alinhamos a ordem unificada.
api_df = align_to_unified(api_raw).withColumn("data_source", F.lit("api"))

print(f"[STEP 1] Lendo Webhook silver de {WEBHOOK_LOCATION} ...")
wh_raw = spark.read.option("ignoreMissingFiles", "true").parquet(WEBHOOK_LOCATION)
# Reconcilia subid* -> utm_* (mesmo dado, nome diferente).
for subid, utm in SUBID_TO_UTM.items():
    if subid in wh_raw.columns:
        wh_raw = wh_raw.withColumnRenamed(subid, utm)
wh_df = align_to_unified(wh_raw).withColumn("data_source", F.lit("webhook"))

print("[STEP 2] Montando UNION com prioridade do webhook ...")
# transaction_ids presentes no webhook (chave de prioridade).
wh_ids = (
    wh_df.where(F.col("transaction_id").isNotNull())
    .select("transaction_id")
    .distinct()
)
# historico que NAO existe no webhook.
api_only = api_df.join(wh_ids, on="transaction_id", how="left_anti")

unified = wh_df.unionByName(api_only)
unified = unified.withColumn("id", F.monotonically_increasing_id().cast("bigint"))
unified = unified.select(["id"] + UNIFIED_COLS + ["data_source"])

total_webhook = wh_df.count()
total_api_only = api_only.count()
total_unified = unified.count()
print(
    f"[STEP 2] total_webhook={total_webhook} total_api_only={total_api_only} "
    f"total_unified={total_unified}"
)
if total_unified != total_webhook + total_api_only:
    raise RuntimeError(
        "Inconsistencia na unificacao: total_unified != total_webhook + total_api_only "
        f"({total_unified} != {total_webhook} + {total_api_only})"
    )
if total_unified < min_rows_threshold:
    raise RuntimeError(
        f"total_unified abaixo do threshold. total_unified={total_unified} "
        f"threshold={min_rows_threshold}"
    )

print(f"[STEP 3] Extraindo credenciais da Glue Connection ({glue_connection_name})...")
jdbc_conf = glue_context.extract_jdbc_conf(glue_connection_name)
raw_url = jdbc_conf.get("url") or jdbc_conf.get("fullUrl", "")
user = jdbc_conf.get("user") or jdbc_conf.get("username", "")
password = jdbc_conf.get("password", "")
host, port, database = parse_jdbc_url(raw_url)
jdbc_url = build_jdbc_url(host, port, database)
print(f"[STEP 3] OK host={host} port={port} db={database}")

executor = JdbcExecutor(spark, jdbc_url, user, password)

try:
    # Salvaguarda: se a tabela final ja existe e tem volume, nao publicar um
    # snapshot muito menor (provavel leitura incompleta da silver upstream).
    if executor.table_exists(database, MYSQL_TABLE):
        current_count = executor.fetch_scalar_int(
            f"SELECT COUNT(*) FROM {quote_ident(MYSQL_TABLE)}"
        )
        if current_count >= min_rows_threshold and total_unified < int(current_count * 0.90):
            raise RuntimeError(
                "Snapshot unificado parece incompleto vs tabela atual. "
                f"total_unified={total_unified} current_count={current_count}. Retry later."
            )
        print(f"[STEP 3.5] OK total_unified={total_unified} current_count={current_count}")

    print(f"[STEP 4] Escrevendo {total_unified} linhas no staging {STAGING_TABLE} (overwrite)...")
    (
        unified.write.mode("overwrite")
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", STAGING_TABLE)
        .option("user", user)
        .option("password", password)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .option("batchsize", "10000")
        .save()
    )
    print("[STEP 4] OK escrita no staging concluida")

    # Auto-bootstrap: cria a tabela final na 1a execucao com o mesmo schema do staging.
    print(f"[STEP 5] Garantindo existencia da tabela final {MYSQL_TABLE} (CREATE IF NOT EXISTS LIKE staging)...")
    executor.execute(
        f"CREATE TABLE IF NOT EXISTS {quote_ident(MYSQL_TABLE)} LIKE {quote_ident(STAGING_TABLE)}"
    )

    print("[STEP 6] Validando contagem do staging...")
    staging_count = executor.fetch_scalar_int(
        f"SELECT COUNT(*) FROM {quote_ident(STAGING_TABLE)}"
    )
    if staging_count < min_rows_threshold:
        raise RuntimeError(
            f"Staging abaixo do threshold. staging_count={staging_count} threshold={min_rows_threshold}"
        )
    print(f"[STEP 6] OK staging_count={staging_count}")

    print("[STEP 7] Swap atomico (RENAME TABLE)...")
    executor.execute(f"DROP TABLE IF EXISTS {quote_ident(BACKUP_TABLE)}")
    executor.execute(
        "RENAME TABLE "
        f"{quote_ident(MYSQL_TABLE)} TO {quote_ident(BACKUP_TABLE)}, "
        f"{quote_ident(STAGING_TABLE)} TO {quote_ident(MYSQL_TABLE)}"
    )
    print("[STEP 7] OK swap concluido")

    print("[STEP 8] Limpando backup...")
    executor.execute(f"DROP TABLE IF EXISTS {quote_ident(BACKUP_TABLE)}")
    print("[STEP 8] OK")

finally:
    executor.close()

elapsed = int(time.time() - start)
print(
    f"[FINAL] OK unificacao concluida em {elapsed}s | "
    f"total_webhook={total_webhook} total_api_only={total_api_only} total_unified={total_unified}"
)
job.commit()
````

## Relacionados
[[00-Data-Lake]]
