---
tipo: crawler-glue
ambiente: prod
camada: silver
database: gex_db_prod_silver
ultimo_status: SUCCEEDED
tags: [datalake, glue-crawler]
---

# gex-silver-clickbank-crawler-prod

> Glue Crawler · cataloga **gex_db_prod_silver** (silver · prod)

## Propriedades

| Propriedade | Valor |
|---|---|
| Database de destino | [[gex_db_prod_silver/00-Indice|gex_db_prod_silver]] |
| Camada / Ambiente | silver / prod |
| Estado | READY |
| Último resultado | SUCCEEDED |
| Schedule | — |
| Role | `gex-glue-role-prod` |

## Alvos S3 (o que ele varre)

- `s3://gex-datalake-silver-prod/gex_clickbank_physical_new/`

## Relacionados
[[00-Data-Lake]] · [[00-Orquestracao]]
