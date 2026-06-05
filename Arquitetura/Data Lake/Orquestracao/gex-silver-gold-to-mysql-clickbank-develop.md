---
tipo: step-function
ambiente: develop
sfn_type: STANDARD
ultima_execucao: 2026-06-03 14:20
ultimo_estado: FAILED
tags: [datalake, step-function, orquestracao]
---

# gex-silver-gold-to-mysql-clickbank-develop

> Step Function (orquestração) · ambiente **develop** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-develop` |
| Criada | 2026-04-27 14:53:11.893000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[silver-clickbank-physical-to-mysql-develop]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Agendada (EventBridge schedule):**
- `gex-silver-gold-to-mysql-clickbank-15min-develop` — todo dia a cada 15 min a partir do min 20 UTC · expressão `cron(20/15 * * * ? *)`

## Dispara (alvos)

- **Jobs:** [[silver-clickbank-physical-to-mysql-develop]]
- **Crawlers:** —
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-03 14:20 | FAILED |
| 2026-06-03 13:50 | FAILED |
| 2026-06-03 13:35 | FAILED |
| 2026-06-03 13:20 | FAILED |
| 2026-06-03 12:50 | FAILED |
| 2026-06-03 12:35 | FAILED |
| 2026-06-03 12:20 | FAILED |
| 2026-06-03 11:50 | FAILED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_Silver_To_MySQL",
  "States": {
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Rodar_Silver_To_MySQL": {
      "Catch": [
        {
          "ErrorEquals": [
            "Glue.ConcurrentRunsExceededException"
          ],
          "Next": "Finalizar_Com_Sucesso"
        }
      ],
      "Next": "Finalizar_Com_Sucesso",
      "Parameters": {
        "JobName": "silver-clickbank-physical-to-mysql-develop"
      },
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Retry": [
        {
          "BackoffRate": 2,
          "ErrorEquals": [
            "Glue.InternalServiceException"
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
