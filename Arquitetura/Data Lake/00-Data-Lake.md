---
tipo: indice-datalake
gerado_por: skill/catalogo-datalake
tags: [datalake, indice]
---
# 🗄️ Data Lake — Catálogo (AWS Glue)

> Gerado da AWS Glue + Step Functions (conta 406933028738, `us-east-1`, perfil `buygoods`). **Não editar à mão** — regerável.
> **40 tabelas** em 7 databases · **63 jobs** ETL · **20 Step Functions** · **17 crawlers** · **49 agendamentos**.
> Arquitetura **medallion**: `landing → bronze → silver → gold → MySQL` (develop e prod).
> Orquestração, cadeias e **agendamentos** (cron/rate): **[[00-Orquestracao]]**.

## Databases (Glue Data Catalog)

| Database | Ambiente | Camada | Tabelas |
|---|---|---|---|
| `default` |  |  | 0 |
| `gex_db_develop_bronze` | develop | bronze | 15 |
| `gex_db_develop_gold` | develop | gold | 0 |
| `gex_db_develop_silver` | develop | silver | 3 |
| `gex_db_prod_bronze` | prod | bronze | 16 |
| `gex_db_prod_gold` | prod | gold | 3 |
| `gex_db_prod_silver` | prod | silver | 3 |

## Tabelas por database

### `gex_db_develop_bronze`
- [[gex_db_develop_bronze/buygoods_orders|buygoods_orders]]
- [[gex_db_develop_bronze/tb_bronze_buygoods|tb_bronze_buygoods]]
- [[gex_db_develop_bronze/tb_bronze_buygoods_api_orders|tb_bronze_buygoods_api_orders]]
- [[gex_db_develop_bronze/tb_bronze_call_center_sales|tb_bronze_call_center_sales]]
- [[gex_db_develop_bronze/tb_bronze_clickbank_fee_rates|tb_bronze_clickbank_fee_rates]]
- [[gex_db_develop_bronze/tb_bronze_clickbank_internal_affiliates|tb_bronze_clickbank_internal_affiliates]]
- [[gex_db_develop_bronze/tb_bronze_clickbank_products|tb_bronze_clickbank_products]]
- [[gex_db_develop_bronze/tb_bronze_clickbank_vendas|tb_bronze_clickbank_vendas]]
- [[gex_db_develop_bronze/tb_bronze_clickbank_vendas_new|tb_bronze_clickbank_vendas_new]]
- [[gex_db_develop_bronze/tb_bronze_clickbank_vendas_old|tb_bronze_clickbank_vendas_old]]
- [[gex_db_develop_bronze/tb_bronze_exchange_rates|tb_bronze_exchange_rates]]
- [[gex_db_develop_bronze/tb_bronze_general_product_costs|tb_bronze_general_product_costs]]
- [[gex_db_develop_bronze/tb_bronze_gross_recovery_target|tb_bronze_gross_recovery_target]]
- [[gex_db_develop_bronze/tb_bronze_sms_costs|tb_bronze_sms_costs]]
- [[gex_db_develop_bronze/tb_bronze_unified_lead_events_new|tb_bronze_unified_lead_events_new]]

### `gex_db_develop_silver`
- [[gex_db_develop_silver/buygoods_orders|buygoods_orders]]
- [[gex_db_develop_silver/tb_buygoods_physical_new|tb_buygoods_physical_new]]
- [[gex_db_develop_silver/tb_silver_gex_datalake_silver_develop|tb_silver_gex_datalake_silver_develop]]

### `gex_db_prod_bronze`
- [[gex_db_prod_bronze/tb_bronze_buygoods|tb_bronze_buygoods]]
- [[gex_db_prod_bronze/tb_bronze_buygoods_api_orders|tb_bronze_buygoods_api_orders]]
- [[gex_db_prod_bronze/tb_bronze_buygoods_internal_affiliates|tb_bronze_buygoods_internal_affiliates]]
- [[gex_db_prod_bronze/tb_bronze_buygoods_products|tb_bronze_buygoods_products]]
- [[gex_db_prod_bronze/tb_bronze_call_center_sales|tb_bronze_call_center_sales]]
- [[gex_db_prod_bronze/tb_bronze_clickbank_fee_rates|tb_bronze_clickbank_fee_rates]]
- [[gex_db_prod_bronze/tb_bronze_clickbank_internal_affiliates|tb_bronze_clickbank_internal_affiliates]]
- [[gex_db_prod_bronze/tb_bronze_clickbank_products|tb_bronze_clickbank_products]]
- [[gex_db_prod_bronze/tb_bronze_clickbank_vendas|tb_bronze_clickbank_vendas]]
- [[gex_db_prod_bronze/tb_bronze_clickbank_vendas_new|tb_bronze_clickbank_vendas_new]]
- [[gex_db_prod_bronze/tb_bronze_clickbank_vendas_old|tb_bronze_clickbank_vendas_old]]
- [[gex_db_prod_bronze/tb_bronze_exchange_rates|tb_bronze_exchange_rates]]
- [[gex_db_prod_bronze/tb_bronze_general_product_costs|tb_bronze_general_product_costs]]
- [[gex_db_prod_bronze/tb_bronze_gross_recovery_target|tb_bronze_gross_recovery_target]]
- [[gex_db_prod_bronze/tb_bronze_sms_costs|tb_bronze_sms_costs]]
- [[gex_db_prod_bronze/tb_bronze_unified_lead_events_new|tb_bronze_unified_lead_events_new]]

### `gex_db_prod_gold`
- [[gex_db_prod_gold/tb_gex_dashboard_channels_marketing|tb_gex_dashboard_channels_marketing]]
- [[gex_db_prod_gold/tb_gex_gold_buygoods|tb_gex_gold_buygoods]]
- [[gex_db_prod_gold/tb_gex_gold_clickbank|tb_gex_gold_clickbank]]

### `gex_db_prod_silver`
- [[gex_db_prod_silver/tb_buygoods_physical_new|tb_buygoods_physical_new]]
- [[gex_db_prod_silver/tb_gex_clickbank_physical_new|tb_gex_clickbank_physical_new]]
- [[gex_db_prod_silver/tb_silver_buygoods_orders|tb_silver_buygoods_orders]]

## Jobs ETL por fluxo

### MySQL → Bronze
- [[gex-mysql-to-bronze-develop]]
- [[gex-mysql-to-bronze-prod]]
- [[mysql-to-bronze-buygoods_internal_affiliates-prod]]
- [[mysql-to-bronze-buygoods_products-prod]]
- [[mysql-to-bronze-clickbank_fee_rates-develop]]
- [[mysql-to-bronze-clickbank_fee_rates-prod]]
- [[mysql-to-bronze-clickbank_internal_affiliates-develop]]
- [[mysql-to-bronze-clickbank_internal_affiliates-prod]]
- [[mysql-to-bronze-clickbank_products-develop]]
- [[mysql-to-bronze-clickbank_products-prod]]
- [[mysql-to-bronze-exchange_rates-develop]]
- [[mysql-to-bronze-exchange_rates-prod]]
- [[mysql-to-bronze-general_product_costs-develop]]
- [[mysql-to-bronze-general_product_costs-prod]]
- [[mysql-to-bronze-gross_recovery_target-develop]]
- [[mysql-to-bronze-gross_recovery_target-prod]]
- [[mysql-to-bronze-sms_costs-develop]]
- [[mysql-to-bronze-sms_costs-prod]]

### Landing → Bronze
- [[gex-landing-to-bronze-buygoods-develop]]
- [[gex-landing-to-bronze-buygoods-polling-develop]]
- [[gex-landing-to-bronze-buygoods-polling-prod]]
- [[gex-landing-to-bronze-buygoods-prod]]
- [[gex-landing-to-bronze-develop]]
- [[gex-landing-to-bronze-new-develop]]
- [[gex-landing-to-bronze-new-prod]]
- [[gex-landing-to-bronze-prod]]

### Bronze → Silver
- [[bronze-to-silver-buygoods-develop]]
- [[bronze-to-silver-buygoods-prod]]
- [[bronze-to-silver-clickbank-develop]]
- [[gex-bronze-to-silver-prod]]
- [[gex-buygoods-orders-bronze-to-silver-develop]]
- [[gex-buygoods-orders-bronze-to-silver-prod]]

### Silver → Gold
- [[gex-silver-to-gold-prod]]
- [[silver-to-gold-clickbank-develop]]

### Gold/Silver → MySQL
- [[buygoods_silver_to_mysql]]
- [[gex-buygoods-orders-silver-to-mysql-develop]]
- [[gex-buygoods-orders-silver-to-mysql-prod]]
- [[gex-buygoods-unified-to-mysql-develop]]
- [[gex-buygoods-unified-to-mysql-prod]]
- [[gold-clickbank-to-mysql-develop]]
- [[gold-clickbank-to-mysql-prod]]
- [[gold-to-mysql-channels-marketing-develop]]
- [[gold-to-mysql-channels-marketing-prod]]
- [[silver-buygoods-physical-to-mysql-prod]]
- [[silver-clickbank-physical-to-mysql-develop]]
- [[silver-clickbank-physical-to-mysql-prod]]

### Outros
- [[buygoods_bootstrap_mysql_tables]]
- [[buygoods_bronze_extract]]
- [[buygoods_bronze_to_silver]]
- [[gex-buygoods-api-convert-develop]]
- [[gex-buygoods-api-convert-prod]]
- [[gex-buygoods-api-extract-prod]]
- [[gex-buygoods-gold-develop]]
- [[gex-buygoods-gold-prod]]
- [[gex-buygoods-orders-bootstrap-mysql-develop]]
- [[gex-buygoods-orders-bootstrap-mysql-prod]]
- [[gex-buygoods-orders-extract-develop]]
- [[gex-buygoods-orders-extract-prod]]
- [[gex-docs-dev-extractor]]
- [[gex-mysql-leads-heavy-prod]]
- [[gex-silver-clickbank-dedup-oneshot]]
- [[gold-dashboard-channels-marketing-develop]]
- [[gold-dashboard-channels-marketing-prod]]

## Step Functions (orquestração)

Visão das cadeias e do grafo: **[[00-Orquestracao]]**.

### prod
- [[gex-bronze-to-silver-buygoods-prod]]
- [[gex-bronze-to-silver-clickbank-prod]]
- [[gex-buygoods-gold-prod]]
- [[gex-buygoods-unified-to-mysql-prod]]
- [[gex-clickbank-config-daily-prod]]
- [[gex-clickbank-ingestion-old-prod]]
- [[gex-gold-dashboard-channels-marketing-prod]]
- [[gex-gold-to-mysql-channels-marketing-prod]]
- [[gex-mysql-leads-daily-prod]]
- [[gex-mysql-sales-hourly-prod]]
- [[gex-silver-gold-to-mysql-clickbank-prod]]
- [[gex-silver-to-gold-clickbank-prod]]
- [[gex-silver-to-mysql-buygoods-prod]]

### develop
- [[gex-clickbank-config-daily-develop]]
- [[gex-clickbank-ingestion-old-develop]]
- [[gex-gold-dashboard-channels-marketing-develop]]
- [[gex-gold-to-mysql-channels-marketing-develop]]
- [[gex-mysql-leads-daily-develop]]
- [[gex-mysql-sales-hourly-develop]]
- [[gex-silver-gold-to-mysql-clickbank-develop]]

## Crawlers (Glue)

### `gex_db_develop_bronze`
- [[gex-bronze-buygoods-api-crawler-develop]]
- [[gex-bronze-crawler-develop]]

### `gex_db_develop_gold`
- [[gex-buygoods-gold-crawler-develop]]
- [[gex-gold-crawler-develop]]
- [[gex-gold-dashboard-channels-marketing-crawler-develop]]

### `gex_db_develop_silver`
- [[gex-silver-buygoods-crawler-develop]]
- [[gex-silver-clickbank-crawler-develop]]
- [[gex-silver-crawler-develop]]

### `gex_db_prod_bronze`
- [[gex-bronze-buygoods-api-crawler-prod]]
- [[gex-bronze-crawler-prod]]

### `gex_db_prod_gold`
- [[gex-buygoods-gold-crawler-prod]]
- [[gex-gold-crawler-prod]]
- [[gex-gold-dashboard-channels-marketing-crawler-prod]]

### `gex_db_prod_silver`
- [[gex-buygoods-orders-silver-crawler-prod]]
- [[gex-silver-buygoods-crawler-prod]]
- [[gex-silver-clickbank-crawler-prod]]
- [[gex-silver-crawler-prod]]

## Agendamentos (EventBridge)

Horários (UTC), expressões e alvos: **[[00-Orquestracao]]**.

- 🟢 `cb-ingestion-d1-prod` — todo dia a cada 15 min UTC → gex-clickbank-poller-new-prod
- 🟢 `cb-ingestion-d60-cgbk-prod` — todo dia às 00:30 e 12:30 UTC → gex-clickbank-poller-new-prod
- 🟢 `cb-ingestion-d60-rfnd-prod` — todo dia às 00:00 e 12:00 UTC → gex-clickbank-poller-new-prod
- 🟢 `cb-ingestion-d90-audit-prod` — todo dia às 04:00 UTC → gex-clickbank-poller-new-prod
- 🟢 `gex-bronze-to-silver-15min-prod` — todo dia a cada 2h (no min 05) UTC → [[gex-bronze-to-silver-clickbank-prod]]
- 🟢 `gex-bronze-to-silver-buygoods-2h-prod` — todo dia a cada 2h (no min 30) UTC → [[gex-bronze-to-silver-buygoods-prod]]
- 🟢 `gex-buygoods-api-polling-daily-develop` — a cada 1 day → gex-buygoods-api-polling-develop
- 🟢 `gex-clickbank-config-daily-timer-prod` — todo dia às 01:00 UTC → [[gex-clickbank-config-daily-prod]]
- 🟢 `gex-clickbank-glue-processing-prod` — todo dia a cada 15 min a partir do min 10 UTC → [[gex-landing-to-bronze-new-prod]]
- 🟢 `gex-docs-dev-extractor-schedule` — seg às 09:00 UTC → [[gex-docs-dev-extractor]]
- 🟢 `gex-mysql-gross-recovery-timer-prod` — todo dia às 05:30 UTC → [[mysql-to-bronze-gross_recovery_target-prod]]
- 🟢 `gex-mysql-leads-hourly-timer-prod` — a cada 1 hour → [[gex-mysql-leads-daily-prod]]
- 🟢 `gex-mysql-sales-daily-timer-prod` — todo dia às 02:00 UTC → [[gex-mysql-sales-hourly-prod]]
- 🟢 `gex-mysql-sms-costs-timer-prod` — todo dia às 05:15 UTC → [[mysql-to-bronze-sms_costs-prod]]
- 🟢 `gex-silver-gold-to-mysql-clickbank-15min-develop` — todo dia a cada 15 min a partir do min 20 UTC → [[gex-silver-gold-to-mysql-clickbank-develop]]
- 🟢 `instituto-experience-dev-cartpanda_physical_rabbitmq-rule-1` — a cada 5 minutes → instituto-experience-dev-cartpanda_physical_rabbitmq
- 🟢 `instituto-experience-dev-clickbank_physical-rule-1` — a cada 20 minutes → instituto-experience-dev-clickbank_physical
- 🟢 `instituto-experience-dev-clickbank_physical_chargeback-rule-1` — a cada 90 minutes → instituto-experience-dev-clickbank_physical_chargeback
- 🟢 `instituto-experience-dev-clickbank_physical_refund-rule-1` — a cada 1 hour → instituto-experience-dev-clickbank_physical_refund
- 🟢 `instituto-experience-dev-clickbank_physical_sale-rule-1` — a cada 30 minutes → instituto-experience-dev-clickbank_physical_sale
- 🟢 `instituto-experience-dev-meta_ad_id_rabbitmq-rule-1` — a cada 5 minutes → instituto-experience-dev-meta_ad_id_rabbitmq
- ⚪ `cb-ingestion-d1-develop` — todo dia a cada 15 min UTC → gex-clickbank-poller-new-develop
- ⚪ `cb-ingestion-d60-cgbk-develop` — todo dia às 00:30 e 12:30 UTC → gex-clickbank-poller-new-develop
- ⚪ `cb-ingestion-d60-rfnd-develop` — todo dia às 00:00 e 12:00 UTC → gex-clickbank-poller-new-develop
- ⚪ `cb-ingestion-d90-audit-develop` — todo dia às 04:00 UTC → gex-clickbank-poller-new-develop
- ⚪ `gex-buygoods-api-polling-daily-prod` — a cada 1 day → gex-buygoods-api-polling-prod
- ⚪ `gex-clickbank-config-daily-timer-develop` — todo dia às 01:00 UTC → [[gex-clickbank-config-daily-develop]]
- ⚪ `gex-clickbank-glue-processing-develop` — todo dia a cada 15 min a partir do min 10 UTC → [[gex-landing-to-bronze-new-develop]]
- ⚪ `gex-clickbank-old-polling-all-develop` — todo dia às 03:00 UTC → gex-clickbank-poller-develop
- ⚪ `gex-clickbank-old-polling-all-prod` — todo dia às 03:00 UTC → gex-clickbank-poller-prod
- ⚪ `gex-clickbank-old-polling-chargeback-develop` — todo dia às 01:00 e 13:00 UTC → gex-clickbank-poller-develop
- ⚪ `gex-clickbank-old-polling-refund-develop` — todo dia às 01:00 e 13:00 UTC → gex-clickbank-poller-develop
- ⚪ `gex-clickbank-old-processing-develop` — todo dia às 05:00 UTC → [[gex-clickbank-ingestion-old-develop]]
- ⚪ `gex-clickbank-old-processing-prod` — todo dia às 05:00 UTC → [[gex-clickbank-ingestion-old-prod]]
- ⚪ `gex-gold-dashboard-channels-marketing-timer-develop` — todo dia a cada 15 min a partir do min 20 UTC → [[gex-gold-dashboard-channels-marketing-develop]]
- ⚪ `gex-gold-dashboard-channels-marketing-timer-prod` — todo dia a cada 15 min a partir do min 20 UTC → [[gex-gold-dashboard-channels-marketing-prod]]
- ⚪ `gex-gold-to-mysql-channels-marketing-timer-develop` — todo dia a cada 15 min a partir do min 25 UTC → [[gex-gold-to-mysql-channels-marketing-develop]]
- ⚪ `gex-gold-to-mysql-channels-marketing-timer-prod` — todo dia a cada 15 min a partir do min 25 UTC → [[gex-gold-to-mysql-channels-marketing-prod]]
- ⚪ `gex-mysql-leads-daily-timer-develop` — todo dia às 02:00 UTC → [[gex-mysql-leads-daily-develop]]
- ⚪ `gex-mysql-sales-hourly-timer-develop` — a cada 1 hour → [[gex-mysql-sales-hourly-develop]]
- ⚪ `gex-silver-gold-to-mysql-clickbank-15min-prod` — todo dia a cada 15 min a partir do min 20 UTC → [[gex-silver-gold-to-mysql-clickbank-prod]]
- ⚪ `gex-silver-to-gold-15min-prod` — todo dia a cada 15 min a partir do min 10 UTC → [[gex-silver-to-gold-clickbank-prod]]
- ⚪ `instituto-experience-dev-15287825defb2e2fce2afe501eb8b0cc-rule-1` — a cada 30 minutes → instituto-experience-dev-cartpanda_carrinhos_perdidos_instituto
- ⚪ `instituto-experience-dev-1df07fb095450bed3a2db53be9f61cae-rule-1` — a cada 30 minutes → instituto-experience-dev-cartpanda_carrinhos_perdidos_health
- ⚪ `instituto-experience-dev-1ee39b2d0769b2101104c60b656a2229-rule-1` — a cada 20 minutes → instituto-experience-dev-cartpanda_pedidos_update_instituto
- ⚪ `instituto-experience-dev-5edb102ca4b9c480aa9d38a6fcfd33f0-rule-1` — a cada 20 minutes → instituto-experience-dev-cartpanda_pedidos_update_group_health
- ⚪ `instituto-experience-dev-cartpanda_pedidos_todos-rule-1` — a cada 40 minutes → instituto-experience-dev-cartpanda_pedidos_todos
- ⚪ `instituto-experience-dev-cartpanda_physical_reembolso-rule-1` — a cada 20 minutes → instituto-experience-dev-cartpanda_physical_reembolso
- ⚪ `instituto-experience-dev-cartpanda_physical_todos-rule-1` — a cada 20 minutes → instituto-experience-dev-cartpanda_physical_todos

## Relacionados
[[00-Indice]] · [[00-Orquestracao]] · skill `catalogo-datalake` · skill `limpeza-banco`
