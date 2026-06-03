---
tipo: tabela-datalake
database: gex_db_develop_bronze
ambiente: develop
camada: bronze
formato: parquet
colunas: 29
tags: [datalake, bronze, develop]
---

# tb_bronze_clickbank_vendas_old

> `gex_db_develop_bronze` · camada **bronze** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_develop_bronze |
| Camada | bronze |
| Ambiente | develop |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-develop/clickbank/clickbank_vendas_old/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 29 |
| Atualizada em | 2026-04-02 15:26:17-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | accountamount | string |
| 2 | affi | string |
| 3 | amount | string |
| 4 | country | string |
| 5 | currency | string |
| 6 | customercontactinfo | array<struct<field:string,value:string>> |
| 7 | customerdisplayname | string |
| 8 | customerrefundablestate | string |
| 9 | date | string |
| 10 | email | string |
| 11 | firstname | string |
| 12 | futurepayments | string |
| 13 | item | string |
| 14 | lastname | string |
| 15 | nextpaymentdate | string |
| 16 | physical | string |
| 17 | pmttype | string |
| 18 | processedpayments | string |
| 19 | promo | string |
| 20 | rebillamount | string |
| 21 | receipt | string |
| 22 | recurring | string |
| 23 | role | string |
| 24 | site | string |
| 25 | state | string |
| 26 | status | string |
| 27 | title | string |
| 28 | txntype | string |
| 29 | zip | string |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
