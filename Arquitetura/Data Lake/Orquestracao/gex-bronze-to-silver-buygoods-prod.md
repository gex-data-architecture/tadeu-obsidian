---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-12 09:30
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-bronze-to-silver-buygoods-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-05-21 14:44:01.587000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-landing-to-bronze-buygoods-prod]]
- 🕷️ crawler [[gex-bronze-crawler-prod]]
- ▶️ job [[bronze-to-silver-buygoods-prod]]
- 🕷️ crawler [[gex-silver-buygoods-crawler-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-bronze-to-silver-buygoods-2h-prod` — todo dia a cada 2h (no min 30) UTC · expressão `cron(30 0/2 * * ? *)`

**Ao terminar, dispara:**
- quando job [[bronze-to-silver-buygoods-prod]] conclui `SUCCEEDED` ⟶ inicia [[gex-silver-to-mysql-buygoods-prod]]
- quando job [[bronze-to-silver-buygoods-prod]] conclui `SUCCEEDED` ⟶ inicia [[gex-buygoods-unified-to-mysql-prod]]

## Dispara (alvos)

- **Jobs:** [[bronze-to-silver-buygoods-prod]], [[gex-landing-to-bronze-buygoods-prod]]
- **Crawlers:** [[gex-bronze-crawler-prod]], [[gex-silver-buygoods-crawler-prod]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-12 09:30 | SUCCEEDED |
| 2026-06-12 07:30 | SUCCEEDED |
| 2026-06-12 05:30 | SUCCEEDED |
| 2026-06-12 03:30 | SUCCEEDED |
| 2026-06-12 01:30 | SUCCEEDED |
| 2026-06-11 23:30 | SUCCEEDED |
| 2026-06-11 21:30 | SUCCEEDED |
| 2026-06-11 19:30 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_Bronze_BuyGoods",
  "States": {
    "Atualizar_Catalogo_Bronze_BuyGoods": {
      "Catch": [
        {
          "ErrorEquals": [
            "Glue.CrawlerRunningException"
          ],
          "Next": "Rodar_Silver_BuyGoods"
        }
      ],
      "Next": "Rodar_Silver_BuyGoods",
      "Parameters": {
        "Name": "gex-bronze-crawler-prod"
      },
      "Resource": "arn:aws:states:::aws-sdk:glue:startCrawler",
      "Type": "Task"
    },
    "Atualizar_Catalogo_Silver_BuyGoods": {
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
        "Name": "gex-silver-buygoods-crawler-prod"
      },
      "Resource": "arn:aws:states:::aws-sdk:glue:startCrawler",
      "Type": "Task"
    },
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Rodar_Bronze_BuyGoods": {
      "Next": "Atualizar_Catalogo_Bronze_BuyGoods",
      "Parameters": {
        "JobName": "gex-landing-to-bronze-buygoods-prod"
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
    "Rodar_Silver_BuyGoods": {
      "Next": "Atualizar_Catalogo_Silver_BuyGoods",
      "Parameters": {
        "JobName": "bronze-to-silver-buygoods-prod"
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
