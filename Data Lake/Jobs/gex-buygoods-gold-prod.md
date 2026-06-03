---
tipo: job-glue
ambiente: prod
fluxo: 
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-03 14:05
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-buygoods-gold-prod

> Glue ETL · fluxo **—** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x4 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/buygoods_gold/jobs/gold_build_buygoods.py` |
| Criado | 2026-06-02 14:24:12.553000-03:00 |
| Modificado | 2026-06-03 13:59:34.448000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--DATE_FLOOR` | 2026-01-01 |
| `--DB_TABLE` | tb_gex_gold_buygoods |
| `--GLUE_CONNECTION_NAME` | gex-mysql-connection-prod |
| `--GOLD_S3_PREFIX` | gex_gold_buygoods |
| `--MIN_ROWS_THRESHOLD` | 100 |
| `--SOURCE_DATABASE` | instituto_experience |
| `--SOURCE_TABLE` | tb_gex_buygoods_unified |
| `--TARGET_DATABASE` | instituto_experience |
| `--target_bucket` | gex-datalake-gold-prod |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-03 14:05 | SUCCEEDED | 10m47s | — |
| 2026-06-03 13:48 | SUCCEEDED | 10m46s | — |
| 2026-06-03 13:28 | SUCCEEDED | 11m1s | — |
| 2026-06-03 11:48 | SUCCEEDED | 10m54s | — |
| 2026-06-03 09:48 | SUCCEEDED | 10m29s | — |
| 2026-06-03 07:47 | SUCCEEDED | 10m23s | — |
| 2026-06-03 05:48 | SUCCEEDED | 13m17s | — |
| 2026-06-03 03:50 | SUCCEEDED | 17m39s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/buygoods_gold/jobs/gold_build_buygoods.py` — baixado do S3 (read-only).

````python
"""
Glue Job: gold_build_buygoods
=============================
Constroi a camada GOLD BuyGoods (dashboard_gold_buygoods) a partir da fonte
unica instituto_experience.tb_gex_buygoods_unified, executando o SQL validado
pelo time (Tadeu) DIRETO no MySQL (server-side), com SWAP ATOMICO de tabela.
Em seguida ESPELHA a gold para o S3 (parquet) para catalogo/Athena.

A logica de negocio (sessionizacao por janela de 4h, classificacao funnel_type,
heranca de produto principal, 75 colunas, mapeamento de pais ISO-2) e o SQL de
referencia, mantido VERBATIM; aqui parametrizamos apenas:
  - a tabela fonte (SOURCE_DATABASE.SOURCE_TABLE)
  - o piso de data (DATE_FLOOR)
  - o nome da tabela destino/staging

=== CREDENCIAIS ===
  Lidas da Glue Connection via glue_context.extract_jdbc_conf() (sem Secrets Manager).

=== FLUXO ===
  [1] Credenciais da Glue Connection
  [2] DROP staging; CREATE TABLE <staging> AS <SQL>   (compute roda no RDS)
  [3] Valida COUNT(*) >= MIN_ROWS_THRESHOLD
  [4] CREATE TABLE IF NOT EXISTS <final> LIKE <staging>  (auto-bootstrap 1a run)
  [5] Swap atomico: RENAME <final>->_backup, <staging>-><final>; DROP _backup
  [6] Le <final> do MySQL e grava parquet em s3://<target_bucket>/<GOLD_S3_PREFIX>/

Parametros (--CHAVE valor):
  --JOB_NAME             (req, injetado pelo Glue)
  --GLUE_CONNECTION_NAME (req)   ex: gex-mysql-connection-prod
  --SOURCE_DATABASE      (opt)   default: instituto_experience
  --SOURCE_TABLE         (opt)   default: tb_gex_buygoods_unified
  --DB_TABLE             (opt)   default: dashboard_gold_buygoods   (tabela final/gold no MySQL)
  --TARGET_DATABASE      (opt)   default: instituto_experience
  --DATE_FLOOR           (opt)   default: 2026-01-01
  --MIN_ROWS_THRESHOLD   (opt)   default: 100
  --target_bucket        (req)   bucket gold (ex: gex-datalake-gold-prod)
  --GOLD_S3_PREFIX       (opt)   default: gex_gold_buygoods
"""

import re
import sys
import time

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark import SparkConf
from pyspark.context import SparkContext


def get_optional_arg(name: str, default: str) -> str:
    token = f"--{name}"
    if token in sys.argv:
        idx = sys.argv.index(token)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return default


# --- parametros ---
SOURCE_DATABASE = get_optional_arg("SOURCE_DATABASE", "instituto_experience")
SOURCE_TABLE = get_optional_arg("SOURCE_TABLE", "tb_gex_buygoods_unified")
DEFAULT_DATABASE = get_optional_arg("TARGET_DATABASE", "instituto_experience")
MYSQL_TABLE = get_optional_arg("DB_TABLE", "dashboard_gold_buygoods")
STAGING_TABLE = f"{MYSQL_TABLE}_old"
BACKUP_TABLE = f"{MYSQL_TABLE}_backup"
DATE_FLOOR = get_optional_arg("DATE_FLOOR", "2026-01-01")
GOLD_S3_PREFIX = get_optional_arg("GOLD_S3_PREFIX", "gex_gold_buygoods").strip("/")


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


# ===========================================================================
# SQL de referencia (Tadeu) — VERBATIM, com sentinelas para parametrizacao:
#   __SOURCE_FQTN__ -> SOURCE_DATABASE.SOURCE_TABLE
#   __DATE_FLOOR__  -> DATE_FLOOR
# Mantem-se apenas o corpo (WITH ... SELECT ...); o CREATE TABLE <staging> AS
# e montado em runtime.
# ===========================================================================
GOLD_SELECT_BODY = r"""
WITH base AS (
    SELECT
        cb.*,
        TIMESTAMP(CONCAT(cb.created_at_date, ' ', cb.created_at_hour)) AS created_at_ts,
        UPPER(COALESCE(cb.product_codename, '')) AS _codename_upper
    FROM __SOURCE_FQTN__ cb
    WHERE (cb.created_at_date >= '__DATE_FLOOR__' OR cb.created_at_date IS NULL)
),
ordenado AS (
    SELECT *,
        LAG(created_at_ts) OVER (
            PARTITION BY client_email, account_id
            ORDER BY created_at_ts, transaction_id
        ) AS prev_ts
    FROM base
),
flag_grupo AS (
    SELECT *,
        CASE
            WHEN prev_ts IS NULL THEN 1
            WHEN TIMESTAMPDIFF(MINUTE, prev_ts, created_at_ts) > 240 THEN 1
            ELSE 0
        END AS new_group
    FROM ordenado
),
grupo_id AS (
    SELECT *,
        SUM(new_group) OVER (
            PARTITION BY client_email, account_id
            ORDER BY created_at_ts, transaction_id
            ROWS UNBOUNDED PRECEDING
        ) AS purchase_group_id_final
    FROM flag_grupo
),
classificado AS (
    SELECT *,
        CASE
            -- 1) PRIMEIRA REGRA: offer_name (canonico, sera a fonte definitiva)
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%upsell 1%'   THEN 'upsell1'
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%upsell 2%'   THEN 'upsell2'
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%upsell 3%'   THEN 'upsell3'
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%downsell 1%' THEN 'downsell1'
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%downsell 2%' THEN 'downsell2'
            WHEN LOWER(sales_type) = 'venda de funil' AND LOWER(offer_name) LIKE '%downsell 3%' THEN 'downsell3'
            WHEN LOWER(sales_type) = 'order bump'                                                THEN 'order_bump'

            -- 2) SEGUNDA REGRA: fallback via product_codename
            WHEN _codename_upper REGEXP '(^|[_-])UP1([_-]|$)' OR _codename_upper REGEXP 'UP1[0-9]' THEN 'upsell1'
            WHEN _codename_upper REGEXP '(^|[_-])UP2([_-]|$)' OR _codename_upper REGEXP 'UP2[0-9]' THEN 'upsell2'
            WHEN _codename_upper REGEXP '(^|[_-])UP3([_-]|$)' OR _codename_upper REGEXP 'UP3[0-9]' THEN 'upsell3'
            WHEN _codename_upper REGEXP '(^|[_-])DW1([_-]|$)' OR _codename_upper REGEXP 'DW1[0-9]' THEN 'downsell1'
            WHEN _codename_upper REGEXP '(^|[_-])DW2([_-]|$)' OR _codename_upper REGEXP 'DW2[0-9]' THEN 'downsell2'
            WHEN _codename_upper REGEXP '(^|[_-])DW3([_-]|$)' OR _codename_upper REGEXP 'DW3[0-9]' THEN 'downsell3'
            WHEN _codename_upper REGEXP '(^|[_-])PP([_-]|$)'  OR _codename_upper REGEXP 'PP[0-9]'  THEN 'main'

            -- 3) TERCEIRA REGRA: fallback final pelo sales_type
            WHEN TRIM(LOWER(sales_type)) LIKE 'produto principal%'                                  THEN 'main'
            WHEN LOWER(sales_type) = 'venda de funil' AND (offer_name IS NULL OR TRIM(offer_name) = '') THEN 'funil_sem_offer'
            WHEN LOWER(sales_type) = 'venda de funil'                                                THEN 'funil_sem_offer'
            ELSE 'other'
        END AS funnel_type
    FROM grupo_id
),
main_por_grupo AS (
    SELECT
        client_email,
        account_id,
        purchase_group_id_final,
        MAX(CASE WHEN funnel_type = 'main' THEN product_name END) AS main_product_name,
        MAX(CASE WHEN funnel_type = 'main' THEN offer_name   END) AS main_offer_name,
        MAX(CASE WHEN funnel_type = 'main' THEN product_sku  END) AS main_product_sku,
        MIN(created_at_ts)                                        AS grupo_ts
    FROM classificado
    GROUP BY client_email, account_id, purchase_group_id_final
)
SELECT
    MIN(c.transaction_id)                                                       AS transaction_id,                  -- 1
    CASE
        WHEN COUNT(DISTINCT c.payment_status) = 1
            THEN MAX(c.payment_status)
        WHEN MAX(CASE WHEN c.payment_status = 'chargeback' THEN 1 ELSE 0 END) = 1
            THEN 'chargeback'
        ELSE 'refunded_partial'
    END                                                                         AS payment_status,                  -- 2
    MAX(c.client_name)                                                          AS client_name,                     -- 3
    c.client_email                                                              AS client_email,                    -- 4
    MAX(c.client_phone)                                                         AS client_phone,                    -- 5
    MAX(c.client_zip)                                                           AS client_zip,                      -- 6
    CASE MAX(c.client_country)
        WHEN 'AD' THEN 'Andorra'              WHEN 'AE' THEN 'United Arab Emirates'
        WHEN 'AF' THEN 'Afghanistan'          WHEN 'AG' THEN 'Antigua and Barbuda'
        WHEN 'AL' THEN 'Albania'              WHEN 'AM' THEN 'Armenia'
        WHEN 'AO' THEN 'Angola'               WHEN 'AR' THEN 'Argentina'
        WHEN 'AT' THEN 'Austria'              WHEN 'AU' THEN 'Australia'
        WHEN 'AZ' THEN 'Azerbaijan'           WHEN 'BA' THEN 'Bosnia and Herzegovina'
        WHEN 'BB' THEN 'Barbados'             WHEN 'BD' THEN 'Bangladesh'
        WHEN 'BE' THEN 'Belgium'              WHEN 'BF' THEN 'Burkina Faso'
        WHEN 'BG' THEN 'Bulgaria'             WHEN 'BH' THEN 'Bahrain'
        WHEN 'BI' THEN 'Burundi'              WHEN 'BJ' THEN 'Benin'
        WHEN 'BN' THEN 'Brunei'               WHEN 'BO' THEN 'Bolivia'
        WHEN 'BR' THEN 'Brazil'               WHEN 'BS' THEN 'Bahamas'
        WHEN 'BT' THEN 'Bhutan'               WHEN 'BW' THEN 'Botswana'
        WHEN 'BY' THEN 'Belarus'              WHEN 'BZ' THEN 'Belize'
        WHEN 'CA' THEN 'Canada'               WHEN 'CD' THEN 'Democratic Republic of the Congo'
        WHEN 'CF' THEN 'Central African Republic' WHEN 'CG' THEN 'Republic of the Congo'
        WHEN 'CH' THEN 'Switzerland'          WHEN 'CI' THEN 'Ivory Coast'
        WHEN 'CL' THEN 'Chile'                WHEN 'CM' THEN 'Cameroon'
        WHEN 'CN' THEN 'China'                WHEN 'CO' THEN 'Colombia'
        WHEN 'CR' THEN 'Costa Rica'           WHEN 'CU' THEN 'Cuba'
        WHEN 'CV' THEN 'Cape Verde'           WHEN 'CY' THEN 'Cyprus'
        WHEN 'CZ' THEN 'Czech Republic'       WHEN 'DE' THEN 'Germany'
        WHEN 'DJ' THEN 'Djibouti'             WHEN 'DK' THEN 'Denmark'
        WHEN 'DM' THEN 'Dominica'             WHEN 'DO' THEN 'Dominican Republic'
        WHEN 'DZ' THEN 'Algeria'              WHEN 'EC' THEN 'Ecuador'
        WHEN 'EE' THEN 'Estonia'              WHEN 'EG' THEN 'Egypt'
        WHEN 'ER' THEN 'Eritrea'              WHEN 'ES' THEN 'Spain'
        WHEN 'ET' THEN 'Ethiopia'             WHEN 'FI' THEN 'Finland'
        WHEN 'FJ' THEN 'Fiji'                 WHEN 'FR' THEN 'France'
        WHEN 'GA' THEN 'Gabon'                WHEN 'GB' THEN 'United Kingdom'
        WHEN 'GD' THEN 'Grenada'              WHEN 'GE' THEN 'Georgia'
        WHEN 'GH' THEN 'Ghana'                WHEN 'GM' THEN 'Gambia'
        WHEN 'GN' THEN 'Guinea'               WHEN 'GQ' THEN 'Equatorial Guinea'
        WHEN 'GR' THEN 'Greece'               WHEN 'GT' THEN 'Guatemala'
        WHEN 'GW' THEN 'Guinea-Bissau'        WHEN 'GY' THEN 'Guyana'
        WHEN 'HN' THEN 'Honduras'             WHEN 'HR' THEN 'Croatia'
        WHEN 'HT' THEN 'Haiti'                WHEN 'HU' THEN 'Hungary'
        WHEN 'ID' THEN 'Indonesia'            WHEN 'IE' THEN 'Ireland'
        WHEN 'IL' THEN 'Israel'               WHEN 'IN' THEN 'India'
        WHEN 'IQ' THEN 'Iraq'                 WHEN 'IR' THEN 'Iran'
        WHEN 'IS' THEN 'Iceland'              WHEN 'IT' THEN 'Italy'
        WHEN 'JM' THEN 'Jamaica'              WHEN 'JO' THEN 'Jordan'
        WHEN 'JP' THEN 'Japan'                WHEN 'KE' THEN 'Kenya'
        WHEN 'KG' THEN 'Kyrgyzstan'           WHEN 'KH' THEN 'Cambodia'
        WHEN 'KI' THEN 'Kiribati'             WHEN 'KM' THEN 'Comoros'
        WHEN 'KN' THEN 'Saint Kitts and Nevis' WHEN 'KP' THEN 'North Korea'
        WHEN 'KR' THEN 'South Korea'          WHEN 'KW' THEN 'Kuwait'
        WHEN 'KZ' THEN 'Kazakhstan'           WHEN 'LA' THEN 'Laos'
        WHEN 'LB' THEN 'Lebanon'              WHEN 'LC' THEN 'Saint Lucia'
        WHEN 'LI' THEN 'Liechtenstein'        WHEN 'LK' THEN 'Sri Lanka'
        WHEN 'LR' THEN 'Liberia'              WHEN 'LS' THEN 'Lesotho'
        WHEN 'LT' THEN 'Lithuania'            WHEN 'LU' THEN 'Luxembourg'
        WHEN 'LV' THEN 'Latvia'               WHEN 'LY' THEN 'Libya'
        WHEN 'MA' THEN 'Morocco'              WHEN 'MC' THEN 'Monaco'
        WHEN 'MD' THEN 'Moldova'              WHEN 'ME' THEN 'Montenegro'
        WHEN 'MG' THEN 'Madagascar'           WHEN 'MH' THEN 'Marshall Islands'
        WHEN 'MK' THEN 'North Macedonia'      WHEN 'ML' THEN 'Mali'
        WHEN 'MM' THEN 'Myanmar'              WHEN 'MN' THEN 'Mongolia'
        WHEN 'MR' THEN 'Mauritania'           WHEN 'MT' THEN 'Malta'
        WHEN 'MU' THEN 'Mauritius'            WHEN 'MV' THEN 'Maldives'
        WHEN 'MW' THEN 'Malawi'               WHEN 'MX' THEN 'Mexico'
        WHEN 'MY' THEN 'Malaysia'             WHEN 'MZ' THEN 'Mozambique'
        WHEN 'NA' THEN 'Namibia'              WHEN 'NE' THEN 'Niger'
        WHEN 'NG' THEN 'Nigeria'              WHEN 'NI' THEN 'Nicaragua'
        WHEN 'NL' THEN 'Netherlands'          WHEN 'NO' THEN 'Norway'
        WHEN 'NP' THEN 'Nepal'                WHEN 'NR' THEN 'Nauru'
        WHEN 'NZ' THEN 'New Zealand'          WHEN 'OM' THEN 'Oman'
        WHEN 'PA' THEN 'Panama'               WHEN 'PE' THEN 'Peru'
        WHEN 'PG' THEN 'Papua New Guinea'     WHEN 'PH' THEN 'Philippines'
        WHEN 'PK' THEN 'Pakistan'             WHEN 'PL' THEN 'Poland'
        WHEN 'PT' THEN 'Portugal'             WHEN 'PW' THEN 'Palau'
        WHEN 'PY' THEN 'Paraguay'             WHEN 'QA' THEN 'Qatar'
        WHEN 'RO' THEN 'Romania'              WHEN 'RS' THEN 'Serbia'
        WHEN 'RU' THEN 'Russia'               WHEN 'RW' THEN 'Rwanda'
        WHEN 'SA' THEN 'Saudi Arabia'         WHEN 'SB' THEN 'Solomon Islands'
        WHEN 'SC' THEN 'Seychelles'           WHEN 'SD' THEN 'Sudan'
        WHEN 'SE' THEN 'Sweden'               WHEN 'SG' THEN 'Singapore'
        WHEN 'SI' THEN 'Slovenia'             WHEN 'SK' THEN 'Slovakia'
        WHEN 'SL' THEN 'Sierra Leone'         WHEN 'SM' THEN 'San Marino'
        WHEN 'SN' THEN 'Senegal'              WHEN 'SO' THEN 'Somalia'
        WHEN 'SR' THEN 'Suriname'             WHEN 'SS' THEN 'South Sudan'
        WHEN 'ST' THEN 'Sao Tome and Principe' WHEN 'SV' THEN 'El Salvador'
        WHEN 'SY' THEN 'Syria'                WHEN 'SZ' THEN 'Eswatini'
        WHEN 'TD' THEN 'Chad'                 WHEN 'TG' THEN 'Togo'
        WHEN 'TH' THEN 'Thailand'             WHEN 'TJ' THEN 'Tajikistan'
        WHEN 'TL' THEN 'Timor-Leste'          WHEN 'TM' THEN 'Turkmenistan'
        WHEN 'TN' THEN 'Tunisia'              WHEN 'TO' THEN 'Tonga'
        WHEN 'TR' THEN 'Turkey'               WHEN 'TT' THEN 'Trinidad and Tobago'
        WHEN 'TV' THEN 'Tuvalu'               WHEN 'TZ' THEN 'Tanzania'
        WHEN 'UA' THEN 'Ukraine'              WHEN 'UG' THEN 'Uganda'
        WHEN 'US' THEN 'United States'        WHEN 'UY' THEN 'Uruguay'
        WHEN 'UZ' THEN 'Uzbekistan'           WHEN 'VA' THEN 'Vatican City'
        WHEN 'VC' THEN 'Saint Vincent and the Grenadines'
        WHEN 'VE' THEN 'Venezuela'            WHEN 'VN' THEN 'Vietnam'
        WHEN 'VU' THEN 'Vanuatu'              WHEN 'WS' THEN 'Samoa'
        WHEN 'YE' THEN 'Yemen'                WHEN 'ZA' THEN 'South Africa'
        WHEN 'ZM' THEN 'Zambia'               WHEN 'ZW' THEN 'Zimbabwe'
        ELSE MAX(c.client_country)
    END                                                                         AS client_country,                  -- 7
    MAX(c.client_state)                                                         AS client_state,                    -- 8
    MAX(c.client_city)                                                          AS client_city,                     -- 9
    MAX(c.client_street)                                                        AS client_street,                   -- 10
    COALESCE(
        MAX(CASE WHEN c.funnel_type = 'main' THEN c.product_name END),
        (
            SELECT mp2.main_product_name
            FROM main_por_grupo mp2
            WHERE mp2.client_email = c.client_email
              AND mp2.account_id = c.account_id
              AND mp2.main_product_name IS NOT NULL
              AND mp2.grupo_ts <= MIN(c.created_at_ts)
            ORDER BY mp2.grupo_ts DESC
            LIMIT 1
        )
    )                                                                           AS product_name,                    -- 11
    COALESCE(
        MAX(CASE WHEN c.funnel_type = 'main' THEN c.offer_name END),
        (
            SELECT mp2.main_offer_name
            FROM main_por_grupo mp2
            WHERE mp2.client_email = c.client_email
              AND mp2.account_id = c.account_id
              AND mp2.main_offer_name IS NOT NULL
              AND mp2.grupo_ts <= MIN(c.created_at_ts)
            ORDER BY mp2.grupo_ts DESC
            LIMIT 1
        )
    )                                                                           AS offer_name,                      -- 12
    COALESCE(
        MAX(CASE WHEN c.funnel_type = 'main' THEN c.product_sku END),
        (
            SELECT mp2.main_product_sku
            FROM main_por_grupo mp2
            WHERE mp2.client_email = c.client_email
              AND mp2.account_id = c.account_id
              AND mp2.main_product_sku IS NOT NULL
              AND mp2.grupo_ts <= MIN(c.created_at_ts)
            ORDER BY mp2.grupo_ts DESC
            LIMIT 1
        )
    )                                                                           AS product_sku,                     -- 13
    ROUND(SUM(c.product_cost), 4)                                               AS product_cost,                    -- 14
    ROUND(SUM(c.product_cost_usd), 2)                                           AS product_cost_usd,                -- 15
    SUM(c.quantity)                                                             AS quantity,                        -- 16
    MAX(CASE WHEN c.funnel_type = 'main' THEN c.quantity END)                   AS quantity_principal,              -- 17
    ROUND(SUM(c.total_price), 4)                                                AS total_price,                     -- 18
    ROUND(SUM(c.total_price_usd), 2)                                            AS total_price_usd,                 -- 19
    ROUND(SUM(c.taxes), 4)                                                      AS taxes,                           -- 20
    ROUND(SUM(c.taxes_usd), 2)                                                  AS taxes_usd,                       -- 21
    ROUND(SUM(c.total_refund), 4)                                               AS total_refund,                    -- 22
    ROUND(SUM(c.total_refund_usd), 2)                                           AS total_refund_usd,                -- 23
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN COALESCE(c.commission, 0) + COALESCE(c.affiliate_amount, 0)
             ELSE c.commission END), 4)                                         AS commission,                      -- 24
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN COALESCE(c.commission_usd, 0) + COALESCE(c.affiliate_amount_usd, 0)
             ELSE c.commission_usd END), 2)                                     AS commission_usd,                  -- 25
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN 0
             ELSE c.affiliate_amount END), 4)                                   AS affiliate_amount,                -- 26
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN 0
             ELSE c.affiliate_amount_usd END), 2)                               AS affiliate_amount_usd,            -- 27
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN COALESCE(c.affiliate_amount, 0)
             ELSE 0 END), 4)                                                    AS revenue_afiliado,                -- 28
    ROUND(SUM(CASE WHEN c.is_house_traffic = 1
             THEN COALESCE(c.affiliate_amount_usd, 0)
             ELSE 0 END), 2)                                                    AS revenue_afiliado_usd,            -- 29
    SUM(CASE WHEN c.funnel_type = 'upsell1'    THEN 1 ELSE 0 END)               AS has_upsell,                      -- 30
    SUM(CASE WHEN c.funnel_type = 'upsell2'    THEN 1 ELSE 0 END)               AS has_upsell2,                     -- 31
    SUM(CASE WHEN c.funnel_type = 'upsell3'    THEN 1 ELSE 0 END)               AS has_upsell3,                     -- 32
    SUM(CASE WHEN c.funnel_type = 'downsell1'  THEN 1 ELSE 0 END)               AS has_downsell,                    -- 33
    SUM(CASE WHEN c.funnel_type = 'downsell2'  THEN 1 ELSE 0 END)               AS has_downsell2,                   -- 34
    SUM(CASE WHEN c.funnel_type = 'downsell3'  THEN 1 ELSE 0 END)               AS has_downsell3,                   -- 35
    SUM(CASE WHEN c.funnel_type = 'order_bump' THEN 1 ELSE 0 END)               AS has_order_bump,                  -- 36
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell1'    THEN c.total_price     ELSE 0 END), 2) AS total_price_upsell,           -- 37
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell1'    THEN c.total_price_usd ELSE 0 END), 2) AS total_price_upsell_usd,       -- 38
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell2'    THEN c.total_price     ELSE 0 END), 2) AS total_price_upsell2,          -- 39
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell2'    THEN c.total_price_usd ELSE 0 END), 2) AS total_price_upsell2_usd,      -- 40
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell3'    THEN c.total_price     ELSE 0 END), 2) AS total_price_upsell3,          -- 41
    ROUND(SUM(CASE WHEN c.funnel_type = 'upsell3'    THEN c.total_price_usd ELSE 0 END), 2) AS total_price_upsell3_usd,      -- 42
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell1'  THEN c.total_price     ELSE 0 END), 2) AS total_price_downsell,         -- 43
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell1'  THEN c.total_price_usd ELSE 0 END), 2) AS total_price_downsell_usd,     -- 44
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell2'  THEN c.total_price     ELSE 0 END), 2) AS total_price_downsell2,        -- 45
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell2'  THEN c.total_price_usd ELSE 0 END), 2) AS total_price_downsell2_usd,    -- 46
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell3'  THEN c.total_price     ELSE 0 END), 2) AS total_price_downsell3,        -- 47
    ROUND(SUM(CASE WHEN c.funnel_type = 'downsell3'  THEN c.total_price_usd ELSE 0 END), 2) AS total_price_downsell3_usd,    -- 48
    ROUND(SUM(CASE WHEN c.funnel_type = 'order_bump' THEN c.total_price     ELSE 0 END), 2) AS total_price_order_bump,       -- 49
    ROUND(SUM(CASE WHEN c.funnel_type = 'order_bump' THEN c.total_price_usd ELSE 0 END), 2) AS total_price_order_bump_usd,   -- 50

    -- Colunas NAO existentes no BuyGoods - preenchidas com NULL
    CAST(NULL AS CHAR)                                                          AS coupon_code,                     -- 51

    DATE(MIN(c.created_at_ts))                                                  AS created_at_date,                 -- 52
    TIME_FORMAT(TIME(MIN(c.created_at_ts)), '%H:%i:%s')                         AS created_at_hour,                 -- 53
    MAX(c.date_refunded)                                                        AS date_refunded,                   -- 54

    -- UTMs agora vem direto da silver tb_gex_buygoods_physical_new
    MAX(c.utm_source)                                                           AS utm_source,                      -- 55
    MAX(c.utm_medium)                                                           AS utm_medium,                      -- 56
    MAX(c.utm_content)                                                          AS utm_content,                     -- 57
    MAX(c.utm_term)                                                             AS utm_term,                        -- 58
    MAX(c.utm_campaign)                                                         AS utm_campaign,                    -- 59
    CAST(NULL AS CHAR)                                                          AS src,                             -- 60

    MAX(c.platform)                                                             AS platform,                        -- 61
    MAX(c.affiliate_name)                                                       AS affiliate_name,                  -- 62

    -- vendor_name nao existe na BuyGoods (vem vazio no silver)
    CAST(NULL AS CHAR)                                                          AS vendor_name,                     -- 63
    CAST(MAX(CASE WHEN c.is_house_traffic = 1 THEN 1 ELSE 0 END) AS SIGNED)     AS is_house_traffic,                -- 64

    -- ============================================================
    -- NOVAS COLUNAS EXCLUSIVAS DO BUYGOODS (a partir da 65)
    -- ============================================================
    CONCAT(c.client_email, '_', c.account_id, '_', c.purchase_group_id_final)   AS purchase_group_id,               -- 65
    c.account_id                                                                AS account_id,                      -- 66
    MIN(c.datetime_platform)                                                    AS datetime_platform,               -- 67
    ROUND(SUM(c.total_collected_usd), 2)                                        AS total_collected_usd,             -- 68
    ROUND(SUM(c.iva), 4)                                                        AS iva,                             -- 69
    ROUND(SUM(c.iva_usd), 2)                                                    AS iva_usd,                         -- 70
    ROUND(SUM(c.refund_fee), 4)                                                 AS refund_fee,                      -- 71
    ROUND(SUM(c.refund_fee_usd), 2)                                             AS refund_fee_usd,                  -- 72
    ROUND(SUM(c.chargeback_fee), 4)                                             AS chargeback_fee,                  -- 73
    ROUND(SUM(c.chargeback_fee_usd), 2)                                         AS chargeback_fee_usd,              -- 74
    MAX(c.affiliate_id)                                                         AS affiliate_id                     -- 75

FROM classificado c
GROUP BY c.client_email, c.account_id, c.purchase_group_id_final
ORDER BY created_at_date DESC, created_at_hour DESC
"""


def build_gold_sql(staging_fqtn: str, source_fqtn: str, date_floor: str) -> str:
    body = GOLD_SELECT_BODY.replace("__SOURCE_FQTN__", source_fqtn).replace(
        "__DATE_FLOOR__", date_floor
    )
    return f"CREATE TABLE {staging_fqtn} AS\n{body}"


args = getResolvedOptions(sys.argv, ["JOB_NAME", "GLUE_CONNECTION_NAME", "target_bucket"])

start = time.time()

_conf = SparkConf()
_conf.set("spark.sql.session.timeZone", "America/Sao_Paulo")
sc = SparkContext(conf=_conf)
glue_context = GlueContext(sc)
spark = glue_context.spark_session

job = Job(glue_context)
job.init(args["JOB_NAME"], args)

glue_connection_name = args["GLUE_CONNECTION_NAME"]
target_bucket = args["target_bucket"]
min_rows_threshold = int(get_optional_arg("MIN_ROWS_THRESHOLD", "100"))

print(f"[STEP 1] Extraindo credenciais da Glue Connection ({glue_connection_name})...")
jdbc_conf = glue_context.extract_jdbc_conf(glue_connection_name)
raw_url = jdbc_conf.get("url") or jdbc_conf.get("fullUrl", "")
user = jdbc_conf.get("user") or jdbc_conf.get("username", "")
password = jdbc_conf.get("password", "")
host, port, database = parse_jdbc_url(raw_url)
jdbc_url = build_jdbc_url(host, port, database)
print(f"[STEP 1] OK host={host} port={port} db={database}")

source_fqtn = f"{quote_ident(SOURCE_DATABASE)}.{quote_ident(SOURCE_TABLE)}"
staging_fqtn = quote_ident(STAGING_TABLE)
final_fqtn = quote_ident(MYSQL_TABLE)
backup_fqtn = quote_ident(BACKUP_TABLE)

executor = JdbcExecutor(spark, jdbc_url, user, password)

try:
    print(f"[STEP 2] Construindo staging {STAGING_TABLE} no MySQL (CREATE TABLE AS <SQL>)...")
    executor.execute(f"DROP TABLE IF EXISTS {staging_fqtn}")
    executor.execute(build_gold_sql(staging_fqtn, source_fqtn, DATE_FLOOR))
    print("[STEP 2] OK staging construido")

    print("[STEP 3] Validando contagem do staging...")
    staging_count = executor.fetch_scalar_int(f"SELECT COUNT(*) FROM {staging_fqtn}")
    if staging_count < min_rows_threshold:
        raise RuntimeError(
            f"Gold abaixo do threshold. staging_count={staging_count} threshold={min_rows_threshold}"
        )
    print(f"[STEP 3] OK staging_count={staging_count}")

    print(f"[STEP 4] CREATE TABLE IF NOT EXISTS {MYSQL_TABLE} LIKE staging (auto-bootstrap)...")
    executor.execute(f"CREATE TABLE IF NOT EXISTS {final_fqtn} LIKE {staging_fqtn}")

    print("[STEP 5] Swap atomico (RENAME TABLE)...")
    executor.execute(f"DROP TABLE IF EXISTS {backup_fqtn}")
    executor.execute(
        f"RENAME TABLE {final_fqtn} TO {backup_fqtn}, {staging_fqtn} TO {final_fqtn}"
    )
    executor.execute(f"DROP TABLE IF EXISTS {backup_fqtn}")
    print("[STEP 5] OK swap concluido")

finally:
    executor.close()

# ---------------------------------------------------------------------------
# [6] Espelha a gold para o S3 (parquet) p/ catalogo/Athena
# ---------------------------------------------------------------------------
output_path = f"s3://{target_bucket}/{GOLD_S3_PREFIX}/"
print(f"[STEP 6] Lendo {database}.{MYSQL_TABLE} do MySQL e gravando parquet em {output_path} ...")
gold_dyf = glue_context.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": f"{database}.{MYSQL_TABLE}",
        "connectionName": glue_connection_name,
    },
)
gold_df = gold_dyf.toDF()
s3_count = gold_df.count()
(
    gold_df.repartition(1, "created_at_date")
    .write.mode("overwrite")
    .partitionBy("created_at_date")
    .parquet(output_path)
)
print(f"[STEP 6] OK {s3_count} linhas gravadas no S3")

elapsed = int(time.time() - start)
print(f"[FINAL] OK gold concluida em {elapsed}s | gold_rows={staging_count} s3_rows={s3_count}")
job.commit()
````

## Relacionados
[[00-Data-Lake]]
