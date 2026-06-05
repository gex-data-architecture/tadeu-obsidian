---
tipo: crawler-glue
ambiente: prod
camada: bronze
database: gex_db_prod_bronze
ultimo_status: SUCCEEDED
tags: [datalake, glue-crawler]
---

# gex-bronze-buygoods-api-crawler-prod

> Glue Crawler · cataloga **gex_db_prod_bronze** (bronze · prod)

## Propriedades

| Propriedade | Valor |
|---|---|
| Database de destino | [[gex_db_prod_bronze/00-Indice|gex_db_prod_bronze]] |
| Camada / Ambiente | bronze / prod |
| Estado | READY |
| Último resultado | SUCCEEDED |
| Schedule | — |
| Role | `gex-glue-role-prod` |

## Alvos S3 (o que ele varre)

- `s3://gex-datalake-bronze-prod/buygoods_api/orders/`

## Relacionados
[[00-Data-Lake]] · [[00-Orquestracao]]
