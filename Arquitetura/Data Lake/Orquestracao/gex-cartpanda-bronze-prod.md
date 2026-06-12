---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-12 03:00
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-cartpanda-bronze-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-06-10 09:14:17.903000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-cartpanda-bronze-prod]]
- 🕷️ crawler [[gex-cartpanda-bronze-crawler-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-cartpanda-bronze-daily-prod` — todo dia às 06:00 UTC · expressão `cron(0 6 * * ? *)`

## Dispara (alvos)

- **Jobs:** [[gex-cartpanda-bronze-prod]]
- **Crawlers:** [[gex-cartpanda-bronze-crawler-prod]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-12 03:00 | SUCCEEDED |
| 2026-06-11 03:00 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_Cartpanda_Bronze",
  "States": {
    "Atualizar_Catalogo_Cartpanda": {
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "Finalizar_Com_Sucesso"
        }
      ],
      "Next": "Finalizar_Com_Sucesso",
      "Parameters": {
        "Name": "gex-cartpanda-bronze-crawler-prod"
      },
      "Resource": "arn:aws:states:::aws-sdk:glue:startCrawler",
      "Type": "Task"
    },
    "Falhar_Execucao": {
      "Cause": "Falha na ingestao bronze do cartpanda_physical",
      "Error": "CartpandaBronzeExecutionFailed",
      "Type": "Fail"
    },
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Rodar_Cartpanda_Bronze": {
      "Catch": [
        {
          "ErrorEquals": [
            "Glue.ConcurrentRunsExceededException"
          ],
          "Next": "Finalizar_Com_Sucesso"
        },
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "Falhar_Execucao",
          "ResultPath": "$.error"
        }
      ],
      "Next": "Atualizar_Catalogo_Cartpanda",
      "Parameters": {
        "JobName": "gex-cartpanda-bronze-prod"
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
````

## Relacionados
[[00-Data-Lake]] · [[00-Orquestracao]]
