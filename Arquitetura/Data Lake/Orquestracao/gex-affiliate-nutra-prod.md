---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-11 15:19
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-affiliate-nutra-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-06-10 14:49:01.368000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-affiliate-nutra-brl-prod]]
- ▶️ job [[gex-affiliate-nutra-usd-prod]]
- 🕷️ crawler [[gex-affiliate-nutra-crawler-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Disparada quando:**
- job [[gex-gold-clickbank-buygoods-prod]] = `SUCCEEDED` (via regra EventBridge) ⟶ origem provável: [[gex-gold-clickbank-buygoods-prod]]

## Dispara (alvos)

- **Jobs:** [[gex-affiliate-nutra-brl-prod]], [[gex-affiliate-nutra-usd-prod]]
- **Crawlers:** [[gex-affiliate-nutra-crawler-prod]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-11 15:19 | SUCCEEDED |
| 2026-06-11 14:15 | SUCCEEDED |
| 2026-06-11 12:15 | SUCCEEDED |
| 2026-06-11 10:14 | SUCCEEDED |
| 2026-06-11 08:11 | SUCCEEDED |
| 2026-06-11 06:16 | SUCCEEDED |
| 2026-06-11 04:17 | SUCCEEDED |
| 2026-06-11 02:11 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_Mart_BRL",
  "States": {
    "Atualizar_Catalogo_Mart": {
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
        "Name": "gex-affiliate-nutra-crawler-prod"
      },
      "Resource": "arn:aws:states:::aws-sdk:glue:startCrawler",
      "Type": "Task"
    },
    "Falhar_Execucao": {
      "Cause": "Falha no mart affiliate_nutra",
      "Error": "AffiliateNutraExecutionFailed",
      "Type": "Fail"
    },
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Rodar_Mart_BRL": {
      "Catch": [
        {
          "ErrorEquals": [
            "Glue.ConcurrentRunsExceededException"
          ],
          "Next": "Rodar_Mart_USD"
        },
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "Falhar_Execucao",
          "ResultPath": "$.error"
        }
      ],
      "Next": "Rodar_Mart_USD",
      "Parameters": {
        "JobName": "gex-affiliate-nutra-brl-prod"
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
    "Rodar_Mart_USD": {
      "Catch": [
        {
          "ErrorEquals": [
            "Glue.ConcurrentRunsExceededException"
          ],
          "Next": "Atualizar_Catalogo_Mart"
        },
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "Falhar_Execucao",
          "ResultPath": "$.error"
        }
      ],
      "Next": "Atualizar_Catalogo_Mart",
      "Parameters": {
        "JobName": "gex-affiliate-nutra-usd-prod"
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
