---
tipo: step-function
ambiente: develop
sfn_type: STANDARD
ultima_execucao: —
ultimo_estado: —
tags: [datalake, step-function, orquestracao]
---

# gex-gold-to-mysql-channels-marketing-develop

> Step Function (orquestração) · ambiente **develop** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-develop` |
| Criada | 2026-04-24 14:32:34.725000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gold-to-mysql-channels-marketing-develop]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-gold-to-mysql-channels-marketing-timer-develop` _(desabilitada)_ — todo dia a cada 15 min a partir do min 25 UTC · expressão `cron(25/15 * * * ? *)`

## Dispara (alvos)

- **Jobs:** [[gold-to-mysql-channels-marketing-develop]]
- **Crawlers:** —
- **SFN aninhadas:** —

## Últimas execuções

> Sem execuções registradas.

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_Replicacao_MySQL",
  "States": {
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Rodar_Replicacao_MySQL": {
      "Next": "Finalizar_Com_Sucesso",
      "Parameters": {
        "JobName": "gold-to-mysql-channels-marketing-develop"
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
