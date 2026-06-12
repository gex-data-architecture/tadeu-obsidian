---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-12 09:51
ultimo_estado: SUCCEEDED
tags: [datalake, step-function, orquestracao]
---

# gex-buygoods-gold-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-06-02 14:24:13.359000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-buygoods-gold-prod]]
- 🕷️ crawler [[gex-buygoods-gold-crawler-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Disparada quando:**
- job [[gex-buygoods-unified-to-mysql-prod]] = `SUCCEEDED` (via regra EventBridge) ⟶ origem provável: [[gex-buygoods-unified-to-mysql-prod]]

**Ao terminar, dispara:**
- quando job [[gex-buygoods-gold-prod]] conclui `SUCCEEDED` ⟶ inicia [[gex-gold-clickbank-buygoods-prod]]

## Dispara (alvos)

- **Jobs:** [[gex-buygoods-gold-prod]]
- **Crawlers:** [[gex-buygoods-gold-crawler-prod]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-12 09:51 | SUCCEEDED |
| 2026-06-12 07:50 | SUCCEEDED |
| 2026-06-12 05:51 | SUCCEEDED |
| 2026-06-12 03:49 | SUCCEEDED |
| 2026-06-12 01:50 | SUCCEEDED |
| 2026-06-11 23:48 | SUCCEEDED |
| 2026-06-11 21:50 | SUCCEEDED |
| 2026-06-11 19:50 | SUCCEEDED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_Gold_BuyGoods",
  "States": {
    "Atualizar_Catalogo_Gold": {
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "Finalizar_Com_Sucesso"
        }
      ],
      "Next": "Finalizar_Com_Sucesso",
      "Parameters": {
        "Name": "gex-buygoods-gold-crawler-prod"
      },
      "Resource": "arn:aws:states:::aws-sdk:glue:startCrawler",
      "Type": "Task"
    },
    "Falhar_Execucao": {
      "Cause": "Falha na construcao da gold BuyGoods",
      "Error": "BuyGoodsGoldExecutionFailed",
      "Type": "Fail"
    },
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Rodar_Gold_BuyGoods": {
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
      "Next": "Atualizar_Catalogo_Gold",
      "Parameters": {
        "JobName": "gex-buygoods-gold-prod"
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
