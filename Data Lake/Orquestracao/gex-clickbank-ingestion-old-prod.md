---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-04-10 02:00
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-clickbank-ingestion-old-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-04-06 11:36:53.412000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-landing-to-bronze-prod]]
- 🕷️ crawler [[gex-bronze-crawler-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-clickbank-old-processing-prod` _(desabilitada)_ — todo dia às 05:00 UTC · expressão `cron(0 5 * * ? *)`

## Dispara (alvos)

- **Jobs:** [[gex-landing-to-bronze-prod]]
- **Crawlers:** [[gex-bronze-crawler-prod]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-04-10 02:00 | SUCCEEDED |
| 2026-04-09 02:00 | SUCCEEDED |
| 2026-04-08 02:00 | SUCCEEDED |
| 2026-04-07 02:00 | SUCCEEDED |
| 2026-04-06 18:57 | FAILED |
| 2026-04-06 18:37 | FAILED |
| 2026-04-06 18:17 | FAILED |
| 2026-04-06 17:57 | FAILED |

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
        "Name": "gex-bronze-crawler-prod"
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
        "JobName": "gex-landing-to-bronze-prod"
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
