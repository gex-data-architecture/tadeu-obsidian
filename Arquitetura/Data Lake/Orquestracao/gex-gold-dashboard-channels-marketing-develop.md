---
tipo: step-function
ambiente: develop
sfn_type: STANDARD
ultima_execucao: —
ultimo_estado: —
tags: [datalake, step-function, orquestracao]
---

# gex-gold-dashboard-channels-marketing-develop

> Step Function (orquestração) · ambiente **develop** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-develop` |
| Criada | 2026-04-23 14:34:06.688000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gold-dashboard-channels-marketing-develop]]
- 🕷️ crawler [[gex-gold-dashboard-channels-marketing-crawler-develop]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-gold-dashboard-channels-marketing-timer-develop` _(desabilitada)_ — todo dia a cada 15 min a partir do min 20 UTC · expressão `cron(20/15 * * * ? *)`

## Dispara (alvos)

- **Jobs:** [[gold-dashboard-channels-marketing-develop]]
- **Crawlers:** [[gex-gold-dashboard-channels-marketing-crawler-develop]]
- **SFN aninhadas:** —

## Últimas execuções

> Sem execuções registradas.

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_H5_Gold_Job",
  "States": {
    "Atualizar_Catalogo_H5_Gold": {
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
        "Name": "gex-gold-dashboard-channels-marketing-crawler-develop"
      },
      "Resource": "arn:aws:states:::aws-sdk:glue:startCrawler",
      "Type": "Task"
    },
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Rodar_H5_Gold_Job": {
      "Next": "Atualizar_Catalogo_H5_Gold",
      "Parameters": {
        "JobName": "gold-dashboard-channels-marketing-develop"
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
