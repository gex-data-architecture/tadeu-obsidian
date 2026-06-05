---
tipo: crawler-glue
ambiente: develop
camada: bronze
database: gex_db_develop_bronze
ultimo_status: SUCCEEDED
tags: [datalake, glue-crawler]
---

# gex-bronze-crawler-develop

> Glue Crawler · cataloga **gex_db_develop_bronze** (bronze · develop)

## Propriedades

| Propriedade | Valor |
|---|---|
| Database de destino | [[gex_db_develop_bronze/00-Indice|gex_db_develop_bronze]] |
| Camada / Ambiente | bronze / develop |
| Estado | READY |
| Último resultado | SUCCEEDED |
| Schedule | — |
| Role | `gex-glue-role-develop` |

## Alvos S3 (o que ele varre)

- `s3://gex-datalake-bronze-develop/mysql_data/gross_recovery_target/`
- `s3://gex-datalake-bronze-develop/mysql_data/sms_costs/`
- `s3://gex-datalake-bronze-develop/mysql_data/clickbank_fee_rates/`
- `s3://gex-datalake-bronze-develop/mysql_data/clickbank_internal_affiliates/`
- `s3://gex-datalake-bronze-develop/mysql_data/clickbank_products/`
- `s3://gex-datalake-bronze-develop/mysql_data/exchange_rates/`
- `s3://gex-datalake-bronze-develop/mysql_data/general_product_costs/`
- `s3://gex-datalake-bronze-develop/clickbank/clickbank_vendas_new/`
- `s3://gex-datalake-bronze-develop/clickbank/clickbank_vendas_old/`
- `s3://gex-datalake-bronze-develop/buygoods/`
- `s3://gex-datalake-bronze-develop/mysql_data/call_center_sales/`
- `s3://gex-datalake-bronze-develop/mysql_data/unified_lead_events_new/`

## Relacionados
[[00-Data-Lake]] · [[00-Orquestracao]]
