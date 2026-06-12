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

Regra de unificacao (API = FONTE DA VERDADE, reconciliacao por evento mais avancado):
  - FULL OUTER por transaction_id (nao mais anti-join).
  - so webhook -> webhook; so API -> API.
  - nos dois -> campos de ESTADO (status/refund/datas/fees) vem da fonte com o
    payment_status mais avancado (empate -> API); demais campos coalesce(API, webhook);
    cancel_reason coalesce(API, webhook) (so a API tem).
  - coluna data_source = 'api' (existe na API) | 'webhook'

Reconciliacao de schema (decisao do time): subid*/utm_* sao o MESMO dado com
nomes diferentes. O webhook usa subid..subid5; renomeamos para os utm_*
equivalentes para a tabela unificada ter colunas unicas:
  subid->utm_source, subid2->utm_content, subid3->utm_campaign,
  subid4->utm_term, subid5->utm_medium
cancel_reason existe so na API; no lado webhook entra como NULL.

=== CREDENCIAIS ===
  Lidas da Glue Connection via glue_context.extract_jdbc_conf() (sem Secrets Manager).

=== FLUXO ===
  [1] Le API silver e Webhook silver (parquet, direto do LOCATION no S3; com retry)
  [2] Reconcilia webhook x API por transaction_id (API = fonte da verdade)
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


# ===========================================================================
# Enriquecimento de offer_name — absorve a procedure MySQL
# fill_buygoods_offer_names (5 cenarios) DENTRO do job, sobre a UNIFICADA
# (mesma tabela em que a procedure operava). Fontes de referencia lidas do
# MySQL (mesmas da procedure): buygoods_products, buygoods_internal_affiliates.
# Nao altera o schema de saida — apenas recomputa offer_name e is_house_traffic.
# ===========================================================================
PRODUCTS_TABLE = get_optional_arg("PRODUCTS_MYSQL_TABLE", "buygoods_products")
INTERNAL_AFF_TABLE = get_optional_arg("INTERNAL_AFFILIATES_MYSQL_TABLE", "buygoods_internal_affiliates")


def build_house_offer_name(offer_col_name, ts_col_name, tm_col_name):
    """House traffic: troca 'Affiliate Marketing' pelo traffic_source e insere a
    tag [Gestor de Tráfego: ...] antes do ultimo segmento (se houver '] ['),
    senao concatena no final. Equivalente ao REPLACE/SUBSTRING_INDEX do MySQL.

    Recebe NOMES de coluna (str). A troca de 'Affiliate Marketing' pelo valor de
    uma COLUNA (traffic_source) e feita via F.expr porque o Spark 3.3 (Glue 4.0)
    nao aceita Column como replacement em F.regexp_replace."""
    replaced = F.expr(
        f"regexp_replace(`{offer_col_name}`, 'Affiliate Marketing', coalesce(`{ts_col_name}`, ''))"
    )
    last_segment = F.regexp_extract(replaced, r"\] \[([^\]]+)\]$", 1)
    prefix = F.regexp_replace(replaced, r"\] \[[^\]]+\]$", "")
    tm = F.col(tm_col_name)
    return F.when(
        replaced.rlike(r"\] \["),
        F.concat(prefix, F.lit("] [Gestor de Tráfego: "), tm, F.lit("] ["), last_segment, F.lit("]")),
    ).otherwise(
        F.concat(replaced, F.lit(" [Gestor de Tráfego: "), tm, F.lit("]"))
    )


def add_gestor_to_existing(offer_col, traffic_manager_col):
    """Cenario 4: adiciona a tag [Gestor de Tráfego: ...] ao offer_name EXISTENTE
    (nao usa catalogo), igual ao SQL da procedure (cb.offer_name)."""
    last_segment = F.regexp_extract(offer_col, r"\] \[([^\]]+)\]$", 1)
    prefix = F.regexp_replace(offer_col, r"\] \[[^\]]+\]$", "")
    return F.when(
        offer_col.rlike(r"\] \["),
        F.concat(prefix, F.lit("] [Gestor de Tráfego: "), traffic_manager_col, F.lit("] ["), last_segment, F.lit("]")),
    ).otherwise(
        F.concat(offer_col, F.lit(" [Gestor de Tráfego: "), traffic_manager_col, F.lit("]"))
    )


def enrich_offer_names(df):
    """Aplica os 5 cenarios da procedure fill_buygoods_offer_names sobre a unificada."""
    # --- internal affiliates (MySQL) ---
    ia = glue_context.create_dynamic_frame.from_options(
        connection_type="mysql",
        connection_options={
            "useConnectionProperties": "true",
            "dbtable": f"{DEFAULT_DATABASE}.{INTERNAL_AFF_TABLE}",
            "connectionName": glue_connection_name,
        },
    ).toDF()
    ia = ia.toDF(*[c.lower() for c in ia.columns])
    ts_src = F.trim(F.col("traffic_source")) if "traffic_source" in ia.columns else F.lit(None)
    tm_src = F.trim(F.col("traffic_manager")) if "traffic_manager" in ia.columns else F.lit(None)
    ia_sel = (
        ia.withColumn("_aff_key", F.lower(F.trim(F.regexp_replace(F.col("affiliate_name"), " +", " "))))
        .withColumn("_traffic_source", ts_src)
        .withColumn("_traffic_manager", tm_src)
        .withColumn("_is_internal", F.lit(1))
        .select("_aff_key", "_traffic_source", "_traffic_manager", "_is_internal")
        .dropDuplicates(["_aff_key"])
    )

    # --- products (MySQL) ---
    pr = glue_context.create_dynamic_frame.from_options(
        connection_type="mysql",
        connection_options={
            "useConnectionProperties": "true",
            "dbtable": f"{DEFAULT_DATABASE}.{PRODUCTS_TABLE}",
            "connectionName": glue_connection_name,
        },
    ).toDF()
    pr = pr.toDF(*[c.lower() for c in pr.columns])
    has_locked = "offer_name_locked" in pr.columns
    if not has_locked:
        print("[INFO] offer_name_locked ausente em products — fallback 0 aplicado (cenarios 1/2/3 nao disparam)")
    locked_col = F.col("offer_name_locked") if has_locked else F.lit(0)
    pr_sel = (
        pr.withColumn("_prod_key", F.lower(F.trim(F.col("product_id").cast("string"))))
        .withColumn("_acct_key", F.lower(F.trim(F.col("account_name").cast("string"))))
        .withColumn("_cat_offer", F.trim(F.col("offer_name")))
        .withColumn("_locked", F.coalesce(locked_col.cast("int"), F.lit(0)))
        .select("_prod_key", "_acct_key", "_cat_offer", "_locked")
        .dropDuplicates(["_prod_key", "_acct_key"])
    )

    e = (
        df.withColumn("_aff_key", F.lower(F.trim(F.col("affiliate_name"))))
        .withColumn("_prod_key", F.lower(F.trim(F.col("product_id").cast("string"))))
        .withColumn("_acct_key", F.lower(F.trim(F.col("account_id").cast("string"))))
        .join(ia_sel, on="_aff_key", how="left")
        .join(pr_sel, on=["_prod_key", "_acct_key"], how="left")
    )

    is_internal = F.coalesce(F.col("_is_internal"), F.lit(0)) == 1
    # Cenario 5: marca is_house_traffic p/ afiliados internos (alem do que o silver ja marcou)
    ht = F.coalesce(F.col("is_house_traffic").cast("boolean"), F.lit(False)) | is_internal
    ts, tm = F.col("_traffic_source"), F.col("_traffic_manager")
    cat, locked = F.col("_cat_offer"), (F.col("_locked") == 1)
    o = F.col("offer_name")

    new_offer = (
        # Cenario 1: afiliado externo, offer_name NULL -> catalogo
        F.when((~ht) & o.isNull() & cat.isNotNull() & (cat != "") & locked, cat)
        # Cenario 2: house traffic, offer_name NULL -> catalogo formatado
        .when(
            ht & o.isNull() & cat.isNotNull() & (cat != "") & locked,
            build_house_offer_name("_cat_offer", "_traffic_source", "_traffic_manager"),
        )
        # Cenario 3: house traffic com 'Affiliate Marketing' -> catalogo formatado
        .when(
            ht & o.isNotNull() & o.contains("Affiliate Marketing") & cat.isNotNull() & (cat != "") & locked,
            build_house_offer_name("_cat_offer", "_traffic_source", "_traffic_manager"),
        )
        # Cenario 4: house traffic sem tag de gestor -> adiciona ao offer_name EXISTENTE
        .when(
            ht & o.isNotNull() & (~o.contains("Affiliate Marketing")) & (~o.contains("Gestor de Tráfego:")),
            add_gestor_to_existing(o, tm),
        )
        # senao mantem o offer_name atual
        .otherwise(o)
    )

    e = (
        e.withColumn("offer_name", new_offer)
        .withColumn("is_house_traffic", ht)
        .drop("_aff_key", "_prod_key", "_acct_key", "_is_internal", "_traffic_source", "_traffic_manager", "_cat_offer", "_locked")
    )
    print("[INFO] offer_name enriquecido — cenarios 1/2/3/4 + marcacao house traffic (5) aplicados")
    return e


# cancel_reason que recebem refund_fee diferenciado de US$ 25 (alerta de
# chargeback = e tratado como refund pela BuyGoods, nao e chargeback de verdade).
CHARGEBACK_ALERT_REASONS = ["ChargebackAlert", "ChargebackAlert RDR"]

# Campos de ESTADO do ciclo de vida: na reconciliacao webhook x API, vem da fonte
# com o evento MAIS AVANCADO (nao um coalesce cego). Os demais campos sao
# coalesce(API, webhook) = API prioridade, webhook preenche o que a API nao tem.
STATE_COLS = [
    "payment_status", "transaction_type",
    "total_refund_usd", "total_refund",
    "date_refunded", "datetime_refunded_platform",
    "refund_fee_usd", "refund_fee",
    "chargeback_fee_usd", "chargeback_fee",
]


def _status_rank(col):
    """Hierarquia 'only-advance' do ciclo de vida (maior = evento mais recente/completo)."""
    return (
        F.when(col == "chargeback", F.lit(3))
        .when(col == "refunded", F.lit(2))
        .when(col == "refunded_partial", F.lit(1))
        .otherwise(F.lit(0))  # approved / desconhecido
    )


def reconcile_webhook_api(api_df, wh_df):
    """
    Reconciliacao webhook x API (Defeito no2 — API e a FONTE DA VERDADE), SEM
    sobrescrever cegamente: priorizacao por 'evento mais recente e mais completo'
    = estado mais avancado do ciclo de vida (frase do Gabriel).

    Por transaction_id:
      - so webhook -> mantem webhook
      - so API     -> mantem API
      - nos dois   -> campos de ESTADO (STATE_COLS) vem da fonte com payment_status
                      mais avancado (empate -> API); demais campos = coalesce(API,
                      webhook) (API prioridade, webhook preenche os nulos);
                      cancel_reason = coalesce(API, webhook) (so a API tem -> destrava no3).
    data_source = 'api' quando a transacao existe na API (overlap ou so-API), senao 'webhook'.
    Mantem 1 linha por transaction_id (as silvers ja deduplicam por transaction_id).
    """
    a = api_df.withColumn("_in_api", F.lit(True)).alias("a")
    w = wh_df.withColumn("_in_wh", F.lit(True)).alias("w")
    j = a.join(w, on="transaction_id", how="full_outer")

    in_api = F.col("a._in_api").isNotNull()
    in_wh = F.col("w._in_wh").isNotNull()
    api_rank = _status_rank(F.col("a.payment_status"))
    wh_rank = _status_rank(F.col("w.payment_status"))
    # estado vem da API se: so API, ou (nos dois e API tao/mais avancado que webhook)
    take_api_state = in_api & (~in_wh | (api_rank >= wh_rank))

    out_cols = [F.col("transaction_id")]
    for c in UNIFIED_COLS:
        if c == "transaction_id":
            continue
        if c in STATE_COLS:
            out_cols.append(
                F.when(take_api_state, F.col(f"a.{c}")).otherwise(F.col(f"w.{c}")).alias(c)
            )
        else:
            out_cols.append(F.coalesce(F.col(f"a.{c}"), F.col(f"w.{c}")).alias(c))
    out_cols.append(F.when(in_api, F.lit("api")).otherwise(F.lit("webhook")).alias("data_source"))
    return j.select(*out_cols)


def apply_canonical_commission(df):
    """
    Recalcula commission_usd/commission (Opcao A) sobre os campos JA reconciliados.

    Regra (confirmada pelo time):
        total_price_usd = total_collected_usd - iva_usd
        refund_fee_usd  = 25 se cancel_reason IN (ChargebackAlert, ChargebackAlert RDR);
                          senao mantem o valor atual (1 em reembolso)
        commission_usd  = total_price_usd
                          - (taxes_usd se payment_status='approved'; senao 0)
                          - affiliate_amount_usd        (sempre; sem clawback)
                          - total_refund_usd
                          - refund_fee_usd
                          - chargeback_fee_usd          (do payload, mantido)
        commission(BRL) = commission_usd * exchange_rate

    Preserva NULL onde commission_usd ja era NULL. NAO aplica taxa proporcional (no4 fora).
    """
    # 1) refund_fee: 25 para alerta de chargeback; senao mantem (1 em reembolso, 0 fora).
    df = df.withColumn(
        "refund_fee_usd",
        F.when(F.col("cancel_reason").isin(CHARGEBACK_ALERT_REASONS), F.lit(25.0))
        .otherwise(F.coalesce(F.col("refund_fee_usd"), F.lit(0.0))),
    )

    # 2) commission canonico (base unica; taxa cheia so em aprovada; preserva NULL).
    total_price = F.coalesce(F.col("total_collected_usd"), F.lit(0.0)) - F.coalesce(F.col("iva_usd"), F.lit(0.0))
    taxes_term = F.when(
        F.col("payment_status") == "approved", F.coalesce(F.col("taxes_usd"), F.lit(0.0))
    ).otherwise(F.lit(0.0))
    commission_calc = (
        total_price
        - taxes_term
        - F.coalesce(F.col("affiliate_amount_usd"), F.lit(0.0))
        - F.coalesce(F.col("total_refund_usd"), F.lit(0.0))
        - F.coalesce(F.col("refund_fee_usd"), F.lit(0.0))
        - F.coalesce(F.col("chargeback_fee_usd"), F.lit(0.0))
    )
    df = df.withColumn(
        "commission_usd",
        F.when(F.col("commission_usd").isNotNull(), F.round(commission_calc, 2).cast("decimal(10,2)"))
        .otherwise(F.lit(None).cast("decimal(10,2)")),
    )
    df = df.withColumn(
        "commission",
        F.when(
            F.col("commission_usd").isNotNull(),
            F.round(F.col("commission_usd") * F.coalesce(F.col("exchange_rate"), F.lit(0.0)), 4).cast("decimal(12,4)"),
        ).otherwise(F.lit(None).cast("decimal(12,4)")),
    )
    df = df.withColumn("refund_fee_usd", F.round(F.col("refund_fee_usd"), 2).cast("decimal(10,2)"))
    return df


def read_silver_resilient(path, label, retries=8, wait=30):
    """Le a silver do S3 com retry. A silver do WEBHOOK grava com write.mode('overwrite'),
    que APAGA e recria o path -> se a leitura cair nessa janela, o Spark levanta
    'Path does not exist' / 'Unable to infer schema' por alguns segundos. Tratamos
    como TRANSIENTE e tentamos de novo antes de falhar (evita a corrida em run manual;
    no fluxo automatico o EventBridge ja dispara a unificada apos o SUCCEEDED do silver)."""
    transient = ("Path does not exist", "Unable to infer schema", "does not exist")
    for attempt in range(1, retries + 1):
        try:
            df = spark.read.option("ignoreMissingFiles", "true").parquet(path)
            df.take(1)  # forca a analise/leitura agora (o erro aparece aqui, nao adiante)
            print(f"[STEP 1] {label} OK (tentativa {attempt}/{retries}).")
            return df
        except Exception as e:
            msg = str(e)
            if attempt >= retries or not any(m in msg for m in transient):
                raise
            print(
                f"[STEP 1] {label}: tentativa {attempt}/{retries} caiu na janela de overwrite "
                f"({msg[:120]}); aguardando {wait}s e tentando de novo..."
            )
            time.sleep(wait)


print(f"[STEP 1] Lendo API silver de {API_LOCATION} ...")
api_raw = read_silver_resilient(API_LOCATION, "API silver")
# API ja possui utm_* e cancel_reason; alinhamos a ordem unificada.
api_df = align_to_unified(api_raw).withColumn("data_source", F.lit("api"))

print(f"[STEP 1] Lendo Webhook silver de {WEBHOOK_LOCATION} ...")
wh_raw = read_silver_resilient(WEBHOOK_LOCATION, "Webhook silver")
# Reconcilia subid* -> utm_* (mesmo dado, nome diferente).
for subid, utm in SUBID_TO_UTM.items():
    if subid in wh_raw.columns:
        wh_raw = wh_raw.withColumnRenamed(subid, utm)
wh_df = align_to_unified(wh_raw).withColumn("data_source", F.lit("webhook"))

print("[STEP 2] Reconciliando webhook x API (API = fonte da verdade; estado mais avancado)...")
unified = reconcile_webhook_api(api_df, wh_df)

# Normaliza affiliate_name: colapsa 2+ espacos em 1 e faz trim
# (ex.: "matheus  correa" -> "matheus correa"). Tambem melhora o match de
# house traffic com buygoods_internal_affiliates no enriquecimento abaixo.
unified = unified.withColumn(
    "affiliate_name", F.trim(F.regexp_replace(F.col("affiliate_name"), " +", " "))
)

print("[STEP 2.1] Enriquecendo offer_name (absorve a procedure fill_buygoods_offer_names)...")
unified = enrich_offer_names(unified)

print("[STEP 2.2] Recalculando commission canonico (refund_fee 1->25 + base canonica)...")
unified = apply_canonical_commission(unified)

unified = unified.withColumn("id", F.monotonically_increasing_id().cast("bigint"))
unified = unified.select(["id"] + UNIFIED_COLS + ["data_source"])

total_webhook = wh_df.count()
total_api = api_df.count()
total_unified = unified.count()
overlap = total_webhook + total_api - total_unified
print(
    f"[STEP 2] total_webhook={total_webhook} total_api={total_api} "
    f"overlap~={overlap} total_unified={total_unified}"
)
# Reconciliacao = UNIAO por transaction_id distinto: total_unified deve estar
# entre max(webhook,api) e webhook+api (sem o overlap).
if not (max(total_webhook, total_api) <= total_unified <= total_webhook + total_api):
    raise RuntimeError(
        "Contagem reconciliada fora dos limites esperados: total_unified deve estar "
        f"entre max(webhook,api) e webhook+api. wh={total_webhook} api={total_api} "
        f"unif={total_unified}"
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
    f"total_webhook={total_webhook} total_api={total_api} total_unified={total_unified}"
)
job.commit()
````

## Relacionados
[[00-Data-Lake]]
