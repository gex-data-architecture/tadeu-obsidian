---
tipo: step-function
ambiente: prod
sfn_type: STANDARD
ultima_execucao: 2026-06-12 10:00
ultimo_estado: FAILED
tags: [datalake, step-function, orquestracao]
---

# gex-gold-clickbank-buygoods-prod

> Step Function (orquestração) · ambiente **prod** · tipo STANDARD

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | STANDARD |
| Role | `arn:aws:iam::406933028738:role/gex-sfn-role-prod` |
| Criada | 2026-06-10 10:55:11.318000-03:00 |

## Fluxo (passo a passo do ASL)

> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).

- ▶️ job [[gex-gold-clickbank-buygoods-prod]]
- 🕷️ crawler [[gex-gold-clickbank-buygoods-crawler-prod]]
- ✅ fim (sucesso)

## Encadeamento (EventBridge)

**Disparada quando:**
- job [[gex-buygoods-gold-prod]] = `SUCCEEDED` (via regra EventBridge) ⟶ origem provável: [[gex-buygoods-gold-prod]]

**Ao terminar, dispara:**
- quando job [[gex-gold-clickbank-buygoods-prod]] conclui `SUCCEEDED` ⟶ inicia [[gex-affiliate-nutra-prod]]

## Dispara (alvos)

- **Jobs:** [[gex-gold-clickbank-buygoods-prod]]
- **Crawlers:** [[gex-gold-clickbank-buygoods-crawler-prod]]
- **SFN aninhadas:** —

## Últimas execuções

> 8 mais recentes (read-only via `list_executions`).

| Início | Estado |
|---|---|
| 2026-06-12 10:00 | FAILED |
| 2026-06-12 07:59 | FAILED |
| 2026-06-12 06:03 | FAILED |
| 2026-06-12 04:01 | FAILED |
| 2026-06-12 01:59 | FAILED |
| 2026-06-11 23:58 | FAILED |
| 2026-06-11 21:59 | FAILED |
| 2026-06-11 20:00 | FAILED |

## Definição (Amazon States Language)

````json
{
  "StartAt": "Rodar_Gold_Combinada",
  "States": {
    "Atualizar_Catalogo_Gold_Combinada": {
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
        "Name": "gex-gold-clickbank-buygoods-crawler-prod"
      },
      "Resource": "arn:aws:states:::aws-sdk:glue:startCrawler",
      "Type": "Task"
    },
    "Falhar_Execucao": {
      "Cause": "Falha na gold combinada clickbank+buygoods",
      "Error": "GoldClickbankBuygoodsExecutionFailed",
      "Type": "Fail"
    },
    "Finalizar_Com_Sucesso": {
      "Type": "Succeed"
    },
    "Rodar_Gold_Combinada": {
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
      "Next": "Atualizar_Catalogo_Gold_Combinada",
      "Parameters": {
        "JobName": "gex-gold-clickbank-buygoods-prod"
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
