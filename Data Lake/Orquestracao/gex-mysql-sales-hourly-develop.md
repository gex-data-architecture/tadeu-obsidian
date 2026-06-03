---
tipo: step-function
ambiente: develop
sfn_type: STANDARD
ultima_execucao: 2026-03-25 17:48
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-mysql-sales-hourly-develop

> Step Function (orquestração) · ambiente **develop** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-develop` |
| Criada | 2026-03-24 12:47:57.887000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-mysql-to-bronze-develop]]
- 🕷️ crawler [[gex-bronze-crawler-develop]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-mysql-sales-hourly-timer-develop` _(desabilitada)_ — a cada 1 hour · expressão `rate(1 hour)`

## Dispara (alvos)

- **Jobs:** [[gex-mysql-to-bronze-develop]]
- **Crawlers:** [[gex-bronze-crawler-develop]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-03-25 17:48 | SUCCEEDED |
| 2026-03-25 16:48 | SUCCEEDED |
| 2026-03-25 15:48 | SUCCEEDED |
| 2026-03-25 14:48 | SUCCEEDED |
| 2026-03-25 13:48 | SUCCEEDED |
| 2026-03-25 12:48 | SUCCEEDED |
| 2026-03-25 11:48 | SUCCEEDED |
| 2026-03-25 10:48 | SUCCEEDED |

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
        "Name": "gex-bronze-crawler-develop"
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
