---
tipo: job-glue
ambiente: prod
fluxo: 
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: 2026-06-11 15:19
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-affiliate-nutra-brl-prod

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
| Script | `s3://gex-datalake-bronze-prod/scripts/affiliate_nutra_build.py` |
| Criado | 2026-06-10 16:28:07.330000-03:00 |
| Modificado | 2026-06-10 16:28:07.330000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--CARTPANDA_TABLE` | cartpanda_physical |
| `--CCS_TABLE` | call_center_sales |
| `--CURRENCY` | BRL |
| `--DATE_FLOOR` | 2026-01-01 |
| `--DB_TABLE` | tb_gex_affiliate_nutra |
| `--GLUE_CONNECTION_NAME` | gex-mysql-connection-prod |
| `--GOLD_S3_PREFIX` | gex_affiliate_nutra |
| `--GOLD_TABLE` | tb_gex_gold_clickbank_buygoods |
| `--MIN_ROWS_THRESHOLD` | 100 |
| `--TARGET_DATABASE` | instituto_experience |
| `--target_bucket` | gex-datalake-gold-prod |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-11 15:19 | SUCCEEDED | 2m20s | — |
| 2026-06-11 14:15 | SUCCEEDED | 2m17s | — |
| 2026-06-11 12:15 | SUCCEEDED | 1m57s | — |
| 2026-06-11 10:14 | SUCCEEDED | 3m1s | — |
| 2026-06-11 08:11 | SUCCEEDED | 2m5s | — |
| 2026-06-11 06:16 | SUCCEEDED | 2m13s | — |
| 2026-06-11 04:17 | SUCCEEDED | 2m8s | — |
| 2026-06-11 02:11 | SUCCEEDED | 2m13s | — |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/affiliate_nutra_build.py` — baixado do S3 (read-only).

````python
"""
Glue Job: affiliate_nutra_build
===============================
Mart affiliate_nutra (BRL e USD) — UM job parametrizado por --CURRENCY.
Reproduz VERBATIM as procedures refresh_dashboard_affiliate_nutra (BRL) e
refresh_dashboard_affiliate_nutra_usd (USD), no padrao server-side MySQL
(CTAS em staging -> DQ gate -> swap atomico) + espelho parquet no S3 (Athena).

Fontes (MySQL): gold combinada (tb_gex_gold_clickbank_buygoods, no lugar do nome
legado dashboard_gold_clickbank_buygoods das procedures), cartpanda_physical e
call_center_sales. Destino: tb_gex_affiliate_nutra (BRL) / tb_gex_affiliate_nutra_usd (USD).

Sentinelas aplicadas no SQL (somente parametrizacao; logica intacta):
  __GOLD__       -> gold combinada FQTN
  __CARTPANDA__  -> cartpanda_physical FQTN
  __CCS__        -> call_center_sales FQTN
  __DATEFLOOR__  -> piso de data nos WHERE (a janela de imposto BETWEEN
                    '2026-01-01' AND '2026-03-31' permanece LITERAL, e regra de negocio)

Parametros (--CHAVE valor):
  --JOB_NAME, --GLUE_CONNECTION_NAME, --target_bucket   (req)
  --CURRENCY             (opt) BRL|USD  default: BRL
  --DB_TABLE             (opt) default: tb_gex_affiliate_nutra (BRL) — passar p/ USD
  --GOLD_TABLE           (opt) default: tb_gex_gold_clickbank_buygoods
  --CARTPANDA_TABLE      (opt) default: cartpanda_physical
  --CCS_TABLE            (opt) default: call_center_sales
  --TARGET_DATABASE      (opt) default: instituto_experience
  --DATE_FLOOR           (opt) default: 2026-01-01
  --MIN_ROWS_THRESHOLD   (opt) default: 100
  --GOLD_S3_PREFIX       (opt) default: gex_affiliate_nutra
"""

import re
import sys
import time

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext


def get_optional_arg(name, default):
    token = f"--{name}"
    if token in sys.argv:
        idx = sys.argv.index(token)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return default


# ===========================================================================
# SQL VERBATIM das procedures (corpo do SELECT do INSERT), com sentinelas.
# ===========================================================================
BRL_SELECT = r"""
SELECT
    ud.created_at_date,
    ud.clean_product_name,
    ud.platform,
    ud.affiliate_name,
    ud.affiliate_id,
    ud.payment_status,
    ud.funil_id,
    ud.coupon_code,
    nl.niche,
    ud.total_vendas,
    ud.total_price,
    ud.commission,
    ud.taxes,
    ud.total_refund,
    ud.product_cost,
    ud.affiliate_amount,
    ud.imposto,
    ud.`1_2_units_sales`,
    ud.`3_4_units_sales`,
    ud.`5_6_units_sales`,
    ud.faixa_potes,
    ud.ob_count, ud.ob_revenue,
    ud.up1_count, ud.up1_revenue,
    ud.up2_count, ud.up2_revenue,
    ud.up3_count, ud.up3_revenue,
    ud.down1_count, ud.down1_revenue,
    ud.down2_count, ud.down2_revenue,
    ud.down3_count, ud.down3_revenue,
    (ud.total_price - (
        ud.ob_revenue + ud.up1_revenue + ud.up2_revenue + ud.up3_revenue
            + ud.down1_revenue + ud.down2_revenue + ud.down3_revenue
        )) AS revenue_no_funnel
FROM (

         -- ===================== 1) CARTPANDA =====================
         SELECT
             cp.created_at_date,

             LOWER(REGEXP_REPLACE(
                     TRIM(CASE
                              WHEN cp.product_name LIKE '%-%'
                                  THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                              WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                  THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                              ELSE cp.product_name
                         END),
                     '[^a-zA-Z0-9]', ''
                   )) AS product_key,

             CONCAT(
                     UPPER(LEFT(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cp.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                      ELSE cp.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                      )), 1)),
                     SUBSTRING(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cp.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                      ELSE cp.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                     )), 2)
             ) AS clean_product_name,

             'cartpanda' AS platform,
             cp.affiliate_name,
             cp.affiliate_id,
             cp.payment_status,

             CASE
                 WHEN cp.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                     THEN TRIM(REGEXP_SUBSTR(cp.offer_name, 'Funil [^#]*#[0-9]+'))
                 ELSE NULL
                 END AS funil_id,

             NULLIF(cp.coupon_code, '') AS coupon_code,

             CASE
                 WHEN LOWER(cp.product_sku) LIKE '%1unit%'
                   OR LOWER(cp.product_sku) LIKE '%2unit%' THEN '1 a 2 Potes'
                 WHEN LOWER(cp.product_sku) LIKE '%3unit%'
                   OR LOWER(cp.product_sku) LIKE '%4unit%' THEN '3 a 4 Potes'
                 WHEN LOWER(cp.product_sku) LIKE '%5unit%'
                   OR LOWER(cp.product_sku) LIKE '%6unit%' THEN '5+ Potes'
                 ELSE 'Não Encontrado'
             END AS faixa_potes,

             COUNT(*) AS total_vendas,
             COALESCE(SUM(cp.total_price), 0) AS total_price,
             COALESCE(SUM(cp.commission), 0) AS commission,
             COALESCE(SUM(cp.taxes), 0) AS taxes,
             COALESCE(SUM(cp.total_refund), 0) AS total_refund,
             COALESCE(SUM(cp.affiliate_amount), 0) AS affiliate_amount,

             COALESCE(SUM(CASE
                              WHEN cp.payment_status IN ('approved', 'refunded_partial')
                                  THEN cp.product_cost
                              ELSE 0
                 END), 0) AS product_cost,

             SUM(CASE
                     WHEN cp.payment_status IN ('approved', 'refunded_partial')
                         THEN
                         CASE
                             WHEN cp.created_at_date BETWEEN '2026-01-01' AND '2026-03-31' THEN
                                 CASE
                                     WHEN LOWER(REGEXP_REPLACE(
                                             TRIM(CASE
                                                      WHEN cp.product_name LIKE '%-%'
                                                          THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                                      WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                                          THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                                      ELSE cp.product_name
                                                 END),
                                             '[^a-zA-Z0-9]', ''
                                                )) IN ('glycopezil', 'sugarcontrol')
                                         THEN cp.total_price * 0.017
                                     ELSE cp.total_price * 0
                                     END
                             ELSE cp.total_price * 0.01
                             END
                     ELSE 0
                 END) AS imposto,

             SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%1unit%'
                 OR LOWER(cp.product_sku) LIKE '%2unit%' THEN 1 ELSE 0 END) AS `1_2_units_sales`,
             SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%3unit%'
                 OR LOWER(cp.product_sku) LIKE '%4unit%' THEN 1 ELSE 0 END) AS `3_4_units_sales`,
             SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%5unit%'
                 OR LOWER(cp.product_sku) LIKE '%6unit%' THEN 1 ELSE 0 END) AS `5_6_units_sales`,

             COALESCE(SUM(cp.has_order_bump), 0) AS ob_count,
             COALESCE(SUM(cp.total_price_order_bump), 0) AS ob_revenue,
             COALESCE(SUM(cp.has_upsell), 0) AS up1_count,
             COALESCE(SUM(cp.total_price_upsell), 0) AS up1_revenue,
             COALESCE(SUM(cp.has_upsell2), 0) AS up2_count,
             COALESCE(SUM(cp.total_price_upsell2), 0) AS up2_revenue,
             COALESCE(SUM(cp.has_upsell3), 0) AS up3_count,
             COALESCE(SUM(cp.total_price_upsell3), 0) AS up3_revenue,
             COALESCE(SUM(cp.has_downsell), 0) AS down1_count,
             COALESCE(SUM(cp.total_price_downsell), 0) AS down1_revenue,
             COALESCE(SUM(cp.has_downsell2), 0) AS down2_count,
             COALESCE(SUM(cp.total_price_downsell2), 0) AS down2_revenue,
             COALESCE(SUM(cp.has_downsell3), 0) AS down3_count,
             COALESCE(SUM(cp.total_price_downsell3), 0) AS down3_revenue

         FROM __CARTPANDA__ cp FORCE INDEX (idx_cp_created_date)
         WHERE cp.created_at_date >= '__DATEFLOOR__'
           AND cp.payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
           AND cp.affiliate_name IS NOT NULL
           AND cp.affiliate_name <> ''
         GROUP BY
             cp.created_at_date,
             LOWER(REGEXP_REPLACE(
                     TRIM(CASE
                              WHEN cp.product_name LIKE '%-%'
                                  THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                              WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                  THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                              ELSE cp.product_name
                         END),
                     '[^a-zA-Z0-9]', ''
                   )),
             CONCAT(
                     UPPER(LEFT(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cp.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                      ELSE cp.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                      )), 1)),
                     SUBSTRING(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cp.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                      ELSE cp.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                     )), 2)
             ),
             cp.affiliate_name,
             cp.affiliate_id,
             cp.payment_status,
             CASE
                 WHEN cp.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                     THEN TRIM(REGEXP_SUBSTR(cp.offer_name, 'Funil [^#]*#[0-9]+'))
                 ELSE NULL
                 END,
             NULLIF(cp.coupon_code, ''),
             CASE
                 WHEN LOWER(cp.product_sku) LIKE '%1unit%'
                   OR LOWER(cp.product_sku) LIKE '%2unit%' THEN '1 a 2 Potes'
                 WHEN LOWER(cp.product_sku) LIKE '%3unit%'
                   OR LOWER(cp.product_sku) LIKE '%4unit%' THEN '3 a 4 Potes'
                 WHEN LOWER(cp.product_sku) LIKE '%5unit%'
                   OR LOWER(cp.product_sku) LIKE '%6unit%' THEN '5+ Potes'
                 ELSE 'Não Encontrado'
             END

         UNION ALL

         -- ===================== 2) GOLD CLICKBANK + BUYGOODS =====================
         SELECT
             cbg.created_at_date,

             LOWER(REGEXP_REPLACE(
                     TRIM(CASE
                              WHEN cbg.product_name LIKE '%-%'
                                  THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                              WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                  THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                              ELSE cbg.product_name
                         END),
                     '[^a-zA-Z0-9]', ''
                   )) AS product_key,

             CONCAT(
                     UPPER(LEFT(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cbg.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                      ELSE cbg.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                      )), 1)),
                     SUBSTRING(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cbg.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                      ELSE cbg.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                     )), 2)
             ) AS clean_product_name,

             cbg.platform AS platform,
             cbg.affiliate_name,
             NULL AS affiliate_id,
             cbg.payment_status,

             CASE
                 WHEN cbg.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                     THEN TRIM(REGEXP_SUBSTR(cbg.offer_name, 'Funil [^#]*#[0-9]+'))
                 ELSE NULL
                 END AS funil_id,

             NULL AS coupon_code,

             CASE
                 WHEN cbg.quantity_principal IN (1, 2) THEN '1 a 2 Potes'
                 WHEN cbg.quantity_principal IN (3, 4) THEN '3 a 4 Potes'
                 WHEN cbg.quantity_principal >= 5     THEN '5+ Potes'
                 ELSE 'Não Encontrado'
             END AS faixa_potes,

             COUNT(*) AS total_vendas,
             COALESCE(SUM(cbg.total_price), 0) AS total_price,
             COALESCE(SUM(cbg.commission), 0) AS commission,
             COALESCE(SUM(cbg.taxes), 0) AS taxes,
             COALESCE(SUM(cbg.total_refund), 0) AS total_refund,
             COALESCE(SUM(cbg.affiliate_amount), 0) AS affiliate_amount,

             COALESCE(SUM(CASE
                              WHEN cbg.payment_status IN ('approved', 'refunded_partial')
                                  THEN cbg.product_cost
                              ELSE 0
                 END), 0) AS product_cost,

             SUM(CASE
                     WHEN cbg.payment_status IN ('approved', 'refunded_partial')
                         THEN
                         CASE
                             WHEN cbg.created_at_date BETWEEN '2026-01-01' AND '2026-03-31' THEN
                                 CASE
                                     WHEN LOWER(REGEXP_REPLACE(
                                             TRIM(CASE
                                                      WHEN cbg.product_name LIKE '%-%'
                                                          THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                                      WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                                          THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                                      ELSE cbg.product_name
                                                 END),
                                             '[^a-zA-Z0-9]', ''
                                                )) IN ('glycopezil', 'sugarcontrol')
                                         THEN cbg.total_price * 0.017
                                     ELSE cbg.total_price * 0
                                     END
                             ELSE cbg.total_price * 0.01
                             END
                     ELSE 0
                 END) AS imposto,

             SUM(CASE WHEN cbg.quantity_principal IN (1, 2) THEN 1 ELSE 0 END) AS `1_2_units_sales`,
             SUM(CASE WHEN cbg.quantity_principal IN (3, 4) THEN 1 ELSE 0 END) AS `3_4_units_sales`,
             SUM(CASE WHEN cbg.quantity_principal >= 5     THEN 1 ELSE 0 END) AS `5_6_units_sales`,

             COALESCE(SUM(cbg.has_order_bump), 0) AS ob_count,
             COALESCE(SUM(cbg.total_price_order_bump), 0) AS ob_revenue,
             COALESCE(SUM(cbg.has_upsell), 0) AS up1_count,
             COALESCE(SUM(cbg.total_price_upsell), 0) AS up1_revenue,
             COALESCE(SUM(cbg.has_upsell2), 0) AS up2_count,
             COALESCE(SUM(cbg.total_price_upsell2), 0) AS up2_revenue,
             COALESCE(SUM(cbg.has_upsell3), 0) AS up3_count,
             COALESCE(SUM(cbg.total_price_upsell3), 0) AS up3_revenue,
             COALESCE(SUM(cbg.has_downsell), 0) AS down1_count,
             COALESCE(SUM(cbg.total_price_downsell), 0) AS down1_revenue,
             COALESCE(SUM(cbg.has_downsell2), 0) AS down2_count,
             COALESCE(SUM(cbg.total_price_downsell2), 0) AS down2_revenue,
             COALESCE(SUM(cbg.has_downsell3), 0) AS down3_count,
             COALESCE(SUM(cbg.total_price_downsell3), 0) AS down3_revenue

         FROM __GOLD__ cbg
         WHERE cbg.created_at_date >= '__DATEFLOOR__'
           AND cbg.payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
           AND cbg.affiliate_name IS NOT NULL
           AND cbg.affiliate_name <> ''
           AND (cbg.is_house_traffic = 0 OR cbg.is_house_traffic IS NULL)
         GROUP BY
             cbg.created_at_date,
             LOWER(REGEXP_REPLACE(
                     TRIM(CASE
                              WHEN cbg.product_name LIKE '%-%'
                                  THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                              WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                  THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                              ELSE cbg.product_name
                         END),
                     '[^a-zA-Z0-9]', ''
                   )),
             CONCAT(
                     UPPER(LEFT(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cbg.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                      ELSE cbg.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                      )), 1)),
                     SUBSTRING(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cbg.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                      ELSE cbg.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                     )), 2)
             ),
             cbg.platform,
             cbg.affiliate_name,
             cbg.payment_status,
             CASE
                 WHEN cbg.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                     THEN TRIM(REGEXP_SUBSTR(cbg.offer_name, 'Funil [^#]*#[0-9]+'))
                 ELSE NULL
                 END,
             CASE
                 WHEN cbg.quantity_principal IN (1, 2) THEN '1 a 2 Potes'
                 WHEN cbg.quantity_principal IN (3, 4) THEN '3 a 4 Potes'
                 WHEN cbg.quantity_principal >= 5     THEN '5+ Potes'
                 ELSE 'Não Encontrado'
             END

     ) ud

    LEFT JOIN (
        SELECT product_key, MAX(niche) AS niche
        FROM __CCS__
        WHERE nome_produto != 'Geral'
          AND nome_produto NOT LIKE '%Sem Nome%'
          AND nome_produto NOT LIKE '%Outros%'
        GROUP BY product_key
    ) nl ON ud.product_key = nl.product_key
"""

USD_SELECT = r"""
SELECT
    ud.created_at_date,
    ud.clean_product_name,
    ud.platform,
    ud.affiliate_name,
    ud.affiliate_id,
    ud.payment_status,
    ud.funil_id,
    ud.coupon_code,
    nl.niche,
    ud.total_vendas,
    ud.total_price,
    ud.commission,
    ud.taxes,
    ud.total_refund,
    ud.refund_total_amount,
    ud.refund_partial_amount,
    ud.chargeback_amount,
    ud.refund_total_sales,
    ud.refund_partial_sales,
    ud.chargeback_sales,
    ud.product_cost,
    ud.affiliate_amount,
    ud.imposto,
    ud.`1_2_units_sales`,
    ud.`3_4_units_sales`,
    ud.`5_6_units_sales`,
    ud.faixa_potes,
    ud.ob_count, ud.ob_revenue,
    ud.up1_count, ud.up1_revenue,
    ud.up2_count, ud.up2_revenue,
    ud.up3_count, ud.up3_revenue,
    ud.down1_count, ud.down1_revenue,
    ud.down2_count, ud.down2_revenue,
    ud.down3_count, ud.down3_revenue,
    (ud.total_price - (
        ud.ob_revenue + ud.up1_revenue + ud.up2_revenue + ud.up3_revenue
            + ud.down1_revenue + ud.down2_revenue + ud.down3_revenue
        )) AS revenue_no_funnel
FROM (

         -- ===================== 1) CARTPANDA (BRL / 5.5) =====================
         SELECT
             cp.created_at_date,

             LOWER(REGEXP_REPLACE(
                     TRIM(CASE
                              WHEN cp.product_name LIKE '%-%'
                                  THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                              WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                  THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                              ELSE cp.product_name
                         END),
                     '[^a-zA-Z0-9]', ''
                   )) AS product_key,

             CONCAT(
                     UPPER(LEFT(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cp.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                      ELSE cp.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                      )), 1)),
                     SUBSTRING(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cp.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                      ELSE cp.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                     )), 2)
             ) AS clean_product_name,

             'cartpanda' AS platform,
             cp.affiliate_name,
             cp.affiliate_id,
             cp.payment_status,

             CASE
                 WHEN cp.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                     THEN TRIM(REGEXP_SUBSTR(cp.offer_name, 'Funil [^#]*#[0-9]+'))
                 ELSE NULL
                 END AS funil_id,

             NULLIF(cp.coupon_code, '') AS coupon_code,

             CASE
                 WHEN LOWER(cp.product_sku) LIKE '%1unit%'
                   OR LOWER(cp.product_sku) LIKE '%2unit%' THEN '1 a 2 Potes'
                 WHEN LOWER(cp.product_sku) LIKE '%3unit%'
                   OR LOWER(cp.product_sku) LIKE '%4unit%' THEN '3 a 4 Potes'
                 WHEN LOWER(cp.product_sku) LIKE '%5unit%'
                   OR LOWER(cp.product_sku) LIKE '%6unit%' THEN '5+ Potes'
                 ELSE 'Não Encontrado'
             END AS faixa_potes,

             COUNT(*) AS total_vendas,
             ROUND(COALESCE(SUM(cp.total_price), 0) / 5.5, 2) AS total_price,
             ROUND(COALESCE(SUM(cp.commission), 0) / 5.5, 2) AS commission,
             ROUND(COALESCE(SUM(cp.taxes), 0) / 5.5, 2) AS taxes,
             ROUND(COALESCE(SUM(cp.total_refund), 0) / 5.5, 2) AS total_refund,

             ROUND(COALESCE(SUM(CASE
                                    WHEN cp.payment_status = 'refunded'
                                        THEN cp.total_refund
                                    ELSE 0
                 END), 0) / 5.5, 2) AS refund_total_amount,

             ROUND(COALESCE(SUM(CASE
                                    WHEN cp.payment_status = 'refunded_partial'
                                        THEN cp.total_refund
                                    ELSE 0
                 END), 0) / 5.5, 2) AS refund_partial_amount,

             ROUND(COALESCE(SUM(CASE
                                    WHEN cp.payment_status = 'chargeback'
                                        THEN cp.total_refund
                                    ELSE 0
                 END), 0) / 5.5, 2) AS chargeback_amount,

             SUM(CASE WHEN cp.payment_status = 'refunded' THEN 1 ELSE 0 END) AS refund_total_sales,
             SUM(CASE WHEN cp.payment_status = 'refunded_partial' THEN 1 ELSE 0 END) AS refund_partial_sales,
             SUM(CASE WHEN cp.payment_status = 'chargeback' THEN 1 ELSE 0 END) AS chargeback_sales,

             ROUND(COALESCE(SUM(cp.affiliate_amount), 0) / 5.5, 2) AS affiliate_amount,

             ROUND(COALESCE(SUM(CASE
                                    WHEN cp.payment_status IN ('approved', 'refunded_partial')
                                        THEN cp.product_cost
                                    ELSE 0
                 END), 0) / 5.5, 2) AS product_cost,

             ROUND(SUM(CASE
                           WHEN cp.payment_status IN ('approved', 'refunded_partial')
                               THEN
                               CASE
                                   WHEN cp.created_at_date BETWEEN '2026-01-01' AND '2026-03-31' THEN
                                       CASE
                                           WHEN LOWER(REGEXP_REPLACE(
                                                   TRIM(CASE
                                                            WHEN cp.product_name LIKE '%-%'
                                                                THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                                            WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                                                THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                                            ELSE cp.product_name
                                                       END),
                                                   '[^a-zA-Z0-9]', ''
                                                      )) IN ('glycopezil', 'sugarcontrol')
                                               THEN cp.total_price * 0.017
                                           ELSE cp.total_price * 0
                                           END
                                   ELSE cp.total_price * 0.01
                                   END
                           ELSE 0
                 END) / 5.5, 2) AS imposto,

             SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%1unit%'
                 OR LOWER(cp.product_sku) LIKE '%2unit%' THEN 1 ELSE 0 END) AS `1_2_units_sales`,
             SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%3unit%'
                 OR LOWER(cp.product_sku) LIKE '%4unit%' THEN 1 ELSE 0 END) AS `3_4_units_sales`,
             SUM(CASE WHEN LOWER(cp.product_sku) LIKE '%5unit%'
                 OR LOWER(cp.product_sku) LIKE '%6unit%' THEN 1 ELSE 0 END) AS `5_6_units_sales`,

             COALESCE(SUM(cp.has_order_bump), 0) AS ob_count,
             ROUND(COALESCE(SUM(cp.total_price_order_bump), 0) / 5.5, 2) AS ob_revenue,
             COALESCE(SUM(cp.has_upsell), 0) AS up1_count,
             ROUND(COALESCE(SUM(cp.total_price_upsell), 0) / 5.5, 2) AS up1_revenue,
             COALESCE(SUM(cp.has_upsell2), 0) AS up2_count,
             ROUND(COALESCE(SUM(cp.total_price_upsell2), 0) / 5.5, 2) AS up2_revenue,
             COALESCE(SUM(cp.has_upsell3), 0) AS up3_count,
             ROUND(COALESCE(SUM(cp.total_price_upsell3), 0) / 5.5, 2) AS up3_revenue,
             COALESCE(SUM(cp.has_downsell), 0) AS down1_count,
             ROUND(COALESCE(SUM(cp.total_price_downsell), 0) / 5.5, 2) AS down1_revenue,
             COALESCE(SUM(cp.has_downsell2), 0) AS down2_count,
             ROUND(COALESCE(SUM(cp.total_price_downsell2), 0) / 5.5, 2) AS down2_revenue,
             COALESCE(SUM(cp.has_downsell3), 0) AS down3_count,
             ROUND(COALESCE(SUM(cp.total_price_downsell3), 0) / 5.5, 2) AS down3_revenue

         FROM __CARTPANDA__ cp FORCE INDEX (idx_cp_created_date)
         WHERE cp.created_at_date >= '__DATEFLOOR__'
           AND cp.payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
           AND cp.affiliate_name IS NOT NULL
           AND cp.affiliate_name <> ''
         GROUP BY
             cp.created_at_date,
             LOWER(REGEXP_REPLACE(
                     TRIM(CASE
                              WHEN cp.product_name LIKE '%-%'
                                  THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                              WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                  THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                              ELSE cp.product_name
                         END),
                     '[^a-zA-Z0-9]', ''
                   )),
             CONCAT(
                     UPPER(LEFT(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cp.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                      ELSE cp.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                      )), 1)),
                     SUBSTRING(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cp.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cp.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cp.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cp.product_name, '^[^0-9]+'))
                                      ELSE cp.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                     )), 2)
             ),
             cp.affiliate_name,
             cp.affiliate_id,
             cp.payment_status,
             CASE
                 WHEN cp.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                     THEN TRIM(REGEXP_SUBSTR(cp.offer_name, 'Funil [^#]*#[0-9]+'))
                 ELSE NULL
                 END,
             NULLIF(cp.coupon_code, ''),
             CASE
                 WHEN LOWER(cp.product_sku) LIKE '%1unit%'
                   OR LOWER(cp.product_sku) LIKE '%2unit%' THEN '1 a 2 Potes'
                 WHEN LOWER(cp.product_sku) LIKE '%3unit%'
                   OR LOWER(cp.product_sku) LIKE '%4unit%' THEN '3 a 4 Potes'
                 WHEN LOWER(cp.product_sku) LIKE '%5unit%'
                   OR LOWER(cp.product_sku) LIKE '%6unit%' THEN '5+ Potes'
                 ELSE 'Não Encontrado'
             END

         UNION ALL

         -- ===================== 2) GOLD CLICKBANK + BUYGOODS (campos _usd nativos) =====================
         SELECT
             cbg.created_at_date,

             LOWER(REGEXP_REPLACE(
                     TRIM(CASE
                              WHEN cbg.product_name LIKE '%-%'
                                  THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                              WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                  THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                              ELSE cbg.product_name
                         END),
                     '[^a-zA-Z0-9]', ''
                   )) AS product_key,

             CONCAT(
                     UPPER(LEFT(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cbg.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                      ELSE cbg.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                      )), 1)),
                     SUBSTRING(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cbg.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                      ELSE cbg.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                     )), 2)
             ) AS clean_product_name,

             cbg.platform AS platform,
             cbg.affiliate_name,
             NULL AS affiliate_id,
             cbg.payment_status,

             CASE
                 WHEN cbg.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                     THEN TRIM(REGEXP_SUBSTR(cbg.offer_name, 'Funil [^#]*#[0-9]+'))
                 ELSE NULL
                 END AS funil_id,

             NULL AS coupon_code,

             CASE
                 WHEN cbg.quantity_principal IN (1, 2) THEN '1 a 2 Potes'
                 WHEN cbg.quantity_principal IN (3, 4) THEN '3 a 4 Potes'
                 WHEN cbg.quantity_principal >= 5     THEN '5+ Potes'
                 ELSE 'Não Encontrado'
             END AS faixa_potes,

             COUNT(*) AS total_vendas,
             COALESCE(SUM(cbg.total_price_usd), 0) AS total_price,
             COALESCE(SUM(cbg.commission_usd), 0) AS commission,
             COALESCE(SUM(cbg.taxes_usd), 0) AS taxes,
             COALESCE(SUM(cbg.total_refund_usd), 0) AS total_refund,

             COALESCE(SUM(CASE
                              WHEN cbg.payment_status = 'refunded'
                                  THEN cbg.total_refund_usd
                              ELSE 0
                 END), 0) AS refund_total_amount,

             COALESCE(SUM(CASE
                              WHEN cbg.payment_status = 'refunded_partial'
                                  THEN cbg.total_refund_usd
                              ELSE 0
                 END), 0) AS refund_partial_amount,

             COALESCE(SUM(CASE
                              WHEN cbg.payment_status = 'chargeback'
                                  THEN cbg.total_refund_usd
                              ELSE 0
                 END), 0) AS chargeback_amount,

             SUM(CASE WHEN cbg.payment_status = 'refunded' THEN 1 ELSE 0 END) AS refund_total_sales,
             SUM(CASE WHEN cbg.payment_status = 'refunded_partial' THEN 1 ELSE 0 END) AS refund_partial_sales,
             SUM(CASE WHEN cbg.payment_status = 'chargeback' THEN 1 ELSE 0 END) AS chargeback_sales,

             COALESCE(SUM(cbg.affiliate_amount_usd), 0) AS affiliate_amount,

             COALESCE(SUM(CASE
                              WHEN cbg.payment_status IN ('approved', 'refunded_partial')
                                  THEN cbg.product_cost_usd
                              ELSE 0
                 END), 0) AS product_cost,

             SUM(CASE
                     WHEN cbg.payment_status IN ('approved', 'refunded_partial')
                         THEN
                         CASE
                             WHEN cbg.created_at_date BETWEEN '2026-01-01' AND '2026-03-31' THEN
                                 CASE
                                     WHEN LOWER(REGEXP_REPLACE(
                                             TRIM(CASE
                                                      WHEN cbg.product_name LIKE '%-%'
                                                          THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                                      WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                                          THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                                      ELSE cbg.product_name
                                                 END),
                                             '[^a-zA-Z0-9]', ''
                                                )) IN ('glycopezil', 'sugarcontrol')
                                         THEN cbg.total_price_usd * 0.017
                                     ELSE cbg.total_price_usd * 0
                                     END
                                 ELSE cbg.total_price_usd * 0.01
                                 END
                         ELSE 0
                 END) AS imposto,

             SUM(CASE WHEN cbg.quantity_principal IN (1, 2) THEN 1 ELSE 0 END) AS `1_2_units_sales`,
             SUM(CASE WHEN cbg.quantity_principal IN (3, 4) THEN 1 ELSE 0 END) AS `3_4_units_sales`,
             SUM(CASE WHEN cbg.quantity_principal >= 5     THEN 1 ELSE 0 END) AS `5_6_units_sales`,

             COALESCE(SUM(cbg.has_order_bump), 0) AS ob_count,
             COALESCE(SUM(cbg.total_price_order_bump_usd), 0) AS ob_revenue,
             COALESCE(SUM(cbg.has_upsell), 0) AS up1_count,
             COALESCE(SUM(cbg.total_price_upsell_usd), 0) AS up1_revenue,
             COALESCE(SUM(cbg.has_upsell2), 0) AS up2_count,
             COALESCE(SUM(cbg.total_price_upsell2_usd), 0) AS up2_revenue,
             COALESCE(SUM(cbg.has_upsell3), 0) AS up3_count,
             COALESCE(SUM(cbg.total_price_upsell3_usd), 0) AS up3_revenue,
             COALESCE(SUM(cbg.has_downsell), 0) AS down1_count,
             COALESCE(SUM(cbg.total_price_downsell_usd), 0) AS down1_revenue,
             COALESCE(SUM(cbg.has_downsell2), 0) AS down2_count,
             COALESCE(SUM(cbg.total_price_downsell2_usd), 0) AS down2_revenue,
             COALESCE(SUM(cbg.has_downsell3), 0) AS down3_count,
             COALESCE(SUM(cbg.total_price_downsell3_usd), 0) AS down3_revenue

         FROM __GOLD__ cbg
         WHERE cbg.created_at_date >= '__DATEFLOOR__'
           AND cbg.payment_status IN ('approved', 'refunded', 'chargeback', 'refunded_partial')
           AND cbg.affiliate_name IS NOT NULL
           AND cbg.affiliate_name <> ''
           AND (cbg.is_house_traffic = 0 OR cbg.is_house_traffic IS NULL)
         GROUP BY
             cbg.created_at_date,
             LOWER(REGEXP_REPLACE(
                     TRIM(CASE
                              WHEN cbg.product_name LIKE '%-%'
                                  THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                              WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                  THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                              ELSE cbg.product_name
                         END),
                     '[^a-zA-Z0-9]', ''
                   )),
             CONCAT(
                     UPPER(LEFT(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cbg.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                      ELSE cbg.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                      )), 1)),
                     SUBSTRING(LOWER(REGEXP_REPLACE(
                             TRIM(CASE
                                      WHEN cbg.product_name LIKE '%-%'
                                          THEN TRIM(SUBSTRING_INDEX(cbg.product_name, '-', 1))
                                      WHEN REGEXP_LIKE(cbg.product_name, '[0-9]')
                                          THEN TRIM(REGEXP_SUBSTR(cbg.product_name, '^[^0-9]+'))
                                      ELSE cbg.product_name
                                 END),
                             '[^a-zA-Z0-9]', ''
                                     )), 2)
             ),
             cbg.platform,
             cbg.affiliate_name,
             cbg.payment_status,
             CASE
                 WHEN cbg.offer_name REGEXP 'Funil [^#]*#[0-9]+'
                     THEN TRIM(REGEXP_SUBSTR(cbg.offer_name, 'Funil [^#]*#[0-9]+'))
                 ELSE NULL
                 END,
             CASE
                 WHEN cbg.quantity_principal IN (1, 2) THEN '1 a 2 Potes'
                 WHEN cbg.quantity_principal IN (3, 4) THEN '3 a 4 Potes'
                 WHEN cbg.quantity_principal >= 5     THEN '5+ Potes'
                 ELSE 'Não Encontrado'
             END

     ) ud

         LEFT JOIN (
    SELECT product_key, MAX(niche) AS niche
    FROM __CCS__
    WHERE nome_produto != 'Geral'
      AND nome_produto NOT LIKE '%Sem Nome%'
      AND nome_produto NOT LIKE '%Outros%'
    GROUP BY product_key
) nl ON ud.product_key = nl.product_key
"""

# --- parametros ---
CURRENCY = get_optional_arg("CURRENCY", "BRL").strip().upper()
MYSQL_TABLE = get_optional_arg("DB_TABLE", "tb_gex_affiliate_nutra")
STAGING_TABLE = f"{MYSQL_TABLE}_stage"
BACKUP_TABLE = f"{MYSQL_TABLE}_old"
DEFAULT_DATABASE = get_optional_arg("TARGET_DATABASE", "instituto_experience")
GOLD_TABLE = get_optional_arg("GOLD_TABLE", "tb_gex_gold_clickbank_buygoods")
CARTPANDA_TABLE = get_optional_arg("CARTPANDA_TABLE", "cartpanda_physical")
CCS_TABLE = get_optional_arg("CCS_TABLE", "call_center_sales")
DATE_FLOOR = get_optional_arg("DATE_FLOOR", "2026-01-01")
GOLD_S3_PREFIX = get_optional_arg("GOLD_S3_PREFIX", "gex_affiliate_nutra").strip("/")


def quote_ident(name):
    return f"`{name.replace('`', '``')}`"


def parse_jdbc_url(url):
    with_db = re.match(r"jdbc:mysql://([^:/]+):(\d+)/([^?]+)", url or "")
    if with_db:
        return with_db.group(1), int(with_db.group(2)), with_db.group(3)
    without_db = re.match(r"jdbc:mysql://([^:/]+):(\d+)$", url or "")
    if without_db:
        return without_db.group(1), int(without_db.group(2)), DEFAULT_DATABASE
    raise ValueError(f"Cannot parse JDBC URL: {url!r}")


def build_jdbc_url(host, port, database):
    return f"jdbc:mysql://{host}:{port}/{database}?useSSL=true&serverTimezone=UTC&rewriteBatchedStatements=true"


class JdbcExecutor:
    def __init__(self, spark, jdbc_url, user, password):
        self._jvm = spark._jvm
        props = self._jvm.java.util.Properties()
        props.setProperty("user", user)
        props.setProperty("password", password)
        self._jvm.java.lang.Class.forName("com.mysql.cj.jdbc.Driver")
        self._conn = self._jvm.java.sql.DriverManager.getConnection(jdbc_url, props)

    def execute(self, sql):
        stmt = self._conn.createStatement()
        try:
            stmt.execute(sql)
        finally:
            stmt.close()

    def fetch_scalar_int(self, sql):
        stmt = self._conn.createStatement()
        try:
            rs = stmt.executeQuery(sql)
            try:
                return int(rs.getLong(1)) if rs.next() else 0
            finally:
                rs.close()
        finally:
            stmt.close()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


def render_select():
    body = USD_SELECT if CURRENCY == "USD" else BRL_SELECT
    fq = lambda t: f"{quote_ident(DEFAULT_DATABASE)}.{quote_ident(t)}"
    return (
        body.replace("__GOLD__", fq(GOLD_TABLE))
        .replace("__CARTPANDA__", fq(CARTPANDA_TABLE))
        .replace("__CCS__", fq(CCS_TABLE))
        .replace("__DATEFLOOR__", DATE_FLOOR)
    )


args = getResolvedOptions(sys.argv, ["JOB_NAME", "GLUE_CONNECTION_NAME", "target_bucket"])
start = time.time()
glue_context = GlueContext(SparkContext())
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

glue_connection_name = args["GLUE_CONNECTION_NAME"]
target_bucket = args["target_bucket"]
min_rows_threshold = int(get_optional_arg("MIN_ROWS_THRESHOLD", "100"))

if CURRENCY not in ("BRL", "USD"):
    raise RuntimeError(f"--CURRENCY invalido: {CURRENCY} (use BRL ou USD)")

print(f"[STEP 1] Credenciais via {glue_connection_name} (CURRENCY={CURRENCY}, destino={MYSQL_TABLE})...")
jdbc_conf = glue_context.extract_jdbc_conf(glue_connection_name)
raw_url = jdbc_conf.get("url") or jdbc_conf.get("fullUrl", "")
user = jdbc_conf.get("user") or jdbc_conf.get("username", "")
password = jdbc_conf.get("password", "")
host, port, database = parse_jdbc_url(raw_url)
jdbc_url = build_jdbc_url(host, port, database)
print(f"[STEP 1] OK host={host} db={database}")

stage_fqtn = quote_ident(STAGING_TABLE)
final_fqtn = quote_ident(MYSQL_TABLE)
backup_fqtn = quote_ident(BACKUP_TABLE)
select_sql = render_select()

# -----------------------------------------------------------------------------
# A uniao CARTPANDA + GOLD NAO pode ser materializada por um unico
# "CREATE TABLE <stage> AS <A UNION ALL B>": as colunas de texto das duas
# fontes tem COLLATIONS diferentes (cartpanda_physical externa vs gold combinada
# criada pelo Spark) e o MySQL recusa o UNION com "Illegal mix of collations".
# Reproduzimos a uniao EXATAMENTE como o SQL do Tadeu, mas materializando-a numa
# tabela temporaria via CREATE + INSERT (o INSERT...SELECT faz coercao implicita
# para a collation da tabela destino, sem operacao de conjunto -> sem clash) e o
# SELECT externo (projecao + LEFT JOIN de niche) le dessa temp. A logica de
# negocio fica intacta: apenas separamos o texto no 'UNION ALL'.
# -----------------------------------------------------------------------------
_head, _rest = select_sql.split("FROM (", 1)
_union_body, _after = _rest.split(") ud", 1)
_cartpanda_branch, _gold_branch = _union_body.split("UNION ALL", 1)
tmp_table = f"{MYSQL_TABLE}_u"
tmp_fqtn = quote_ident(tmp_table)
stage_select = f"{_head}FROM {tmp_fqtn} ud {_after}"

executor = JdbcExecutor(spark, jdbc_url, user, password)
try:
    print(f"[STEP 2] Materializa uniao CARTPANDA+GOLD em {tmp_table} (CREATE+INSERT)"
          f" e CREATE {STAGING_TABLE} AS <SELECT externo {CURRENCY}> (compute no RDS)...")
    executor.execute(f"DROP TABLE IF EXISTS {tmp_fqtn}")
    executor.execute(f"CREATE TABLE {tmp_fqtn} AS\n{_cartpanda_branch}")
    executor.execute(f"INSERT INTO {tmp_fqtn}\n{_gold_branch}")
    executor.execute(f"DROP TABLE IF EXISTS {stage_fqtn}")
    executor.execute(f"CREATE TABLE {stage_fqtn} AS\n{stage_select}")
    executor.execute(f"DROP TABLE IF EXISTS {tmp_fqtn}")

    stage_count = executor.fetch_scalar_int(f"SELECT COUNT(*) FROM {stage_fqtn}")
    print(f"[STEP 3] DQ gate: stage_count={stage_count}")
    if stage_count < min_rows_threshold:
        raise RuntimeError(f"Mart abaixo do threshold. stage_count={stage_count} threshold={min_rows_threshold}")
    nulos_chave = executor.fetch_scalar_int(
        f"SELECT COUNT(*) FROM {stage_fqtn} WHERE created_at_date IS NULL"
    )
    print(f"[STEP 3] OK (created_at_date nulos={nulos_chave})")

    print(f"[STEP 4] CREATE TABLE IF NOT EXISTS {MYSQL_TABLE} LIKE staging (auto-bootstrap)...")
    executor.execute(f"CREATE TABLE IF NOT EXISTS {final_fqtn} LIKE {stage_fqtn}")

    print("[STEP 5] Swap atomico (RENAME)...")
    executor.execute(f"DROP TABLE IF EXISTS {backup_fqtn}")
    executor.execute(f"RENAME TABLE {final_fqtn} TO {backup_fqtn}, {stage_fqtn} TO {final_fqtn}")
    executor.execute(f"DROP TABLE IF EXISTS {backup_fqtn}")
    print("[STEP 5] OK swap concluido")
finally:
    try:
        executor.execute(f"DROP TABLE IF EXISTS {tmp_fqtn}")
    except Exception:
        pass
    executor.close()

# Espelho S3 (parquet) p/ catalogo/Athena
output_path = f"s3://{target_bucket}/{GOLD_S3_PREFIX}/"
print(f"[STEP 6] Lendo {database}.{MYSQL_TABLE} e gravando parquet em {output_path} ...")
final_df = glue_context.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": f"{database}.{MYSQL_TABLE}",
        "connectionName": glue_connection_name,
    },
).toDF()
s3_count = final_df.count()
(
    final_df.repartition(1, "created_at_date")
    .write.mode("overwrite")
    .partitionBy("created_at_date")
    .parquet(output_path)
)

elapsed = int(time.time() - start)
print(f"[FINAL] OK mart {MYSQL_TABLE} ({CURRENCY}) em {elapsed}s | rows={stage_count} s3_rows={s3_count}")
job.commit()
````

## Relacionados
[[00-Data-Lake]]
