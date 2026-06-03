---
tipo: doc-amostra
plataforma: Buygoods
origem: silver_buygoods (webhook)
arquivo: amostra_webhook_buygoods.csv
colunas: 92
linhas_amostra: 100
tags: [fonte, buygoods, amostra]
---
# BuyGoods — Amostra do Webhook

> Referência da amostra **amostra_webhook_buygoods.csv** (92 colunas, 100 linhas).
> O CSV cru fica nesta mesma pasta. Origem da silver: **silver_buygoods (webhook)**.

## action_type observados na amostra
| action_type | linhas |
|---|---:|
| abandon | 67 |
| newcustomer | 11 |
| refund | 9 |
| cancel | 8 |
| neworder | 5 |

## Colunas (ordem do CSV)
| # | coluna |
|---:|---|
| 1 | dt_proc |
| 2 | received_at |
| 3 | account_id |
| 4 | action_type |
| 5 | aff_commission |
| 6 | aff_id |
| 7 | aff_name |
| 8 | affiliate_id |
| 9 | affiliate_name |
| 10 | amount_in_currency |
| 11 | chargeback_fee |
| 12 | charges_count |
| 13 | checkout_conversion_rate |
| 14 | coupon_discount |
| 15 | customer_emailaddress |
| 16 | customer_name |
| 17 | date_canceled |
| 18 | date_chargedback |
| 19 | date_fulfillment |
| 20 | date_refunded |
| 21 | external_order_id |
| 22 | external_order_id2 |
| 23 | external_order_id3 |
| 24 | external_order_id4 |
| 25 | external_order_id5 |
| 26 | flag_frontend |
| 27 | flag_sms_sent |
| 28 | flag_upsell |
| 29 | fulfillmentid |
| 30 | funnel_codename |
| 31 | funnel_step |
| 32 | is_free |
| 33 | is_test |
| 34 | lead_ticket_id |
| 35 | merchant_commission |
| 36 | name |
| 37 | net_commissions |
| 38 | net_sales |
| 39 | order_date |
| 40 | order_date_eu |
| 41 | order_date_time |
| 42 | order_details |
| 43 | order_id |
| 44 | order_id_global |
| 45 | orders_amount_client |
| 46 | payment_status |
| 47 | payment_terms |
| 48 | product |
| 49 | product_codename |
| 50 | product_id |
| 51 | product_name |
| 52 | product_price |
| 53 | product_quantity |
| 54 | product_subtotal |
| 55 | product_url_encoded |
| 56 | referrer |
| 57 | referrer_self |
| 58 | referrer_sid |
| 59 | referrer_url |
| 60 | refund_amount |
| 61 | refund_rate |
| 62 | register_id |
| 63 | rr_createdate |
| 64 | sessid2 |
| 65 | shipping_cost_total |
| 66 | shipping_status |
| 67 | sid |
| 68 | sid2 |
| 69 | sku |
| 70 | state |
| 71 | storecheckedoutcarts_id |
| 72 | taxes |
| 73 | tid |
| 74 | token |
| 75 | token_ipn |
| 76 | total |
| 77 | total_amount_charged |
| 78 | total_amount_charged_in_currency |
| 79 | total_clean |
| 80 | total_collected |
| 81 | total_comma |
| 82 | total_outstanding |
| 83 | tracking_redirect |
| 84 | traffic_source |
| 85 | type |
| 86 | user_id |
| 87 | vid1 |
| 88 | vid2 |
| 89 | vid3 |
| 90 | was_canceled |
| 91 | was_fulfilled |
| 92 | zip |

## Exemplo de 1 registro (neworder) — campos não-vazios
| coluna | valor |
|---|---|
| dt_proc | 2026-06-01 |
| received_at | 2026-06-01T16:30:16.882993 |
| account_id | 12340 |
| action_type | neworder |
| aff_commission | 240.00 |
| aff_id | 1091 |
| aff_name | Neha Singh |
| amount_in_currency | $314.58 |
| customer_emailaddress | anne.seibert3@gmail.com |
| customer_name | Anne seibert |
| flag_frontend | 1 |
| merchant_commission | 24.59 |
| name | Anne seibert |
| order_date | June  1, 2026 |
| order_date_eu | 01/06/2026 |
| order_date_time | June  1, 2026, 12:30 PM |
| order_details | Memopezil 6 Bottles |
| order_id | 779790 |
| order_id_global | A2KZI6JP |
| payment_status | Completed |
| product | Physical Product: Memopezil 6 Bottles |
| product_codename | PP_MMP6UNITS_AFF |
| product_id | 43 |
| product_name | Memopezil 6 Bottles |
| product_price | 294.00 |
| product_quantity | 1 |
| product_subtotal | 294.00 |
| referrer_self | 5570 |
| referrer_sid | ragmem\|f8bd78504eb64052babe4dcdebfa49c8 |
| referrer_url | 1700 |
| register_id | 638350 |
| rr_createdate | 2026-06-01 12:30:04 |
| sessid2 | sessid20260601151338474 |
| shipping_status | Shipping request not sent |
| sid | ragmem |
| sid2 | f8bd78504eb64052babe4dcdebfa49c8 |
| sku | MMP6UNITS |
| state | Georgia |
| storecheckedoutcarts_id | 282322 |
| taxes | 20.58 |
| token | 853b44fdde0f6b086e2b22ce23e21dac |
| token_ipn | 8c260f3a950f85ecf1b81ddc00ce7fc8 |
| total | $314.58 |
| total_amount_charged | 294 |
| total_clean | 314.58 |
| total_comma | $314.58 |
| user_id | 355650 |
| zip | 30519 |
