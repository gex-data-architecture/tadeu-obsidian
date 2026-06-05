---
tipo: doc-tecnico
camada: silver
plataforma: Buygoods
tabela_alvo: tb_gex_buygoods_unified
fontes:
  - gex_db_prod_silver.tb_buygoods_physical_new (webhook — fonte da verdade)
  - gex_db_prod_silver.tb_silver_buygoods_orders (api — complemento)
job: gex-buygoods-unified-to-mysql-prod
versao: "1.0"
tags: [fonte, buygoods, silver, doc-tecnico]
---

# Especificação Técnica — Camada Silver (BuyGoods)

> Regras e processos para gerar a **silver unificada** do BuyGoods
> (`instituto_experience.tb_gex_buygoods_unified`), a partir da junção de **duas silvers**
> no Data Lake (Athena/S3): a **silver do webhook** (fonte da verdade) e a **silver da API**
> (complemento). Esta nota documenta as duas silvers de origem **e** a silver final.

| Campo | Valor |
|---|---|
| Camada | Silver (conformada / "fonte única da verdade" BuyGoods) |
| Tabela alvo | `instituto_experience.tb_gex_buygoods_unified` (MySQL 8) |
| Fontes (Athena/Glue, `gex_db_prod_silver`) | `tb_buygoods_physical_new` (webhook) · `tb_silver_buygoods_orders` (api) |
| Job que gera | Glue ETL **`gex-buygoods-unified-to-mysql-prod`** (script `silver_to_mysql_buygoods_unified.py`) |
| Orquestração | SFN `gex-buygoods-unified-to-mysql-prod` |
| Cadência | A cada **2h** (disparada quando o bronze→silver conclui) |
| Estratégia de escrita | **Swap atômico** (`RENAME TABLE`) — zero downtime |
| Granularidade | 1 linha por **transação** (`transaction_id`), antes da agregação por compra na Gold |
| Colunas | **62** (54 comuns + `cancel_reason` + 5 `utm_*` + `id` + `data_source`) |
| Chave de unificação | `transaction_id` (webhook tem prioridade) |
| Downstream | [[doc_gold_buygoods]] → `dashboard_gold_buygoods` / `dashboard_gold_clickbank_buygoods` |

---

## 1. Visão geral do pipeline

```
                 BuyGoods (plataforma)
            ┌──────────────┴───────────────┐
        Webhook (push, tempo real)     API (pull, histórico/backfill)
            │                               │
        bronze (raw)                    bronze (raw)
            │   gex-bronze-to-silver-buygoods-prod (a cada 2h, min 30 UTC)
            ▼                               ▼
   SILVER WEBHOOK                     SILVER API
   tb_buygoods_physical_new          tb_silver_buygoods_orders
   s3://…silver-prod/                s3://…silver-prod/
        buygoods_physical_new/            buygoods_orders/
            └──────────────┬───────────────┘
                  gex-buygoods-unified-to-mysql-prod  (job de UNIFICAÇÃO)
                  • webhook = base   • api = só transaction_id faltante
                           ▼
                  SILVER UNIFICADA  →  swap atômico
                  instituto_experience.tb_gex_buygoods_unified  (MySQL)
                           ▼
                  GOLD  (gex-buygoods-gold-prod → dashboard_gold_buygoods)
```

- As duas silvers são **lidas do S3** (parquet) pelo job de unificação e estão **catalogadas no Athena/Glue** (`gex_db_prod_silver`) pelos crawlers `gex-silver-buygoods-crawler-prod` / `gex-buygoods-orders-silver-crawler-prod` — daí "vem do Athena".
- O job de unificação roda **logo após** o `bronze-to-silver-buygoods-prod` concluir `SUCCEEDED` (encadeamento por EventBridge); o mesmo gatilho dispara também `gex-silver-to-mysql-buygoods-prod`.

---

## 2. Silver do WEBHOOK — *fonte da verdade*

| Propriedade | Valor |
|---|---|
| Tabela (Athena/Glue) | `gex_db_prod_silver.tb_buygoods_physical_new` |
| Location (S3) | `s3://gex-datalake-silver-prod/buygoods_physical_new/` |
| Origem | **Webhook do BuyGoods** (push em tempo real) |
| Eventos (action_type) | `neworder`, `newcustomer`, `cancel`, `refund`, `abandon` (ver [[amostra_webhook_buygoods]], ~92 colunas) |
| Atribuição (campanha) | colunas **`subid` … `subid5`** (nomes nativos do webhook) |
| `cancel_reason` | **não existe** no webhook (entra NULL na unificada) |

**Por que é a fonte da verdade:** o webhook é o fluxo **vivo e completo** das transações
(é o que chega primeiro e cobre o dia a dia). Na unificação, **todos** os registros do
webhook entram, sem filtro.

---

## 3. Silver da API — *complemento*

| Propriedade | Valor |
|---|---|
| Tabela (Athena/Glue) | `gex_db_prod_silver.tb_silver_buygoods_orders` |
| Location (S3) | `s3://gex-datalake-silver-prod/buygoods_orders/` |
| Origem | **API do BuyGoods** (pull — histórico / backfill) |
| Amostra | ~130 colunas; tem `subid`, `cogs`, `merchant_commission` (ver [[amostra_api_buygoods]]) |
| Atribuição (campanha) | já vem com **`utm_*`** nomeados |
| `cancel_reason` | **existe** (exclusivo da API) |

**Papel:** a API serve para **preencher buracos** — traz o histórico que o webhook não
capturou (ex.: período anterior à ativação do webhook, ou eventos perdidos). Na
unificação, entram **apenas os `transaction_id` da API que NÃO existem no webhook**.

> ⚠️ **Operacional:** o polling da API em prod (`gex-buygoods-api-polling-daily-prod`)
> pode estar **desligado** — nesse caso a fatia `data_source = 'api'` fica **congelada**
> na última carga (o webhook continua atualizando normalmente). Conferir antes de
> investigar "dados faltando" no histórico.

---

## 4. Processo de geração da SILVER UNIFICADA

Job Glue **`gex-buygoods-unified-to-mysql-prod`** (Glue 4.0, `G.1X` x4) — script
`s3://gex-datalake-bronze-prod/scripts/buygoods_unified/jobs/silver_to_mysql_buygoods_unified.py`.

### 4.1 Parâmetros
| Argumento | Valor (prod) |
|---|---|
| `--WEBHOOK_LOCATION` | `s3://gex-datalake-silver-prod/buygoods_physical_new/` |
| `--API_LOCATION` | `s3://gex-datalake-silver-prod/buygoods_orders/` |
| `--TARGET_DATABASE` | `instituto_experience` |
| `--DB_TABLE` | `tb_gex_buygoods_unified` |
| `--GLUE_CONNECTION_NAME` | `gex-mysql-connection-prod` (credenciais via `extract_jdbc_conf`, sem Secrets Manager) |
| `--MIN_ROWS_THRESHOLD` | `1000` |

### 4.2 Regra de unificação (webhook tem prioridade)
1. **Todos** os registros do **webhook** → `data_source = 'webhook'`.
2. **+** registros da **API** cujo `transaction_id` **NÃO existe** no webhook → `data_source = 'api'`.
   - Implementado como **`LEFT ANTI JOIN`** da API contra os `transaction_id` distintos do webhook.
3. Resultado = `webhook ∪ api_only`. Equivalente conceitual em SQL (Athena/Trino):

```sql
WITH wh AS (  -- webhook: subid* renomeados para utm*
  SELECT transaction_id, /* … */
         subid  AS utm_source,  subid2 AS utm_content, subid3 AS utm_campaign,
         subid4 AS utm_term,    subid5 AS utm_medium,
         CAST(NULL AS varchar) AS cancel_reason,
         'webhook' AS data_source
  FROM gex_db_prod_silver.tb_buygoods_physical_new
),
api AS (  -- api: já tem utm_* e cancel_reason
  SELECT transaction_id, /* … */ utm_source, utm_content, utm_campaign,
         utm_term, utm_medium, cancel_reason, 'api' AS data_source
  FROM gex_db_prod_silver.tb_silver_buygoods_orders
),
api_only AS (
  SELECT api.* FROM api
  LEFT ANTI JOIN (SELECT DISTINCT transaction_id FROM wh) w
    ON api.transaction_id = w.transaction_id
)
SELECT * FROM wh
UNION ALL
SELECT * FROM api_only;
```

### 4.3 Reconciliação de schema (de-para `subid` → `utm_*`)
`subid*` (webhook) e `utm_*` (API) são **o mesmo dado com nomes diferentes**. Para a
tabela unificada ter colunas únicas, o webhook é renomeado:

| Webhook | → | Unificada |
|---|---|---|
| `subid`  | → | `utm_source` |
| `subid2` | → | `utm_content` |
| `subid3` | → | `utm_campaign` |
| `subid4` | → | `utm_term` |
| `subid5` | → | `utm_medium` |

- `cancel_reason`: existe **só na API**; no lado webhook entra como `NULL`.
- Qualquer coluna ausente em uma fonte é alinhada como `NULL` (cast string) para o
  schema único (`align_to_unified`).

### 4.4 Fluxo de execução (8 passos, com swap atômico)
| Passo | O que faz |
|---|---|
| 1 | Lê API silver e Webhook silver (parquet, direto do `LOCATION` no S3). |
| 2 | Reconcilia colunas (`subid→utm`) e monta o **UNION** (`webhook` + `api_only`). Adiciona `id = monotonically_increasing_id()` e `data_source`. |
| 3 | Carrega credenciais da Glue Connection (`extract_jdbc_conf`). |
| 3.5 | **Salvaguarda:** se a tabela final já existe e o snapshot novo tem **< 90%** da contagem atual, **aborta** (provável leitura incompleta da silver upstream) e mantém o dado antigo. |
| 4 | Escreve o resultado no **staging** `tb_gex_buygoods_unified_old` (`mode=overwrite`, Spark cria pelo schema do DF). |
| 5 | `CREATE TABLE IF NOT EXISTS <final> LIKE <staging>` (auto-bootstrap na 1ª run). |
| 6 | **Valida** contagem do staging ≥ `MIN_ROWS_THRESHOLD` (1000). |
| 7 | **Swap atômico:** `RENAME TABLE final → backup, staging → final`. |
| 8 | Limpa o backup (`DROP TABLE IF EXISTS …_backup`). |

> Também valida consistência: `total_unified == total_webhook + total_api_only` (senão aborta).

---

## 5. Schema da silver unificada (62 colunas)

> Ordem real da tabela no MySQL. **Origem:** `comum` = vem das duas fontes ·
> `gerado` = criado no job · `só API` · `reconciliado` (subid→utm no webhook).

| # | Coluna | Tipo (MySQL) | Origem / observação |
|--:|---|---|---|
| 1 | `id` | bigint NOT NULL | **gerado** — `monotonically_increasing_id()`. ⚠️ **não é PK estável** (muda a cada run; não usar como chave). |
| 2 | `transaction_id` | text | comum — **chave de unificação** |
| 3 | `transaction_type` | text | comum |
| 4 | `payment_status` | text | comum |
| 5 | `platform` | text | comum (sempre `buygoods`) |
| 6–13 | `client_name`, `client_email`, `client_phone`, `client_zip`, `client_country`, `client_state`, `client_city`, `client_street` | text | comum — dados do cliente |
| 14–18 | `product_name`, `product_sku`, `product_codename`, `product_id`(int), `offer_name` | text/int | comum — produto |
| 19 | `quantity` | int | comum |
| 20 | `sales_type` | text | comum |
| 21 | `vendor_name` | text | comum (geralmente vazio no BG) |
| 22–23 | `product_cost`, `product_cost_usd` | decimal | comum — custo |
| 24 | `total_collected_usd` | decimal(10,2) | comum — valor efetivamente cobrado |
| 25 | `total_price_usd` | decimal(10,2) | comum |
| 26–27 | `iva_usd`, `taxes_usd` | decimal(10,2) | comum — IVA (BR) e taxa de plataforma |
| 28 | `affiliate_amount_usd` | decimal(10,2) | comum |
| 29 | `exchange_rate` | decimal(10,4) | comum |
| 30–33 | `total_price`, `taxes`, `iva`, `affiliate_amount` | decimal(12,4) | comum — versões BRL |
| 34–35 | `commission_usd`, `commission` | decimal | comum |
| 36–37 | `total_refund_usd`, `total_refund` | decimal | comum |
| 38–39 | `refund_fee_usd`, `refund_fee` | decimal | comum — BuyGoods cobra ~USD 1/refund |
| 40–41 | `chargeback_fee_usd`, `chargeback_fee` | decimal | comum — multa de chargeback |
| 42 | `date_refunded` | date | comum |
| 43 | `datetime_refunded_platform` | text | comum |
| 44 | `affiliate_id` | text | comum — PK real do afiliado no BG |
| 45 | `account_id` | text | comum |
| 46 | `affiliate_name` | text | comum |
| 47 | `is_house_traffic` | **bit(1)** NOT NULL | comum — boolean; tráfego próprio (vira 0/1 na Gold) |
| 48 | `upsell_parent_receipt` | text | comum |
| 49–51 | `created_at_date`(date), `created_at_hour`, `datetime_platform` | date/text | comum — data/hora |
| 52–53 | `created_at`, `updated_at` | timestamp | comum |
| 54 | `pipeline_updated_at` | text | comum — ⚠️ é o `created_at` **deslocado ~6h** (timezone); não é "hora do load" |
| 55 | `dt_proc` | date | comum — carimbo de partição/processamento (diário) |
| 56 | `cancel_reason` | text | **só API** — NULL nos registros de webhook |
| 57 | `utm_source` | text | **reconciliado** (`subid` no webhook · nativo na API) |
| 58 | `utm_content` | text | **reconciliado** (`subid2`) |
| 59 | `utm_campaign` | text | **reconciliado** (`subid3`) |
| 60 | `utm_term` | text | **reconciliado** (`subid4`) |
| 61 | `utm_medium` | text | **reconciliado** (`subid5`) |
| 62 | `data_source` | text NOT NULL | **gerado** — `'webhook'` ou `'api'` |

---

## 6. Dicionário de campos — campo a campo

> Para cada campo: **o que representa**, **cálculo/origem** (campo do payload webhook/API quando
> conhecido) e **particularidades**. Origens marcadas com *(derivado)* são transformações do
> bronze→silver (não passthrough direto). Domínios abaixo foram perfilados na tabela real (read-only).

### 6.1 Identificação e tipo
| Campo | Representa | Cálculo / Origem | Particularidades |
|---|---|---|---|
| `id` | Surrogate técnico da linha | *(gerado)* `monotonically_increasing_id()` no Spark | **Volátil** — recriado a cada full-refresh; NÃO é PK estável, não usar como chave de negócio. |
| `transaction_id` | Identificador da transação na BuyGoods | passthrough do payload (`order_id_global`/`order_id`) | **Chave de unificação**. Webhook tem prioridade; a API só entra com IDs ausentes no webhook. Pode repetir entre eventos do mesmo pedido (sale/refund). |
| `transaction_type` | Tipo do evento da transação | *(derivado)* normalizado de `action_type`/`type` | Domínio real: **Sale** (88%), **Cancel** (11%), **Refund**, **Chargeback**, **Rebill**, **Fulfillment**. |
| `payment_status` | Situação do pagamento | *(derivado)* normalizado (ex.: payload `Completed`→`approved`) | Domínio: **approved**, **refunded**, **refunded_partial**, **chargeback**. Minúsculas. |
| `platform` | Plataforma de origem | *(constante)* `'buygoods'` | Sempre `buygoods` (campo existe para UNION com ClickBank na gold). |
| `data_source` | De qual silver o registro veio | *(gerado)* `'webhook'` ou `'api'` | NOT NULL. Use para auditar cobertura/atraso por fonte. ~95% `webhook`, ~5% `api`. |

### 6.2 Cliente
| Campo | Representa | Cálculo / Origem | Particularidades |
|---|---|---|---|
| `client_name` | Nome do cliente | `customer_name` / `name` | — |
| `client_email` | E-mail do cliente | `customer_emailaddress` | **Chave de negócio** usada no agrupamento por compra da gold (janela 240min). |
| `client_phone` | Telefone | `customer_phone` (API) | Frequentemente vazio no webhook. |
| `client_zip` | CEP/ZIP | `customer_zip` / `zip` | — |
| `client_country` | País | `customer_country` / `country` | Texto livre (ex.: `United States`); a gold mapeia ISO→nome. |
| `client_state` | Estado | `customer_state` / `state` | — |
| `client_city` | Cidade | `customer_city` / `city` | — |
| `client_street` | Endereço | `billing_address` / `address` | — |

### 6.3 Produto e funil
| Campo | Representa | Cálculo / Origem | Particularidades |
|---|---|---|---|
| `product_name` | Nome do produto | `product_name` | — |
| `product_sku` | SKU | `sku` | — |
| `product_codename` | Codinome técnico do produto | `product_codename` | Carrega o sinal do funil no prefixo: `PP_` (principal), `UP1_/UP2_/UP3_` (upsell), `DW1_/DW2_/DW3_` (downsell). É o fallback de classificação na gold. |
| `product_id` | ID do produto (int) | `product_id` | — |
| `offer_name` | Nome canônico da oferta | *(derivado)* mapeamento de oferta | **Em preenchimento** — ainda esparso; por isso a gold usa `product_codename` como fallback. |
| `quantity` | Quantidade de unidades | `product_quantity` | — |
| `sales_type` | Natureza da venda | *(derivado)* normalizado | Domínio real: **Produto Principal** (65%) e **Venda de Funil** (35%). |
| `vendor_name` | Nome do vendor | — | **Vazio** no BuyGoods (campo existe para paridade com ClickBank). |

### 6.4 Financeiro — câmbio e valores
> Quase todo valor tem par **USD** e **BRL**. A conversão usa `exchange_rate` (BRL por USD, ~**5,0**; faixa observada 4,89–5,18). USD com `DECIMAL(10,2)`, BRL com `DECIMAL(12,4)`.
>
> ⚠️ **`iva` ≠ `taxes`**: `iva` é o imposto sobre a venda (vem do payload `taxes`, renomeado); `taxes` (silver) representa a **taxa da plataforma** BuyGoods — *(derivado, confirmar no job bronze→silver)*.

| Campo (USD / BRL) | Representa | Cálculo / Origem | Particularidades |
|---|---|---|---|
| `exchange_rate` | Taxa de câmbio aplicada | *(derivado)* cotação USD→BRL do dia | ~5,0; usada para gerar todos os pares BRL a partir do USD. |
| `total_collected_usd` | Valor efetivamente cobrado do cliente | `total_collected` | Inclui o IVA; **maior** que `total_price` (subtotal do produto). Só em USD na tabela. |
| `total_price_usd` / `total_price` | Subtotal do produto (sem impostos) | `product_subtotal` / `product_price`×qtd | Base de "faturamento de produto". |
| `iva_usd` / `iva` | Imposto sobre venda (Brasil) | payload **`taxes`** (renomeado) | Não confundir com `taxes` (plataforma). |
| `taxes_usd` / `taxes` | Taxa da plataforma BuyGoods | *(derivado)* | Distinta do IVA; a confirmar no bronze→silver. |
| `product_cost_usd` / `product_cost` | Custo do produto (COGS) | payload `cogs` (API) / tabela de custos | Pode faltar quando a fonte é só webhook. |
| `commission_usd` / `commission` | Comissão do vendedor (líquida) | *(derivado)* `net_commissions`/`merchant_commission` | Em **house traffic** a gold faz `commission += affiliate_amount`. |
| `affiliate_amount_usd` / `affiliate_amount` | Comissão paga ao afiliado | `aff_commission` | Em house traffic é absorvido pela comissão na gold (vira 0). |
| `total_refund_usd` / `total_refund` | Valor estornado | `refund_amount` | **Bruto** (sem deduzir iva/taxes). `<>0` apenas em cancel/refund/chargeback (~12% das linhas). |
| `refund_fee_usd` / `refund_fee` | Taxa de refund cobrada pela BuyGoods | *(regra fixa)* ~**USD 1,00** por refund | — |
| `chargeback_fee_usd` / `chargeback_fee` | Multa de chargeback | `chargeback_fee` | Tipicamente ~USD 35. |

### 6.5 Afiliado e atribuição de tráfego
| Campo | Representa | Cálculo / Origem | Particularidades |
|---|---|---|---|
| `affiliate_id` | ID real do afiliado na BuyGoods | `aff_id` / `affiliate_id` | **PK real** do afiliado — um mesmo `affiliate_name` pode ter vários `affiliate_id`. |
| `affiliate_name` | Nome do afiliado | `aff_name` / `affiliate_name` | Não usar sozinho como chave. |
| `account_id` | Conta (vendor) na BuyGoods | `account_id` | No futuro será resolvido para `vendor_name`. |
| `is_house_traffic` | Tráfego próprio (afiliado interno) vs externo | *(derivado)* `affiliate_id` ∈ [[buygoods_internal_affiliates]] | Tipo `bit(1)` (0/1), **NOT NULL**. ~5,6k webhook + 1,1k api. Muda o rateio comissão/afiliado na gold. |

### 6.6 Refund / cancelamento
| Campo | Representa | Cálculo / Origem | Particularidades |
|---|---|---|---|
| `date_refunded` | Data do estorno | `date_refunded` (DATE) | NULL quando não houve refund. |
| `datetime_refunded_platform` | Data/hora do estorno (texto da plataforma) | `date_refunded`/`date_chargedback` cru | Texto; preserva o formato original. |
| `cancel_reason` | Motivo do cancelamento | `cancel_reason` | **Só da API** — sempre NULL nos registros `webhook` (confirmado: 0 preenchidos no webhook). Cobertura baixa mesmo na API (~7%). |

### 6.7 Datas, funil e processamento
| Campo | Representa | Cálculo / Origem | Particularidades |
|---|---|---|---|
| `created_at_date` | Data da transação (DATE) | *(derivado)* de `datetime_platform` | Usada em filtros/partição lógica e no agrupamento da gold. |
| `created_at_hour` | Hora da transação (texto) | *(derivado)* de `datetime_platform` | Concatenada com `created_at_date` para reconstruir o timestamp na gold. |
| `datetime_platform` | Data/hora original da plataforma | `order_date_time` / `rr_createdate` | Texto; é o "relógio do negócio" (não o do pipeline). |
| `upsell_parent_receipt` | Pedido principal ao qual o upsell pertence | `external_order_id` / referrer | Liga upsell/downsell ao checkout pai. Deixou de ser chave de agrupamento na gold v2. |
| `created_at` | Timestamp de carga (load) | *(pipeline)* TIMESTAMP | Hora em que o registro foi materializado. |
| `updated_at` | Timestamp da última atualização | *(pipeline)* TIMESTAMP | — |
| `pipeline_updated_at` | (texto) carimbo do pipeline | *(derivado)* = `created_at` deslocado ~6h (timezone) | ⚠️ **Não é hora de carga real** — é o mesmo evento em outro fuso. Para recência, olhar a execução do job/SFN. |
| `dt_proc` | Data de processamento/partição | *(pipeline)* DATE (diário) | Carimbo de lote; útil para auditar por dia processado. |

### 6.8 Atribuição de campanha (UTM)
| Campo | Representa | Cálculo / Origem | Particularidades |
|---|---|---|---|
| `utm_source` | Origem da campanha | webhook `subid` · API `subid`/`utm_source` | ~90% preenchido. |
| `utm_content` | Conteúdo/criativo | webhook `subid2` | — |
| `utm_campaign` | Campanha | webhook `subid3` | — |
| `utm_term` | Termo | webhook `subid4` | — |
| `utm_medium` | Mídia | webhook `subid5` | — |
> **De-para crítico:** no webhook a atribuição chega como `subid…subid5`; o job renomeia para
> `utm_*` (ver §4.3) para a tabela ter colunas únicas. Quem consome deve usar **só `utm_*`**.

## 7. Regras e pontos de atenção
- **Sem chave primária real.** `id` é volátil (recriado a cada run). A chave de negócio é
  `transaction_id`; a deduplicação entre fontes é feita por ele (webhook ganha).
- **Webhook é base; API só complementa.** Nunca há duplicidade de `transaction_id` entre
  as fontes na saída — a API só entra com IDs ausentes no webhook.
- **`cancel_reason` só vem da API** → para registros que existem só no webhook, fica NULL.
- **`utm_*` unificados:** quem consome (Gold/dashboards) lê `utm_*` direto; não usar mais
  `subid*`. A Gold popula os `utm_*` via `MAX(utm_*)` (ver [[doc_gold_buygoods]] §3.10).
- **`pipeline_updated_at` não é hora de carga** — é `created_at` em outro fuso (~6h). Para
  recência real do pipeline, olhar a execução do job/SFN, não essa coluna.
- **Reescrita total (full refresh) a cada run** via swap atômico: a tabela é substituída
  inteira; não é incremental. A salvaguarda de 90% evita publicar snapshot truncado.
- **Cadência ~2h** ⇒ a cauda do dado fica naturalmente até ~2h atrás (lag de batch normal).
- **Volume:** ~300k+ linhas; é uma das tabelas-fonte grandes do banco.

## 8. Operação / troubleshooting
- **Tabela "desatualizada":** confira (1) última execução de `gex-buygoods-unified-to-mysql-prod`
  e do upstream `bronze-to-silver-buygoods-prod`; (2) se a salvaguarda de 90% abortou o swap;
  (3) se a fatia `api` está congelada (polling prod desligado) — separar por `data_source`:
  `SELECT data_source, MAX(created_at), COUNT(*) FROM tb_gex_buygoods_unified GROUP BY data_source;`
- **Falha do job:** alerta `buygoods-glue-job-failures` (EventBridge → SNS `buygoods-glue-alerts`).

## 9. Relacionados
- Job/orquestração: [[gex-buygoods-unified-to-mysql-prod]] · [[gex-bronze-to-silver-buygoods-prod]] · [[00-Orquestracao]]
- Fonte: [[Buygoods]] · [[amostra_webhook_buygoods]] · [[amostra_api_buygoods]] · [[tb_gex_buygoods_unified]]
- Camada Gold: [[doc_gold_buygoods]]
