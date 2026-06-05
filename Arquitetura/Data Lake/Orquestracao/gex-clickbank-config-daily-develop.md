---
tipo: step-function
ambiente: develop
sfn_type: STANDARD
ultima_execucao: 2026-04-02 20:00
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-clickbank-config-daily-develop

> Step Function (orquestração) · ambiente **develop** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-develop` |
| Criada | 2026-03-30 19:27:43.610000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ⑂ parallel:
  - ramo 1:
    - ▶️ job [[mysql-to-bronze-exchange_rates-develop]]
  - ramo 2:
    - ▶️ job [[mysql-to-bronze-clickbank_fee_rates-develop]]
  - ramo 3:
    - ▶️ job [[mysql-to-bronze-general_product_costs-develop]]
  - ramo 4:
    - ▶️ job [[mysql-to-bronze-clickbank_internal_affiliates-develop]]
  - ramo 5:
    - ▶️ job [[mysql-to-bronze-clickbank_products-develop]]
- 🕷️ crawler [[gex-bronze-crawler-develop]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-clickbank-config-daily-timer-develop` _(desabilitada)_ — todo dia às 01:00 UTC · expressão `cron(0 1 * * ? *)`

## Dispara (alvos)

- **Jobs:** [[mysql-to-bronze-clickbank_fee_rates-develop]], [[mysql-to-bronze-clickbank_internal_affiliates-develop]], [[mysql-to-bronze-clickbank_products-develop]], [[mysql-to-bronze-exchange_rates-develop]], [[mysql-to-bronze-general_product_costs-develop]]
- **Crawlers:** [[gex-bronze-crawler-develop]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-04-02 20:00 | SUCCEEDED |
| 2026-03-30 19:41 | SUCCEEDED |
| 2026-03-30 19:36 | FAILED |

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
        "Name": "gex-bronze-crawler-develop"
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
                "JobName": "mysql-to-bronze-exchange_rates-develop"
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
                "JobName": "mysql-to-bronze-clickbank_fee_rates-develop"
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
                "JobName": "mysql-to-bronze-general_product_costs-develop"
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
                "JobName": "mysql-to-bronze-clickbank_internal_affiliates-develop"
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
                "JobName": "mysql-to-bronze-clickbank_products-develop"
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
