---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-03 13:05
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-bronze-to-silver-clickbank-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-04-09 19:28:37.742000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-bronze-to-silver-prod]]
- 🕷️ crawler [[gex-silver-clickbank-crawler-prod]]
- ▶️ job [[gex-silver-to-gold-prod]]
- 🕷️ crawler [[gex-gold-crawler-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-bronze-to-silver-15min-prod` — todo dia a cada 2h (no min 05) UTC · expressão `cron(5 */2 * * ? *)`

**Ao terminar, dispara:**
- quando job [[gex-bronze-to-silver-prod]] conclui `SUCCEEDED` ⟶ inicia [[gex-silver-gold-to-mysql-clickbank-prod]]

## Dispara (alvos)

- **Jobs:** [[gex-bronze-to-silver-prod]], [[gex-silver-to-gold-prod]]
- **Crawlers:** [[gex-gold-crawler-prod]], [[gex-silver-clickbank-crawler-prod]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-03 13:05 | SUCCEEDED |
| 2026-06-03 11:05 | SUCCEEDED |
| 2026-06-03 09:05 | SUCCEEDED |
| 2026-06-03 07:05 | SUCCEEDED |
| 2026-06-03 05:05 | SUCCEEDED |
| 2026-06-03 03:05 | SUCCEEDED |
| 2026-06-03 01:05 | SUCCEEDED |
| 2026-06-02 23:05 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_Silver_Job",
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
    "Atualizar_Catalogo_Silver": {
      "Catch": [
        {
          "ErrorEquals": [
            "Glue.CrawlerRunningException"
          ],
          "Next": "Rodar_Gold_Job"
        }
      ],
      "Next": "Rodar_Gold_Job",
      "Parameters": {
        "Name": "gex-silver-clickbank-crawler-prod"
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
    },
    "Rodar_Silver_Job": {
      "Next": "Atualizar_Catalogo_Silver",
      "Parameters": {
        "JobName": "gex-bronze-to-silver-prod"
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
