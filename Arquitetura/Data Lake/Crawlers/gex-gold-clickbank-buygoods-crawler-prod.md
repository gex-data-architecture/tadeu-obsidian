---
tipo: crawler-glue
ambiente: prod
camada: gold
database: gex_db_prod_gold
ultimo_status: SUCCEEDED
tags: [datalake, glue-crawler]
---

# gex-gold-clickbank-buygoods-crawler-prod

> Glue Crawler · cataloga **gex_db_prod_gold** (gold · prod)

## Propriedades

| Propriedade | Valor |
|---|---|
| Database de destino | [[gex_db_prod_gold/00-Indice|gex_db_prod_gold]] |
| Camada / Ambiente | gold / prod |
| Estado | READY |
| Último resultado | SUCCEEDED |
| Schedule | — |
| Role | `gex-glue-role-prod` |

## Alvos S3 (o que ele varre)

- `s3://gex-datalake-gold-prod/gex_gold_clickbank_buygoods/`

## Relacionados
[[00-Data-Lake]] · [[00-Orquestracao]]
