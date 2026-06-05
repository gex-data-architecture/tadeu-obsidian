---
tipo: procedure
definer: "tadeu_lopes@%"
determinismo: "NO"
acesso_sql: "CONTAINS SQL"
security: "DEFINER"
criada_em: "2026-05-05 11:20:01"
alterada_em: "2026-05-05 11:20:01"
execucoes: 179
tags: [rotina, procedure]
---

# refresh_dashboard_reembolso_coortes

## Dependências

- **Lê:** [[clickbank_physical_new_aws]]
- **Escreve:** [[dashboard_reembolso_coortes_stage]]
- **Cria:** —
- **Trunca:** [[dashboard_reembolso_coortes_stage]]
- **Dropa:** —
- **Chama:** —

## Chamada por
[[sp_master_run_all]]

## Execuções (performance_schema)

> Acumulado **desde o último restart** do MySQL (não é histórico absoluto — zera no restart).

| Métrica | Valor |
|---|---|
| Execuções | 179 |
| Tempo médio | 5.0 s |
| Tempo máx | 8.8 s |
| Tempo total | 14m49s |
| Erros | 2 |
| Warnings | 0 |
| Linhas afetadas (total) | 8,700 |

## Corpo SQL

```sql
BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        TRUNCATE TABLE instituto_experience.dashboard_reembolso_coortes_stage;
        RESIGNAL;
    END;

    -- 1. Limpa a stage
    TRUNCATE TABLE instituto_experience.dashboard_reembolso_coortes_stage;

    -- 2. Insere na stage
    INSERT INTO instituto_experience.dashboard_reembolso_coortes_stage
    WITH coortes AS (
        SELECT
            YEARWEEK(created_at_date, 1)                                        AS coorte_semana,
            MIN(created_at_date) OVER (
                PARTITION BY YEARWEEK(created_at_date, 1))                      AS coorte_inicio,
            total_price_usd,
            total_refund_usd,
            payment_status,
            date_refunded,
            DATEDIFF(date_refunded, created_at_date)                            AS dias_ate_reembolso
        FROM instituto_experience.clickbank_physical_new_aws
        WHERE created_at_date >= '2026-02-01'
    ),
    agregado AS (
        SELECT
            coorte_semana,
            coorte_inicio,
            DATE_ADD(MIN(coorte_inicio), INTERVAL 6 DAY)                        AS coorte_fim,
            DATEDIFF(CURDATE(), DATE_ADD(MIN(coorte_inicio), INTERVAL 6 DAY))   AS dias_desde_fim_coorte,
            SUM(total_price_usd)                                                AS faturamento_usd,

            -- Refund
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial')
                     THEN total_refund_usd ELSE 0 END)                          AS refund_total_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 1
                     THEN total_refund_usd ELSE 0 END)                          AS refund_d1_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 3
                     THEN total_refund_usd ELSE 0 END)                          AS refund_d3_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 7
                     THEN total_refund_usd ELSE 0 END)                          AS refund_d7_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 14
                     THEN total_refund_usd ELSE 0 END)                          AS refund_d14_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 30
                     THEN total_refund_usd ELSE 0 END)                          AS refund_d30_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 60
                     THEN total_refund_usd ELSE 0 END)                          AS refund_d60_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 90
                     THEN total_refund_usd ELSE 0 END)                          AS refund_d90_usd,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 1
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS refund_taxa_d1_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 3
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS refund_taxa_d3_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 7
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS refund_taxa_d7_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 14
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS refund_taxa_d14_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 30
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS refund_taxa_d30_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 60
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS refund_taxa_d60_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial') AND dias_ate_reembolso <= 90
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS refund_taxa_d90_pct,

            -- Chargeback
            SUM(CASE WHEN payment_status = 'chargeback'
                     THEN total_refund_usd ELSE 0 END)                          AS cb_total_usd,
            SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 1
                     THEN total_refund_usd ELSE 0 END)                          AS cb_d1_usd,
            SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 3
                     THEN total_refund_usd ELSE 0 END)                          AS cb_d3_usd,
            SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 7
                     THEN total_refund_usd ELSE 0 END)                          AS cb_d7_usd,
            SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 14
                     THEN total_refund_usd ELSE 0 END)                          AS cb_d14_usd,
            SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 30
                     THEN total_refund_usd ELSE 0 END)                          AS cb_d30_usd,
            SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 60
                     THEN total_refund_usd ELSE 0 END)                          AS cb_d60_usd,
            SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 90
                     THEN total_refund_usd ELSE 0 END)                          AS cb_d90_usd,
            ROUND(SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 1
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS cb_taxa_d1_pct,
            ROUND(SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 3
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS cb_taxa_d3_pct,
            ROUND(SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 7
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS cb_taxa_d7_pct,
            ROUND(SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 14
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS cb_taxa_d14_pct,
            ROUND(SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 30
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS cb_taxa_d30_pct,
            ROUND(SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 60
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS cb_taxa_d60_pct,
            ROUND(SUM(CASE WHEN payment_status = 'chargeback' AND dias_ate_reembolso <= 90
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS cb_taxa_d90_pct,

            -- Refund + Chargeback
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback')
                     THEN total_refund_usd ELSE 0 END)                          AS dev_total_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 1
                     THEN total_refund_usd ELSE 0 END)                          AS dev_d1_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 3
                     THEN total_refund_usd ELSE 0 END)                          AS dev_d3_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 7
                     THEN total_refund_usd ELSE 0 END)                          AS dev_d7_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 14
                     THEN total_refund_usd ELSE 0 END)                          AS dev_d14_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 30
                     THEN total_refund_usd ELSE 0 END)                          AS dev_d30_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 60
                     THEN total_refund_usd ELSE 0 END)                          AS dev_d60_usd,
            SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 90
                     THEN total_refund_usd ELSE 0 END)                          AS dev_d90_usd,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 1
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS dev_taxa_d1_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 3
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS dev_taxa_d3_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 7
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS dev_taxa_d7_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 14
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS dev_taxa_d14_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 30
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS dev_taxa_d30_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 60
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS dev_taxa_d60_pct,
            ROUND(SUM(CASE WHEN payment_status IN ('refunded','refunded_partial','chargeback') AND dias_ate_reembolso <= 90
                           THEN total_refund_usd ELSE 0 END)
                  / NULLIF(SUM(total_price_usd), 0), 4)                         AS dev_taxa_d90_pct

        FROM coortes
        GROUP BY coorte_semana, coorte_inicio
    ),
    historico AS (
        SELECT
            AVG(CASE WHEN dias_desde_fim_coorte >= 1  THEN refund_taxa_d1_pct  END) AS refund_media_d1,
            AVG(CASE WHEN dias_desde_fim_coorte >= 3  THEN refund_taxa_d3_pct  END) AS refund_media_d3,
            AVG(CASE WHEN dias_desde_fim_coorte >= 7  THEN refund_taxa_d7_pct  END) AS refund_media_d7,
            AVG(CASE WHEN dias_desde_fim_coorte >= 14 THEN refund_taxa_d14_pct END) AS refund_media_d14,
            AVG(CASE WHEN dias_desde_fim_coorte >= 30 THEN refund_taxa_d30_pct END) AS refund_media_d30,
            AVG(CASE WHEN dias_desde_fim_coorte >= 60 THEN refund_taxa_d60_pct END) AS refund_media_d60,
            AVG(CASE WHEN dias_desde_fim_coorte >= 90 THEN refund_taxa_d90_pct END) AS refund_media_d90,
            AVG(CASE WHEN dias_desde_fim_coorte >= 1  THEN cb_taxa_d1_pct  END)     AS cb_media_d1,
            AVG(CASE WHEN dias_desde_fim_coorte >= 3  THEN cb_taxa_d3_pct  END)     AS cb_media_d3,
            AVG(CASE WHEN dias_desde_fim_coorte >= 7  THEN cb_taxa_d7_pct  END)     AS cb_media_d7,
            AVG(CASE WHEN dias_desde_fim_coorte >= 14 THEN cb_taxa_d14_pct END)     AS cb_media_d14,
            AVG(CASE WHEN dias_desde_fim_coorte >= 30 THEN cb_taxa_d30_pct END)     AS cb_media_d30,
            AVG(CASE WHEN dias_desde_fim_coorte >= 60 THEN cb_taxa_d60_pct END)     AS cb_media_d60,
            AVG(CASE WHEN dias_desde_fim_coorte >= 90 THEN cb_taxa_d90_pct END)     AS cb_media_d90,
            AVG(CASE WHEN dias_desde_fim_coorte >= 1  THEN dev_taxa_d1_pct  END)    AS dev_media_d1,
            AVG(CASE WHEN dias_desde_fim_coorte >= 3  THEN dev_taxa_d3_pct  END)    AS dev_media_d3,
            AVG(CASE WHEN dias_desde_fim_coorte >= 7  THEN dev_taxa_d7_pct  END)    AS dev_media_d7,
            AVG(CASE WHEN dias_desde_fim_coorte >= 14 THEN dev_taxa_d14_pct END)    AS dev_media_d14,
            AVG(CASE WHEN dias_desde_fim_coorte >= 30 THEN dev_taxa_d30_pct END)    AS dev_media_d30,
            AVG(CASE WHEN dias_desde_fim_coorte >= 60 THEN dev_taxa_d60_pct END)    AS dev_media_d60,
            AVG(CASE WHEN dias_desde_fim_coorte >= 90 THEN dev_taxa_d90_pct END)    AS dev_media_d90
        FROM agregado
    ),
    final AS (
        -- Refund
        SELECT
            a.coorte_semana,
            a.coorte_inicio,
            a.coorte_fim,
            a.faturamento_usd,
            a.dias_desde_fim_coorte,
            'Refund'                    AS tipo_devolucao,
            a.refund_total_usd          AS total_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 1  THEN a.refund_d1_usd  ELSE NULL END AS d1_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 3  THEN a.refund_d3_usd  ELSE NULL END AS d3_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 7  THEN a.refund_d7_usd  ELSE NULL END AS d7_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 14 THEN a.refund_d14_usd ELSE NULL END AS d14_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 30 THEN a.refund_d30_usd ELSE NULL END AS d30_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 60 THEN a.refund_d60_usd ELSE NULL END AS d60_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN a.refund_d90_usd ELSE NULL END AS d90_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 1  THEN a.refund_taxa_d1_pct  ELSE NULL END AS taxa_d1_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 3  THEN a.refund_taxa_d3_pct  ELSE NULL END AS taxa_d3_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 7  THEN a.refund_taxa_d7_pct  ELSE NULL END AS taxa_d7_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 14 THEN a.refund_taxa_d14_pct ELSE NULL END AS taxa_d14_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 30 THEN a.refund_taxa_d30_pct ELSE NULL END AS taxa_d30_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 60 THEN a.refund_taxa_d60_pct ELSE NULL END AS taxa_d60_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN a.refund_taxa_d90_pct ELSE NULL END AS taxa_d90_pct,
            CASE WHEN a.dias_desde_fim_coorte < 90 THEN
                ROUND(CASE
                    WHEN a.dias_desde_fim_coorte >= 60 THEN (a.refund_taxa_d60_pct / NULLIF(h.refund_media_d60, 0)) * h.refund_media_d90
                    WHEN a.dias_desde_fim_coorte >= 30 THEN (a.refund_taxa_d30_pct / NULLIF(h.refund_media_d30, 0)) * h.refund_media_d90
                    WHEN a.dias_desde_fim_coorte >= 14 THEN (a.refund_taxa_d14_pct / NULLIF(h.refund_media_d14, 0)) * h.refund_media_d90
                    WHEN a.dias_desde_fim_coorte >= 7  THEN (a.refund_taxa_d7_pct  / NULLIF(h.refund_media_d7,  0)) * h.refund_media_d90
                    WHEN a.dias_desde_fim_coorte >= 3  THEN (a.refund_taxa_d3_pct  / NULLIF(h.refund_media_d3,  0)) * h.refund_media_d90
                    WHEN a.dias_desde_fim_coorte >= 1  THEN (a.refund_taxa_d1_pct  / NULLIF(h.refund_media_d1,  0)) * h.refund_media_d90
                    ELSE NULL
                END, 4)
            ELSE NULL END                                                           AS taxa_d90_projetada_pct,
            h.refund_media_d1  AS media_d1,
            h.refund_media_d3  AS media_d3,
            h.refund_media_d7  AS media_d7,
            h.refund_media_d14 AS media_d14,
            h.refund_media_d30 AS media_d30,
            h.refund_media_d60 AS media_d60,
            h.refund_media_d90 AS media_d90,
            CASE WHEN a.dias_desde_fim_coorte >= 1  THEN 'fechado' ELSE 'aberto' END AS status_d1,
            CASE WHEN a.dias_desde_fim_coorte >= 3  THEN 'fechado' ELSE 'aberto' END AS status_d3,
            CASE WHEN a.dias_desde_fim_coorte >= 7  THEN 'fechado' ELSE 'aberto' END AS status_d7,
            CASE WHEN a.dias_desde_fim_coorte >= 14 THEN 'fechado' ELSE 'aberto' END AS status_d14,
            CASE WHEN a.dias_desde_fim_coorte >= 30 THEN 'fechado' ELSE 'aberto' END AS status_d30,
            CASE WHEN a.dias_desde_fim_coorte >= 60 THEN 'fechado' ELSE 'aberto' END AS status_d60,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN 'fechado' ELSE 'aberto' END AS status_d90,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN 'fechada' ELSE 'aberta' END AS status_coorte
        FROM agregado a CROSS JOIN historico h

        UNION ALL

        -- Chargeback
        SELECT
            a.coorte_semana,
            a.coorte_inicio,
            a.coorte_fim,
            a.faturamento_usd,
            a.dias_desde_fim_coorte,
            'Chargeback'                AS tipo_devolucao,
            a.cb_total_usd              AS total_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 1  THEN a.cb_d1_usd  ELSE NULL END AS d1_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 3  THEN a.cb_d3_usd  ELSE NULL END AS d3_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 7  THEN a.cb_d7_usd  ELSE NULL END AS d7_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 14 THEN a.cb_d14_usd ELSE NULL END AS d14_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 30 THEN a.cb_d30_usd ELSE NULL END AS d30_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 60 THEN a.cb_d60_usd ELSE NULL END AS d60_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN a.cb_d90_usd ELSE NULL END AS d90_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 1  THEN a.cb_taxa_d1_pct  ELSE NULL END AS taxa_d1_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 3  THEN a.cb_taxa_d3_pct  ELSE NULL END AS taxa_d3_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 7  THEN a.cb_taxa_d7_pct  ELSE NULL END AS taxa_d7_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 14 THEN a.cb_taxa_d14_pct ELSE NULL END AS taxa_d14_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 30 THEN a.cb_taxa_d30_pct ELSE NULL END AS taxa_d30_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 60 THEN a.cb_taxa_d60_pct ELSE NULL END AS taxa_d60_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN a.cb_taxa_d90_pct ELSE NULL END AS taxa_d90_pct,
            CASE WHEN a.dias_desde_fim_coorte < 90 THEN
                ROUND(CASE
                    WHEN a.dias_desde_fim_coorte >= 60 THEN (a.cb_taxa_d60_pct / NULLIF(h.cb_media_d60, 0)) * h.cb_media_d90
                    WHEN a.dias_desde_fim_coorte >= 30 THEN (a.cb_taxa_d30_pct / NULLIF(h.cb_media_d30, 0)) * h.cb_media_d90
                    WHEN a.dias_desde_fim_coorte >= 14 THEN (a.cb_taxa_d14_pct / NULLIF(h.cb_media_d14, 0)) * h.cb_media_d90
                    WHEN a.dias_desde_fim_coorte >= 7  THEN (a.cb_taxa_d7_pct  / NULLIF(h.cb_media_d7,  0)) * h.cb_media_d90
                    WHEN a.dias_desde_fim_coorte >= 3  THEN (a.cb_taxa_d3_pct  / NULLIF(h.cb_media_d3,  0)) * h.cb_media_d90
                    WHEN a.dias_desde_fim_coorte >= 1  THEN (a.cb_taxa_d1_pct  / NULLIF(h.cb_media_d1,  0)) * h.cb_media_d90
                    ELSE NULL
                END, 4)
            ELSE NULL END                                                           AS taxa_d90_projetada_pct,
            h.cb_media_d1  AS media_d1,
            h.cb_media_d3  AS media_d3,
            h.cb_media_d7  AS media_d7,
            h.cb_media_d14 AS media_d14,
            h.cb_media_d30 AS media_d30,
            h.cb_media_d60 AS media_d60,
            h.cb_media_d90 AS media_d90,
            CASE WHEN a.dias_desde_fim_coorte >= 1  THEN 'fechado' ELSE 'aberto' END AS status_d1,
            CASE WHEN a.dias_desde_fim_coorte >= 3  THEN 'fechado' ELSE 'aberto' END AS status_d3,
            CASE WHEN a.dias_desde_fim_coorte >= 7  THEN 'fechado' ELSE 'aberto' END AS status_d7,
            CASE WHEN a.dias_desde_fim_coorte >= 14 THEN 'fechado' ELSE 'aberto' END AS status_d14,
            CASE WHEN a.dias_desde_fim_coorte >= 30 THEN 'fechado' ELSE 'aberto' END AS status_d30,
            CASE WHEN a.dias_desde_fim_coorte >= 60 THEN 'fechado' ELSE 'aberto' END AS status_d60,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN 'fechado' ELSE 'aberto' END AS status_d90,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN 'fechada' ELSE 'aberta' END AS status_coorte
        FROM agregado a CROSS JOIN historico h

        UNION ALL

        -- Refund + Chargeback
        SELECT
            a.coorte_semana,
            a.coorte_inicio,
            a.coorte_fim,
            a.faturamento_usd,
            a.dias_desde_fim_coorte,
            'Refund + Chargeback'       AS tipo_devolucao,
            a.dev_total_usd             AS total_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 1  THEN a.dev_d1_usd  ELSE NULL END AS d1_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 3  THEN a.dev_d3_usd  ELSE NULL END AS d3_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 7  THEN a.dev_d7_usd  ELSE NULL END AS d7_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 14 THEN a.dev_d14_usd ELSE NULL END AS d14_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 30 THEN a.dev_d30_usd ELSE NULL END AS d30_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 60 THEN a.dev_d60_usd ELSE NULL END AS d60_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN a.dev_d90_usd ELSE NULL END AS d90_usd,
            CASE WHEN a.dias_desde_fim_coorte >= 1  THEN a.dev_taxa_d1_pct  ELSE NULL END AS taxa_d1_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 3  THEN a.dev_taxa_d3_pct  ELSE NULL END AS taxa_d3_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 7  THEN a.dev_taxa_d7_pct  ELSE NULL END AS taxa_d7_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 14 THEN a.dev_taxa_d14_pct ELSE NULL END AS taxa_d14_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 30 THEN a.dev_taxa_d30_pct ELSE NULL END AS taxa_d30_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 60 THEN a.dev_taxa_d60_pct ELSE NULL END AS taxa_d60_pct,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN a.dev_taxa_d90_pct ELSE NULL END AS taxa_d90_pct,
            CASE WHEN a.dias_desde_fim_coorte < 90 THEN
                ROUND(CASE
                    WHEN a.dias_desde_fim_coorte >= 60 THEN (a.dev_taxa_d60_pct / NULLIF(h.dev_media_d60, 0)) * h.dev_media_d90
                    WHEN a.dias_desde_fim_coorte >= 30 THEN (a.dev_taxa_d30_pct / NULLIF(h.dev_media_d30, 0)) * h.dev_media_d90
                    WHEN a.dias_desde_fim_coorte >= 14 THEN (a.dev_taxa_d14_pct / NULLIF(h.dev_media_d14, 0)) * h.dev_media_d90
                    WHEN a.dias_desde_fim_coorte >= 7  THEN (a.dev_taxa_d7_pct  / NULLIF(h.dev_media_d7,  0)) * h.dev_media_d90
                    WHEN a.dias_desde_fim_coorte >= 3  THEN (a.dev_taxa_d3_pct  / NULLIF(h.dev_media_d3,  0)) * h.dev_media_d90
                    WHEN a.dias_desde_fim_coorte >= 1  THEN (a.dev_taxa_d1_pct  / NULLIF(h.dev_media_d1,  0)) * h.dev_media_d90
                    ELSE NULL
                END, 4)
            ELSE NULL END                                                           AS taxa_d90_projetada_pct,
            h.dev_media_d1  AS media_d1,
            h.dev_media_d3  AS media_d3,
            h.dev_media_d7  AS media_d7,
            h.dev_media_d14 AS media_d14,
            h.dev_media_d30 AS media_d30,
            h.dev_media_d60 AS media_d60,
            h.dev_media_d90 AS media_d90,
            CASE WHEN a.dias_desde_fim_coorte >= 1  THEN 'fechado' ELSE 'aberto' END AS status_d1,
            CASE WHEN a.dias_desde_fim_coorte >= 3  THEN 'fechado' ELSE 'aberto' END AS status_d3,
            CASE WHEN a.dias_desde_fim_coorte >= 7  THEN 'fechado' ELSE 'aberto' END AS status_d7,
            CASE WHEN a.dias_desde_fim_coorte >= 14 THEN 'fechado' ELSE 'aberto' END AS status_d14,
            CASE WHEN a.dias_desde_fim_coorte >= 30 THEN 'fechado' ELSE 'aberto' END AS status_d30,
            CASE WHEN a.dias_desde_fim_coorte >= 60 THEN 'fechado' ELSE 'aberto' END AS status_d60,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN 'fechado' ELSE 'aberto' END AS status_d90,
            CASE WHEN a.dias_desde_fim_coorte >= 90 THEN 'fechada' ELSE 'aberta' END AS status_coorte
        FROM agregado a CROSS JOIN historico h
    )
    SELECT * FROM final
    ORDER BY tipo_devolucao, coorte_semana;

    -- 3. Troca atômica
    RENAME TABLE
        instituto_experience.dashboard_reembolso_coortes       TO instituto_experience.dashboard_reembolso_coortes_old,
        instituto_experience.dashboard_reembolso_coortes_stage TO instituto_experience.dashboard_reembolso_coortes,
        instituto_experience.dashboard_reembolso_coortes_old   TO instituto_experience.dashboard_reembolso_coortes_stage;

END
```
