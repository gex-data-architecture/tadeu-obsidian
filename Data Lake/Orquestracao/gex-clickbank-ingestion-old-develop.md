---
tipo: step-function
ambiente: develop
sfn_type: STANDARD
ultima_execucao: 2026-04-06 11:43
ultimo_estado: FAILED
tags: [datalake, step-function, orquestracao]
---

# gex-clickbank-ingestion-old-develop

> Step Function (orquestração) · ambiente **develop** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-develop` |
| Criada | 2026-03-31 17:40:25.770000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-landing-to-bronze-develop]]
- 🕷️ crawler [[gex-bronze-crawler-develop]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-clickbank-old-processing-develop` _(desabilitada)_ — todo dia às 05:00 UTC · expressão `cron(0 5 * * ? *)`

## Dispara (alvos)

- **Jobs:** [[gex-landing-to-bronze-develop]]
- **Crawlers:** [[gex-bronze-crawler-develop]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-04-06 11:43 | FAILED |
| 2026-04-06 11:23 | FAILED |
| 2026-04-06 11:03 | FAILED |
| 2026-04-06 10:43 | FAILED |
| 2026-04-06 10:23 | FAILED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Processar_ClickBank_Old",
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
    "Processar_ClickBank_Old": {
      "Next": "Atualizar_Catalogo_Bronze",
      "Parameters": {
        "JobName": "gex-landing-to-bronze-develop"
      },
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Retry": [
        {
          "BackoffRate": 2,
          "ErrorEquals": [
            "Glue.InternalServiceException",
            "Glue.ConcurrentRunsExceededException"
          ],
          "IntervalSeconds": 30,
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
