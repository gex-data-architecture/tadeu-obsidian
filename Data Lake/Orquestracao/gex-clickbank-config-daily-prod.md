---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-02 22:00
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-clickbank-config-daily-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-04-06 11:36:53.434000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ⑂ parallel:
  - ramo 1:
    - ▶️ job [[mysql-to-bronze-exchange_rates-prod]]
  - ramo 2:
    - ▶️ job [[mysql-to-bronze-clickbank_fee_rates-prod]]
  - ramo 3:
    - ▶️ job [[mysql-to-bronze-general_product_costs-prod]]
  - ramo 4:
    - ▶️ job [[mysql-to-bronze-clickbank_internal_affiliates-prod]]
  - ramo 5:
    - ▶️ job [[mysql-to-bronze-clickbank_products-prod]]
  - ramo 6:
    - ▶️ job [[mysql-to-bronze-buygoods_internal_affiliates-prod]]
  - ramo 7:
    - ▶️ job [[mysql-to-bronze-buygoods_products-prod]]
- 🕷️ crawler [[gex-bronze-crawler-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-clickbank-config-daily-timer-prod` — todo dia às 01:00 UTC · expressão `cron(0 1 * * ? *)`

## Dispara (alvos)

- **Jobs:** [[mysql-to-bronze-buygoods_internal_affiliates-prod]], [[mysql-to-bronze-buygoods_products-prod]], [[mysql-to-bronze-clickbank_fee_rates-prod]], [[mysql-to-bronze-clickbank_internal_affiliates-prod]], [[mysql-to-bronze-clickbank_products-prod]], [[mysql-to-bronze-exchange_rates-prod]], [[mysql-to-bronze-general_product_costs-prod]]
- **Crawlers:** [[gex-bronze-crawler-prod]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-02 22:00 | SUCCEEDED |
| 2026-06-01 22:00 | SUCCEEDED |
| 2026-05-31 22:00 | SUCCEEDED |
| 2026-05-30 22:00 | SUCCEEDED |
| 2026-05-29 22:00 | SUCCEEDED |
| 2026-05-28 22:00 | SUCCEEDED |
| 2026-05-27 22:00 | SUCCEEDED |
| 2026-05-26 22:00 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Ingerir_Config_Em_Paralelo",
  "States": {
    "Atualizar_Catalogo_Bronze": {
      "Catch": [
        {
          "ErrorEquals": [
            "Glue.CrawlerRunningException"
          ],
          "Next": "Finalizar_Com_Sucesso"
        }
      ],
      "Next": "Finalizar_Com_Sucesso",
      "Parameters": {
        "Name": "gex-bronze-crawler-prod"
      },
      "Resource": "arn:aws:states:::aws-sdk:glue:startCrawler",
      "Type": "Task"
    },
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Ingerir_Config_Em_Paralelo": {
      "Branches": [
        {
          "StartAt": "exchange_rates",
          "States": {
            "exchange_rates": {
              "End": true,
              "Parameters": {
                "JobName": "mysql-to-bronze-exchange_rates-prod"
              },
              "Resource": "arn:aws:states:::glue:startJobRun.sync",
              "Retry": [
                {
                  "BackoffRate": 2,
                  "ErrorEquals": [
                    "Glue.InternalServiceException",
                    "Glue.ConcurrentRunsExceededException"
                  ],
                  "IntervalSeconds": 5,
                  "MaxAttempts": 3
                }
              ],
              "Type": "Task"
            }
          }
        },
        {
          "StartAt": "clickbank_fee_rates",
          "States": {
            "clickbank_fee_rates": {
              "End": true,
              "Parameters": {
                "JobName": "mysql-to-bronze-clickbank_fee_rates-prod"
              },
              "Resource": "arn:aws:states:::glue:startJobRun.sync",
              "Retry": [
                {
                  "BackoffRate": 2,
                  "ErrorEquals": [
                    "Glue.InternalServiceException",
                    "Glue.ConcurrentRunsExceededException"
                  ],
                  "IntervalSeconds": 5,
                  "MaxAttempts": 3
                }
              ],
              "Type": "Task"
            }
          }
        },
        {
          "StartAt": "general_product_costs",
          "States": {
            "general_product_costs": {
              "End": true,
              "Parameters": {
                "JobName": "mysql-to-bronze-general_product_costs-prod"
              },
              "Resource": "arn:aws:states:::glue:startJobRun.sync",
              "Retry": [
                {
                  "BackoffRate": 2,
                  "ErrorEquals": [
                    "Glue.InternalServiceException",
                    "Glue.ConcurrentRunsExceededException"
                  ],
                  "IntervalSeconds": 5,
                  "MaxAttempts": 3
                }
              ],
              "Type": "Task"
            }
          }
        },
        {
          "StartAt": "clickbank_internal_affiliates",
          "States": {
            "clickbank_internal_affiliates": {
              "End": true,
              "Parameters": {
                "JobName": "mysql-to-bronze-clickbank_internal_affiliates-prod"
              },
              "Resource": "arn:aws:states:::glue:startJobRun.sync",
              "Retry": [
                {
                  "BackoffRate": 2,
                  "ErrorEquals": [
                    "Glue.InternalServiceException",
                    "Glue.ConcurrentRunsExceededException"
                  ],
                  "IntervalSeconds": 5,
                  "MaxAttempts": 3
                }
              ],
              "Type": "Task"
            }
          }
        },
        {
          "StartAt": "clickbank_products",
          "States": {
            "clickbank_products": {
              "End": true,
              "Parameters": {
                "JobName": "mysql-to-bronze-clickbank_products-prod"
              },
              "Resource": "arn:aws:states:::glue:startJobRun.sync",
              "Retry": [
                {
                  "BackoffRate": 2,
                  "ErrorEquals": [
                    "Glue.InternalServiceException",
                    "Glue.ConcurrentRunsExceededException"
                  ],
                  "IntervalSeconds": 5,
                  "MaxAttempts": 3
                }
              ],
              "Type": "Task"
            }
          }
        },
        {
          "StartAt": "buygoods_internal_affiliates",
          "States": {
            "buygoods_internal_affiliates": {
              "End": true,
              "Parameters": {
                "JobName": "mysql-to-bronze-buygoods_internal_affiliates-prod"
              },
              "Resource": "arn:aws:states:::glue:startJobRun.sync",
              "Retry": [
                {
                  "BackoffRate": 2,
                  "ErrorEquals": [
                    "Glue.InternalServiceException",
                    "Glue.ConcurrentRunsExceededException"
                  ],
                  "IntervalSeconds": 5,
                  "MaxAttempts": 3
                }
              ],
              "Type": "Task"
            }
          }
        },
        {
          "StartAt": "buygoods_products",
          "States": {
            "buygoods_products": {
              "End": true,
              "Parameters": {
                "JobName": "mysql-to-bronze-buygoods_products-prod"
              },
              "Resource": "arn:aws:states:::glue:startJobRun.sync",
              "Retry": [
                {
                  "BackoffRate": 2,
                  "ErrorEquals": [
                    "Glue.InternalServiceException",
                    "Glue.ConcurrentRunsExceededException"
                  ],
                  "IntervalSeconds": 5,
                  "MaxAttempts": 3
                }
              ],
              "Type": "Task"
            }
          }
        }
      ],
      "Next": "Atualizar_Catalogo_Bronze",
      "Type": "Parallel"
    }
  }
}
````

## Relacionados
[[00-Data-Lake]] · [[00-Orquestracao]]
