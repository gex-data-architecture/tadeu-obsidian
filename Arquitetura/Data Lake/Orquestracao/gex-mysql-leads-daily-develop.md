---
tipo: step-function
ambiente: develop
sfn_type: STANDARD
ultima_execucao: 2026-03-24 23:00
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-mysql-leads-daily-develop

> Step Function (orquestração) · ambiente **develop** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-develop` |
| Criada | 2026-03-24 12:47:57.867000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-mysql-to-bronze-develop]]
- 🕷️ crawler [[gex-bronze-crawler-develop]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-mysql-leads-daily-timer-develop` _(desabilitada)_ — todo dia às 02:00 UTC · expressão `cron(0 2 * * ? *)`

## Dispara (alvos)

- **Jobs:** [[gex-mysql-to-bronze-develop]]
- **Crawlers:** [[gex-bronze-crawler-develop]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-03-24 23:00 | SUCCEEDED |
| 2026-03-24 15:07 | SUCCEEDED |
| 2026-03-24 15:00 | FAILED |
| 2026-03-24 14:43 | FAILED |
| 2026-03-24 14:53 | FAILED |
| 2026-03-24 14:23 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Processar_Leads",
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
    "Processar_Leads": {
      "Next": "Atualizar_Catalogo_Bronze",
      "Parameters": {
        "Arguments": {
          "--db_table": "unified_lead_events_new"
        },
        "JobName": "gex-mysql-to-bronze-develop"
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
````

## Relacionados
[[00-Data-Lake]] · [[00-Orquestracao]]
