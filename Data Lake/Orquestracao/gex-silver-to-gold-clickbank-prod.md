---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-04-23 11:55
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-silver-to-gold-clickbank-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-04-23 11:23:51.216000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-silver-to-gold-prod]]
- 🕷️ crawler [[gex-gold-crawler-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-silver-to-gold-15min-prod` _(desabilitada)_ — todo dia a cada 15 min a partir do min 10 UTC · expressão `cron(10/15 * * * ? *)`

## Dispara (alvos)

- **Jobs:** [[gex-silver-to-gold-prod]]
- **Crawlers:** [[gex-gold-crawler-prod]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-04-23 11:55 | SUCCEEDED |
| 2026-04-23 11:40 | SUCCEEDED |
| 2026-04-23 11:25 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_Gold_Job",
  "States": {
    "Atualizar_Catalogo_Gold": {
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
        "Name": "gex-gold-crawler-prod"
      },
      "Resource": "arn:aws:states:::aws-sdk:glue:startCrawler",
      "Type": "Task"
    },
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Rodar_Gold_Job": {
      "Next": "Atualizar_Catalogo_Gold",
      "Parameters": {
        "JobName": "gex-silver-to-gold-prod"
      },
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Retry": [
        {
          "BackoffRate": 2,
          "ErrorEquals": [
            "Glue.InternalServiceException",
            "Glue.ConcurrentRunsExceededException"
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
