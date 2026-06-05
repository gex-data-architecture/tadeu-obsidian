---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-03 13:42
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-silver-to-mysql-buygoods-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-05-21 16:08:58.917000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[silver-buygoods-physical-to-mysql-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Disparada quando:**
- job [[bronze-to-silver-buygoods-prod]] = `SUCCEEDED` (via regra EventBridge) ⟶ origem provável: [[gex-bronze-to-silver-buygoods-prod]]

## Dispara (alvos)

- **Jobs:** [[silver-buygoods-physical-to-mysql-prod]]
- **Crawlers:** —
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-03 13:42 | SUCCEEDED |
| 2026-06-03 13:22 | SUCCEEDED |
| 2026-06-03 11:42 | SUCCEEDED |
| 2026-06-03 09:42 | SUCCEEDED |
| 2026-06-03 07:41 | SUCCEEDED |
| 2026-06-03 05:41 | SUCCEEDED |
| 2026-06-03 03:42 | SUCCEEDED |
| 2026-06-03 01:41 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_Silver_BuyGoods_To_MySQL",
  "States": {
    "Falhar_Execucao": {
      "Cause": "Falha na replicacao Silver BuyGoods para MySQL",
      "Error": "SilverToMySQLBuyGoodsExecutionFailed",
      "Type": "Fail"
    },
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Rodar_Silver_BuyGoods_To_MySQL": {
      "Catch": [
        {
          "ErrorEquals": [
            "Glue.ConcurrentRunsExceededException"
          ],
          "Next": "Finalizar_Com_Sucesso"
        },
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "Falhar_Execucao",
          "ResultPath": "$.error"
        }
      ],
      "Next": "Finalizar_Com_Sucesso",
      "Parameters": {
        "JobName": "silver-buygoods-physical-to-mysql-prod"
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
