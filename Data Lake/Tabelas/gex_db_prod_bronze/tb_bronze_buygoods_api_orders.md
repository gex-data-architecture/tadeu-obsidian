---
tipo: tabela-datalake
database: gex_db_prod_bronze
ambiente: prod
camada: bronze
formato: parquet
colunas: 142
tags: [datalake, bronze, prod]
---

# tb_bronze_buygoods_api_orders

> `gex_db_prod_bronze` · camada **bronze** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Database | gex_db_prod_bronze |
| Camada | bronze |
| Ambiente | prod |
| Formato | parquet |
| Location (S3) | `s3://gex-datalake-bronze-prod/buygoods_api/orders/` |
| Tipo | EXTERNAL_TABLE |
| Partições | dt_proc |
| Nº colunas | 142 |
| Atualizada em | 2026-05-28 20:53:35-03:00 |

## Colunas

| # | Coluna | Tipo |
|---|---|---|
| 1 | account_id | string |
| 2 | storecheckedoutcarts_id | string |
| 3 | order_id | string |
| 4 | order_id_global | string |
| 5 | user_id | string |
| 6 | register_id | string |
| 7 | sessid2 | string |
| 8 | action_type | string |
| 9 | rr_createdate | string |
| 10 | order_date | string |
| 11 | order_date_time | string |
| 12 | order_date_eu | string |
| 13 | name | string |
| 14 | address | string |
| 15 | city | string |
| 16 | state | string |
| 17 | country | string |
| 18 | zip | string |
| 19 | country_2letter | string |
| 20 | comments | string |
| 21 | order_details | string |
| 22 | lang | string |
| 23 | is_test | string |
| 24 | is_free | string |
| 25 | was_fulfilled | string |
| 26 | date_fulfillment | string |
| 27 | was_canceled | string |
| 28 | date_canceled | string |
| 29 | cancel_reason | string |
| 30 | was_refunded | string |
| 31 | date_refunded | string |
| 32 | refund_amount | string |
| 33 | was_charged_back | string |
| 34 | chargeback_fee | string |
| 35 | customer_firstname | string |
| 36 | customer_lastname | string |
| 37 | customer_name | string |
| 38 | customer_emailaddress | string |
| 39 | customer_phone | string |
| 40 | customer_country | string |
| 41 | customer_zip | string |
| 42 | customer_state | string |
| 43 | customer_city | string |
| 44 | billing_firstname | string |
| 45 | billing_lastname | string |
| 46 | billing_country | string |
| 47 | billing_state | string |
| 48 | billing_address | string |
| 49 | billing_zip | string |
| 50 | billing_city | string |
| 51 | payment_method | string |
| 52 | payment_cardtype | string |
| 53 | payment_cardlast4 | string |
| 54 | hidden_cardnumber | string |
| 55 | payment_status | string |
| 56 | total | string |
| 57 | total_clean | string |
| 58 | total_comma | string |
| 59 | total_collected | string |
| 60 | total_outstanding | string |
| 61 | total_amount_charged | string |
| 62 | total_amount_charged_in_currency | string |
| 63 | amount_in_currency | string |
| 64 | currency | string |
| 65 | charges_count | string |
| 66 | taxes | string |
| 67 | cogs | string |
| 68 | coupon_discount | string |
| 69 | accrual_total | string |
| 70 | merchant_commission | string |
| 71 | aff_id | string |
| 72 | aff_name | string |
| 73 | aff_commission | string |
| 74 | checkout_conversion_rate | string |
| 75 | orders_amount_client | string |
| 76 | refund_rate | string |
| 77 | net_commissions | string |
| 78 | avg_customer | string |
| 79 | net_sales | string |
| 80 | product_id | string |
| 81 | product_codename | string |
| 82 | product_name | string |
| 83 | product | string |
| 84 | product_price | string |
| 85 | product_quantity | string |
| 86 | product_subtotal | string |
| 87 | product_url_encoded | string |
| 88 | sku | string |
| 89 | picture_thumbnail | string |
| 90 | flag_frontend | string |
| 91 | flag_autofulfill | string |
| 92 | shipping_method | string |
| 93 | shipping_cost | string |
| 94 | shipping_cost_total | string |
| 95 | shipping_name | string |
| 96 | shipping_address | string |
| 97 | shipping_city | string |
| 98 | shipping_state | string |
| 99 | shipping_country | string |
| 100 | shipping_zip | string |
| 101 | shipping_tracking_id | string |
| 102 | shipping_status | string |
| 103 | fulfillmentid | string |
| 104 | external_order_id | string |
| 105 | external_order_id2 | string |
| 106 | external_order_id3 | string |
| 107 | external_order_id4 | string |
| 108 | external_order_id5 | string |
| 109 | referrer_url | string |
| 110 | referrer_sid | string |
| 111 | referrer_self | string |
| 112 | subid | string |
| 113 | subid2 | string |
| 114 | subid3 | string |
| 115 | subid4 | string |
| 116 | subid5 | string |
| 117 | sid | string |
| 118 | sid2 | string |
| 119 | traffic_source | string |
| 120 | vid1 | string |
| 121 | vid2 | string |
| 122 | vid3 | string |
| 123 | funnel_codename | string |
| 124 | funnel_step | string |
| 125 | ipaddress | string |
| 126 | browser_user_agent | string |
| 127 | token | string |
| 128 | token_ipn | string |
| 129 | help_token | string |
| 130 | buy_url | string |
| 131 | payment_terms | string |
| 132 | flag_sms_sent | string |
| 133 | flag_upsell | string |
| 134 | sale_saved_agent | string |
| 135 | sale_saved_date | string |
| 136 | phone_helpgrid | string |
| 137 | _account_id | string |
| 138 | _account_name | string |
| 139 | _date_from | string |
| 140 | _date_to | string |
| 141 | _extracted_at | string |
| 142 | _run_id | string |

## Chaves de partição

- `dt_proc` (string)

## Relacionados
[[00-Data-Lake]]
