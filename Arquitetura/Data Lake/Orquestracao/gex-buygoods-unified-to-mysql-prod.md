---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-12 09:44
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-buygoods-unified-to-mysql-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-06-01 17:37:26.801000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-buygoods-unified-to-mysql-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Disparada quando:**
- job [[bronze-to-silver-buygoods-prod]] = `SUCCEEDED` (via regra EventBridge) ⟶ origem provável: [[gex-bronze-to-silver-buygoods-prod]]

**Ao terminar, dispara:**
- quando job [[gex-buygoods-unified-to-mysql-prod]] conclui `SUCCEEDED` ⟶ inicia [[gex-buygoods-gold-prod]]

## Dispara (alvos)

- **Jobs:** [[gex-buygoods-unified-to-mysql-prod]]
- **Crawlers:** —
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-12 09:44 | SUCCEEDED |
| 2026-06-12 07:43 | SUCCEEDED |
| 2026-06-12 05:43 | SUCCEEDED |
| 2026-06-12 03:42 | SUCCEEDED |
| 2026-06-12 01:43 | SUCCEEDED |
| 2026-06-11 23:42 | SUCCEEDED |
| 2026-06-11 21:44 | SUCCEEDED |
| 2026-06-11 19:43 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_BuyGoods_Unified",
  "States": {
    "Falhar_Execucao": {
      "Cause": "Falha na unificacao BuyGoods para MySQL",
      "Error": "BuyGoodsUnifiedExecutionFailed",
      "Type": "Fail"
    },
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Rodar_BuyGoods_Unified": {
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
        "JobName": "gex-buygoods-unified-to-mysql-prod"
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
