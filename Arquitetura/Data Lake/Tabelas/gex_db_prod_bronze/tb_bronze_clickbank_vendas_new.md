---
tipo: tabela-datalake
database: gex_db_prod_bronze
ambiente: prod
camada: bronze
formato: parquet
colunas: 92
tags: [datalake, bronze, prod]
---

# tb_bronze_clickbank_vendas_new

> `gex_db_prod_bronze` · camada **bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_bronze |
| Camada | bronze |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-prod/clickbank/clickbank_vendas_new/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 92 |
| Atualizada em | 2026-06-12 09:36:21-03:00 |

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
| 14 | billingpostalcode | string |
| 15 | billingstate | string |
| 16 | browser | string |
| 17 | browserlang | string |
| 18 | browserversion | string |
| 19 | campaign | string |
| 20 | cbpage | string |
| 21 | city | string |
| 22 | clickid | string |
| 23 | clicktimestamp | string |
| 24 | commissiontype | string |
| 25 | contactid | string |
| 26 | country | string |
| 27 | couponid | string |
| 28 | creative | string |
| 29 | customertax | double |
| 30 | declinedmarketing | string |
| 31 | devicebrand | string |
| 32 | devicemodel | string |
| 33 | devicetype | string |
| 34 | extclid | string |
| 35 | fbclid | string |
| 36 | foreignexchangefee | double |
| 37 | id | bigint |
| 38 | itemquantity | bigint |
| 39 | jvaffiliateearnings | double |
| 40 | jvsellerearnings | double |
| 41 | lineitemtype | string |
| 42 | offer | string |
| 43 | orderformtemplate | string |
| 44 | ordernumber | string |
| 45 | ordertype | string |
| 46 | os | string |
| 47 | osversion | string |
| 48 | paymentmethod | string |
| 49 | platformfee | double |
| 50 | primaryaffiliate | string |
| 51 | primaryseller | string |
| 52 | productdiscount | double |
| 53 | productitemnumber | string |
| 54 | productpurchaseprice | double |
| 55 | receiptnumber | string |
| 56 | region | string |
| 57 | roleontransaction | string |
| 58 | salesaccount | string |
| 59 | sellerearnings | double |
| 60 | sellervariables | string |
| 61 | shippingandhandling | double |
| 62 | state | string |
| 63 | trackingid | string |
| 64 | trackingtype | string |
| 65 | trafficsource | string |
| 66 | traffictype | string |
| 67 | transactionamount | double |
| 68 | transactiondate | string |
| 69 | transactiontime | string |
| 70 | transactiontype | string |
| 71 | uniqueaffsub1 | string |
| 72 | uniqueaffsub2 | string |
| 73 | uniqueaffsub3 | string |
| 74 | uniqueaffsub4 | string |
| 75 | uniqueaffsub5 | string |
| 76 | upsellflowid | string |
| 77 | upsellpath | string |
| 78 | useragent | string |
| 79 | yourearnings | double |
| 80 | account_owner | string |
| 81 | billingcustomerphone | string |
| 82 | parent_transaction_receipt | string |
| 83 | retrycount | bigint |
| 84 | shippingcity | string |
| 85 | shippingcountry | string |
| 86 | shippingcustomeremail | string |
| 87 | shippingcustomerfirstname | string |
| 88 | shippingcustomerlastname | string |
| 89 | shippingcustomerphone | string |
| 90 | shippingpostalcode | string |
| 91 | shippingstate | string |
| 92 | upsellparentreceipt | string |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
