---
tipo: validacao
assunto: total_refund_usd deve descontar o IVA (taxes) nas silvers BuyGoods — afeta o commission da unificada
data: 2026-06-12
solicitante: Gabriel (CTO)
status: a-implementar
fonte_codigo: Arquitetura/Data Lake/Jobs/bronze-to-silver-buygoods-prod (e gex-buygoods-orders-bronze-to-silver-prod); unificada gex-buygoods-unified-to-mysql-prod
tags: [validacao, buygoods, silver, total-refund, iva, commission, ajuste, a-implementar]
---
# Validação — `total_refund_usd` menos IVA (silvers BuyGoods)

> [!note] Resumo
> Subtrair o **IVA** (campo `taxes` da bronze / `iva_usd` na silver) do **`total_refund_usd`** nos **dois** jobs de silver (webhook e API). É o **único** ajuste de código necessário. A silver **unificada não muda**. Há também 1 lembrete (`transaction_type`) sem ação imediata.

## Contexto

Revisão completa das regras das duas silvers BuyGoods (webhook e API) e da unificada. A grande maioria das diferenças entre as silvers é **intencional** (não são divergências). Confirmados como corretos / sem ação:

- Filtro de `cancel` (só a API descarta) — correto.
- Dedup (estratégias diferentes por fonte) — correto.
- `payment_status` — sem divergência (cancel já é filtrado antes).
- `client_name`, `client_email`, `client_phone`, `client_zip/state/city/street`, `client_country` — sem divergência.
- `total_price_usd` — **correto**: na API é `total_amount_charged − taxes`; no webhook é `total_amount_charged` (no webhook o `total_amount_charged` já não deduz `taxes`). Não é divergência.
- `commission_usd` (base nas silvers) — correto; o cálculo **final** da comissão é feito na unificada.
- `date_refunded` / `datetime_refunded_platform` — corretos (fuso da API difere do webhook por origem).
- `created_at`, `updated_at`, `dt_proc` — sem divergência.
- `utm_*` / `subid*` — correto; padronização feita na unificada.

**Único ajuste de código:** o item 1 abaixo.

## ✅ Ajuste 1 (obrigatório) — `total_refund_usd` passa a descontar o IVA

**Regra nova:** `total_refund_usd` deve ser **subtraído pelo IVA**, onde **IVA = imposto sobre venda = campo `taxes` da bronze** (`iva_usd` na silver).
**Onde:** nos **dois** jobs de silver (webhook **e** API).
**Por que nos jobs de silver (e não na unificada):** o `commission_usd` canônico (calculado na unificada) **subtrai `total_refund_usd`**. Alterar na origem (silvers) muda corretamente a comissão final. O `total_refund` (BRL) acompanha automaticamente (= `total_refund_usd × exchange_rate`).

### 1a) Job da API — `gex-buygoods-orders-bronze-to-silver-prod`
- Script: `s3://gex-datalake-bronze-prod/scripts/buygoods_orders_bronze_to_silver.py`
- IVA neste job = `taxes_v` (= `parse_money(taxes)`; fonte de `iva_usd`).

**ANTES:**
```python
total_refund_usd_expr = (
    F.when(F.col("is_chargeback"), F.coalesce(F.col("total_clean_v"), F.lit(0.0)))
     .when(F.col("is_refund"), F.coalesce(F.col("refund_amount_v"), F.lit(0.0)))
     .otherwise(F.lit(0.0))
)
```

**DEPOIS:**
```python
total_refund_usd_expr = (
    F.when(
        F.col("is_chargeback"),
        F.coalesce(F.col("total_clean_v"), F.lit(0.0)) - F.coalesce(F.col("taxes_v"), F.lit(0.0)),
    )
     .when(
        F.col("is_refund"),
        F.coalesce(F.col("refund_amount_v"), F.lit(0.0)) - F.coalesce(F.col("taxes_v"), F.lit(0.0)),
    )
     .otherwise(F.lit(0.0))
)
```

### 1b) Job do Webhook — `bronze-to-silver-buygoods-prod`
- Script: `s3://gex-datalake-bronze-prod/scripts/bronze_to_silver_buygoods.py`
- IVA neste job = `taxes_bg_sale` (taxes isolado do evento de venda/neworder; fonte de `iva_usd`).

**ANTES:**
```python
total_refund_usd_corrected_expr = (
    F.when(
        F.col("has_chargeback") == 1,
        F.coalesce(F.col("total_clean"), F.lit(0.0))
    )
    .otherwise(F.col("total_refund_usd_raw"))
)
```

**DEPOIS:**
```python
total_refund_usd_corrected_expr = (
    F.when(
        F.col("has_chargeback") == 1,
        F.coalesce(F.col("total_clean"), F.lit(0.0)) - F.coalesce(F.col("taxes_bg_sale"), F.lit(0.0)),
    )
    .when(
        F.col("has_refund") == 1,
        F.coalesce(F.col("total_refund_usd_raw"), F.lit(0.0)) - F.coalesce(F.col("taxes_bg_sale"), F.lit(0.0)),
    )
    .otherwise(F.lit(0.0))
)
```

> **Nota técnica (webhook):** o `otherwise` atual já retornava `total_refund_usd_raw` (0 quando não há reembolso). A reescrita torna explícito o caso `has_refund` (subtrai IVA) e mantém **0** quando não há reembolso/chargeback — preservando o comportamento de pedidos aprovados.

### ⚠️ Ponto a confirmar antes de implementar
1. **Pedido aprovado (sem reembolso):** `total_refund_usd` permanece **0** (não desconta IVA). — *assumido como correto.*
2. **Reembolso menor que o IVA:** o resultado pode ficar **negativo** (`refund − iva < 0`). Confirmar se deve haver **piso em 0** (`max(total_refund_usd, 0)`) ou se o negativo é aceitável.

## 🚫 Não alterar — Silver Unificada (`tb_gex_buygoods_unified`)

- Job `gex-buygoods-unified-to-mysql-prod` **permanece igual**.
- A fórmula do `commission_usd` canônico **continua a mesma**; passará a usar **automaticamente** o novo `total_refund_usd` (herdado das silvers; na reconciliação `total_refund_usd` é campo de ESTADO, vindo da fonte mais avançada).
- Fórmula canônica (inalterada), referência:
  ```
  total_price     = total_collected_usd − iva_usd
  commission_usd  = total_price
                    − (taxes_usd se payment_status='approved'; senão 0)
                    − affiliate_amount_usd
                    − total_refund_usd        ← passa a refletir o novo valor (já com IVA descontado)
                    − refund_fee_usd
                    − chargeback_fee_usd
  ```

## 🔔 Lembrete (sem ação agora) — `transaction_type`

Diferença de vocabulário entre as silvers (sem impacto hoje; **pode** virar mudança de regra depois):
- **Webhook:** ciclo de vida — `Sale` / `Refund` / `Chargeback` / `Cancel`.
- **API:** binário — `Sale` / `Cancel` (refund e chargeback viram `Cancel`).

Apenas registrar; reavaliar futuramente.

## Checklist de implementação

- [ ] Editar `total_refund_usd_expr` no script da **API**.
- [ ] Editar `total_refund_usd_corrected_expr` no script do **Webhook**.
- [ ] Confirmar tratamento de negativos (piso em 0?).
- [ ] Deploy dos dois scripts no S3.
- [ ] Reprocessar as duas silvers.
- [ ] Rodar a unificada e **validar `commission_usd`** (próxima etapa: validação de números).

## Relacionados
- [[validacao-reembolso-parcial-fee]] · [[validacao-conta-buygoods-12340]] · [[validacao-conta-buygoods-12501]]
- Jobs: [[bronze-to-silver-buygoods-prod]] · [[gex-buygoods-orders-bronze-to-silver-prod]] · [[gex-buygoods-unified-to-mysql-prod]]
