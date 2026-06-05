---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-03 13:38
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-mysql-leads-daily-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-03-25 09:47:43.801000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-mysql-leads-heavy-prod]]
- 🕷️ crawler [[gex-bronze-crawler-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-mysql-leads-hourly-timer-prod` — a cada 1 hour · expressão `rate(1 hour)`

## Dispara (alvos)

- **Jobs:** [[gex-mysql-leads-heavy-prod]]
- **Crawlers:** [[gex-bronze-crawler-prod]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-03 13:38 | SUCCEEDED |
| 2026-06-03 12:38 | SUCCEEDED |
| 2026-06-03 11:38 | SUCCEEDED |
| 2026-06-03 10:38 | SUCCEEDED |
| 2026-06-03 09:38 | SUCCEEDED |
| 2026-06-03 08:38 | SUCCEEDED |
| 2026-06-03 07:38 | SUCCEEDED |
| 2026-06-03 06:38 | SUCCEEDED |

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
        "Name": "gex-bronze-crawler-prod"
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
        "JobName": "gex-mysql-leads-heavy-prod"
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
