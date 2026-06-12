---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-11 23:00
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-mysql-sales-hourly-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-03-25 09:47:43.798000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-mysql-to-bronze-prod]]
- 🕷️ crawler [[gex-bronze-crawler-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-mysql-sales-daily-timer-prod` — todo dia às 02:00 UTC · expressão `cron(0 2 * * ? *)`

## Dispara (alvos)

- **Jobs:** [[gex-mysql-to-bronze-prod]]
- **Crawlers:** [[gex-bronze-crawler-prod]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-11 23:00 | SUCCEEDED |
| 2026-06-10 23:00 | SUCCEEDED |
| 2026-06-09 23:00 | SUCCEEDED |
| 2026-06-08 23:00 | SUCCEEDED |
| 2026-06-07 23:00 | SUCCEEDED |
| 2026-06-06 23:00 | SUCCEEDED |
| 2026-06-05 23:00 | SUCCEEDED |
| 2026-06-04 23:00 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Processar_Sales",
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
    "Processar_Sales": {
      "Next": "Atualizar_Catalogo_Bronze",
      "Parameters": {
        "Arguments": {
          "--db_table": "call_center_sales"
        },
        "JobName": "gex-mysql-to-bronze-prod"
      },
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Retry": [
        {
          "BackoffRate": 2,
          "ErrorEquals": [
            "Glue.InternalServiceException",
            "Glue.ConcurrentRunsExceededException"
          ],
          "IntervalSeconds": 2,
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
