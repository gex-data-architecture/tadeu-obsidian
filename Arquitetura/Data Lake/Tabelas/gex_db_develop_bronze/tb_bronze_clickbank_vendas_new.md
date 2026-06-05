---
tipo: tabela-datalake
database: gex_db_develop_bronze
ambiente: develop
camada: bronze
formato: parquet
colunas: 90
tags: [datalake, bronze, develop]
---

# tb_bronze_clickbank_vendas_new

> `gex_db_develop_bronze` · camada **bronze** · ambiente **develop**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_develop_bronze |
| Camada | bronze |
| Ambiente | develop |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-develop/clickbank/clickbank_vendas_new/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 90 |
| Atualizada em | 2026-04-20 14:03:09-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | ad | string |
| 2 | adgroup | string |
| 3 | affsub1 | string |
| 4 | affsub2 | string |
| 5 | affsub3 | string |
| 6 | affsub4 | string |
| 7 | affsub5 | string |
| 8 | affiliateearnings | double |
| 9 | billingcity | string |
| 10 | billingcountry | string |
| 11 | billingcustomeremail | string |
| 12 | billingcustomerfirstname | string |
| 13 | billingcustomerlastname | string |
| 14 | billingcustomerphone | string |
| 15 | billingpostalcode | string |
| 16 | billingstate | string |
| 17 | browser | string |
| 18 | browserlang | string |
| 19 | browserversion | string |
| 20 | campaign | string |
| 21 | cbpage | string |
| 22 | city | string |
| 23 | clickid | string |
| 24 | clicktimestamp | string |
| 25 | commissiontype | string |
| 26 | contactid | string |
| 27 | country | string |
| 28 | couponid | string |
| 29 | creative | string |
| 30 | customertax | double |
| 31 | declinedmarketing | string |
| 32 | devicebrand | string |
| 33 | devicemodel | string |
| 34 | devicetype | string |
| 35 | extclid | string |
| 36 | fbclid | string |
| 37 | foreignexchangefee | double |
| 38 | id | bigint |
| 39 | itemquantity | bigint |
| 40 | jvaffiliateearnings | double |
| 41 | jvsellerearnings | double |
| 42 | lineitemtype | string |
| 43 | offer | string |
| 44 | orderformtemplate | string |
| 45 | os | string |
| 46 | osversion | string |
| 47 | parent_transaction_receipt | string |
| 48 | paymentmethod | string |
| 49 | platformfee | double |
| 50 | primaryaffiliate | string |
| 51 | primaryseller | string |
| 52 | productdiscount | double |
| 53 | productitemnumber | string |
| 54 | productpurchaseprice | double |
| 55 | receiptnumber | string |
| 56 | region | string |
| 57 | retrycount | bigint |
| 58 | roleontransaction | string |
| 59 | salesaccount | string |
| 60 | sellerearnings | double |
| 61 | sellervariables | string |
| 62 | shippingandhandling | double |
| 63 | shippingcity | string |
| 64 | shippingcountry | string |
| 65 | shippingcustomeremail | string |
| 66 | shippingcustomerfirstname | string |
| 67 | shippingcustomerlastname | string |
| 68 | shippingcustomerphone | string |
| 69 | shippingpostalcode | string |
| 70 | shippingstate | string |
| 71 | state | string |
| 72 | trackingid | string |
| 73 | trackingtype | string |
| 74 | trafficsource | string |
| 75 | traffictype | string |
| 76 | transactionamount | double |
| 77 | transactiondate | string |
| 78 | transactiontime | string |
| 79 | transactiontype | string |
| 80 | uniqueaffsub1 | string |
| 81 | uniqueaffsub2 | string |
| 82 | uniqueaffsub3 | string |
| 83 | uniqueaffsub4 | string |
| 84 | uniqueaffsub5 | string |
| 85 | upsellflowid | string |
| 86 | upsellparentreceipt | string |
| 87 | upsellpath | string |
| 88 | useragent | string |
| 89 | yourearnings | double |
| 90 | account_owner | string |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
