---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-12 09:45
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-silver-gold-to-mysql-clickbank-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-04-27 14:53:18.781000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ⑂ parallel:
  - ramo 1:
    - ▶️ job [[silver-clickbank-physical-to-mysql-prod]]
  - ramo 2:
    - ▶️ job [[gex-silver-to-gold-prod]]
    - ▶️ job [[gold-clickbank-to-mysql-prod]]
- ◇ escolha (`Avaliar_Resultados_Paralelo`)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-silver-gold-to-mysql-clickbank-15min-prod` _(desabilitada)_ — todo dia a cada 15 min a partir do min 20 UTC · expressão `cron(20/15 * * * ? *)`

**Disparada quando:**
- job [[gex-bronze-to-silver-prod]] = `SUCCEEDED` (via regra EventBridge) ⟶ origem provável: [[gex-bronze-to-silver-clickbank-prod]]

## Dispara (alvos)

- **Jobs:** [[gex-silver-to-gold-prod]], [[gold-clickbank-to-mysql-prod]], [[silver-clickbank-physical-to-mysql-prod]]
- **Crawlers:** —
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-12 09:45 | SUCCEEDED |
| 2026-06-12 07:43 | SUCCEEDED |
| 2026-06-12 05:43 | FAILED |
| 2026-06-12 03:44 | SUCCEEDED |
| 2026-06-12 01:42 | SUCCEEDED |
| 2026-06-11 23:43 | SUCCEEDED |
| 2026-06-11 21:48 | SUCCEEDED |
| 2026-06-11 19:43 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Executar_Replicacoes_Em_Paralelo",
  "States": {
    "Avaliar_Resultados_Paralelo": {
      "Choices": [
        {
          "Next": "Falhar_Execucao",
          "StringEquals": "failed",
          "Variable": "$.branch_results[0].status"
        },
        {
          "Next": "Falhar_Execucao",
          "StringEquals": "failed",
          "Variable": "$.branch_results[1].status"
        }
      ],
      "Default": "Finalizar_Com_Sucesso",
      "Type": "Choice"
    },
    "Executar_Replicacoes_Em_Paralelo": {
      "Branches": [
        {
          "StartAt": "Rodar_Silver_To_MySQL",
          "States": {
            "Branch1_Falha": {
              "End": true,
              "Parameters": {
                "branch": "silver_to_mysql",
                "cause.$": "$.error.Cause",
                "error.$": "$.error.Error",
                "status": "failed"
              },
              "Type": "Pass"
            },
            "Branch1_Skip_Concorrencia": {
              "End": true,
              "Result": {
                "branch": "silver_to_mysql",
                "reason": "concurrent_run",
                "status": "skipped"
              },
              "Type": "Pass"
            },
            "Branch1_Sucesso": {
              "End": true,
              "Result": {
                "branch": "silver_to_mysql",
                "status": "succeeded"
              },
              "Type": "Pass"
            },
            "Rodar_Silver_To_MySQL": {
              "Catch": [
                {
                  "ErrorEquals": [
                    "Glue.ConcurrentRunsExceededException"
                  ],
                  "Next": "Branch1_Skip_Concorrencia"
                },
                {
                  "ErrorEquals": [
                    "States.ALL"
                  ],
                  "Next": "Branch1_Falha",
                  "ResultPath": "$.error"
                }
              ],
              "Next": "Branch1_Sucesso",
              "Parameters": {
                "JobName": "silver-clickbank-physical-to-mysql-prod"
              },
              "Resource": "arn:aws:states:::glue:startJobRun.sync",
              "Retry": [
                {
                  "BackoffRate": 2,
                  "ErrorEquals": [
                    "Glue.InternalServiceException"
                  ],
                  "IntervalSeconds": 60,
                  "MaxAttempts": 3
                }
              ],
              "Type": "Task"
            }
          }
        },
        {
          "StartAt": "Rodar_Silver_To_Gold",
          "States": {
            "Branch2_Falha": {
              "End": true,
              "Parameters": {
                "branch": "silver_to_gold_to_mysql",
                "cause.$": "$.error.Cause",
                "error.$": "$.error.Error",
                "status": "failed"
              },
              "Type": "Pass"
            },
            "Branch2_Skip_Concorrencia_GoldToMySQL": {
              "End": true,
              "Result": {
                "branch": "silver_to_gold_to_mysql",
                "reason": "concurrent_run_gold_to_mysql",
                "status": "skipped"
              },
              "Type": "Pass"
            },
            "Branch2_Skip_Concorrencia_SilverToGold": {
              "End": true,
              "Result": {
                "branch": "silver_to_gold_to_mysql",
                "reason": "concurrent_run_silver_to_gold",
                "status": "skipped"
              },
              "Type": "Pass"
            },
            "Branch2_Sucesso": {
              "End": true,
              "Result": {
                "branch": "silver_to_gold_to_mysql",
                "status": "succeeded"
              },
              "Type": "Pass"
            },
            "Rodar_Gold_To_MySQL": {
              "Catch": [
                {
                  "ErrorEquals": [
                    "Glue.ConcurrentRunsExceededException"
                  ],
                  "Next": "Branch2_Skip_Concorrencia_GoldToMySQL"
                },
                {
                  "ErrorEquals": [
                    "States.ALL"
                  ],
                  "Next": "Branch2_Falha",
                  "ResultPath": "$.error"
                }
              ],
              "Next": "Branch2_Sucesso",
              "Parameters": {
                "JobName": "gold-clickbank-to-mysql-prod"
              },
              "Resource": "arn:aws:states:::glue:startJobRun.sync",
              "Retry": [
                {
                  "BackoffRate": 2,
                  "ErrorEquals": [
                    "Glue.InternalServiceException"
                  ],
                  "IntervalSeconds": 60,
                  "MaxAttempts": 3
                }
              ],
              "Type": "Task"
            },
            "Rodar_Silver_To_Gold": {
              "Catch": [
                {
                  "ErrorEquals": [
                    "Glue.ConcurrentRunsExceededException"
                  ],
                  "Next": "Branch2_Skip_Concorrencia_SilverToGold"
                },
                {
                  "ErrorEquals": [
                    "States.ALL"
                  ],
                  "Next": "Branch2_Falha",
                  "ResultPath": "$.error"
                }
              ],
              "Next": "Rodar_Gold_To_MySQL",
              "Parameters": {
                "JobName": "gex-silver-to-gold-prod"
              },
              "Resource": "arn:aws:states:::glue:startJobRun.sync",
              "Retry": [
                {
                  "BackoffRate": 2,
                  "ErrorEquals": [
                    "Glue.InternalServiceException"
                  ],
                  "IntervalSeconds": 60,
                  "MaxAttempts": 3
                }
              ],
              "Type": "Task"
            }
          }
        }
      ],
      "Next": "Avaliar_Resultados_Paralelo",
      "ResultPath": "$.branch_results",
      "Type": "Parallel"
    },
    "Falhar_Execucao": {
      "Cause": "Uma ou mais branches falharam na replicacao Silver/Gold para MySQL",
      "Error": "SilverGoldToMySQLExecutionFailed",
      "Type": "Fail"
    },
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    }
  }
}
````

## Relacionados
[[00-Data-Lake]] · [[00-Orquestracao]]
