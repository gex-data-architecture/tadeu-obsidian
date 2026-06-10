---
tipo: validacao
assunto: devolução da taxa da plataforma (merchant fee) em REEMBOLSO PARCIAL — silver BuyGoods
data: 2026-06-10
fonte_codigo: Arquitetura/Data Lake/Jobs/bronze-to-silver-buygoods-prod (e gex-buygoods-orders-bronze-to-silver-prod)
tags: [validacao, reconciliacao, buygoods, silver, reembolso-parcial, fee, achado]
---
# Validação — devolução da fee da plataforma em reembolso parcial

> [!warning] Achado
> Em **reembolso parcial**, a silver **não devolve a fee da plataforma proporcionalmente**. A coluna
> `taxes_usd` (= `merchant_commission`) fica **cheia/congelada**, e no `commission_usd` (líquido do vendor)
> a fee é **removida inteira** (binário, qualquer refund) — mesmo quando só uma fração foi estornada.
> Isso **superestima o `commission_usd`** dos parciais. Efeito quantificado: **~US$ 102 mil** no período.

## Como o job trata o refund parcial (código)
Fonte: job Glue `bronze-to-silver-buygoods-prod` (monta `tb_buygoods_physical_new`); idêntico em
`gex-buygoods-orders-bronze-to-silver-prod` (`tb_silver_buygoods_orders`).

1. **`taxes_usd` (= `merchant_commission`) é IMUTÁVEL do snapshot da venda** — não reduz em refund nenhum:
   ```python
   # [INFO] taxes_usd remains immutable from sale snapshot;
   #        refund/chargeback use taxes=0 only in commission formula.
   .withColumn("taxes_usd", dec2(merchant_commission))   # valor integral da venda
   ```
   No merge incremental é carregada do registro anterior (`coalesce(taxes_usd, taxes_usd_prev)`).

2. **`commission_usd` (líquido do vendor) zera a fee INTEIRA para qualquer refund** (não rateia pelo parcial):
   ```python
   # refunded / refunded_partial:
   total_amount_charged − 0(merchant) − aff_commission − refund_fee_usd
   # venda normal:
   total_amount_charged − merchant_commission − aff_commission
   ```
   → num parcial de 20%, a fee é devolvida 100% no líquido.

3. Demais campos do estorno:
   - `total_refund_usd` = soma real dos `refund_amount` → **respeita o parcial** (valor de fato estornado).
   - `refund_fee_usd` = **US$ 1,00 fixo** por refund (não é a fee da plataforma).
   - `payment_status` = `refunded` se `total_refund ≥ total_clean`, senão `refunded_partial`.

## Como a plataforma realmente faz
A BuyGoods devolve a fee **proporcional** ao valor estornado — confirmado na validação por conta:
o "Fee Voids" do extrato bateu com `taxes_usd × (total_refund/total_collected)` (Slimtide **−0,37%**).
Ver [[validacao-conta-buygoods-12501]].

## Quantificação (período 01/04 → 09/06, `payment_status='refunded_partial'`)
| Métrica | Valor |
|---|--:|
| Nº de reembolsos parciais | **7.627** |
| Fee da plataforma (cheia) nesses pedidos | US$ 171.987,45 |
| % médio estornado | **40,6%** |
| Fee que **deveria** voltar (proporcional) | US$ 69.588,99 |
| **Over-credit no `commission_usd`** (fee devolvida a mais) | **US$ 102.398,46** |

> A silver efetivamente devolve a fee inteira (171,9k) quando o correto seria ~69,6k → **vendor superestimado em ~102,4k** no `commission_usd`/`commission` dos parciais.

## Recomendação
Tornar a devolução da fee **proporcional ao estornado** no `commission_usd` dos `refunded`/`refunded_partial`:
em vez de zerar `merchant_commission`, manter a parte **não estornada** da fee, ex.:
`commission_usd = total_price_usd − merchant_commission × (1 − total_refund/total_collected) − aff_commission − refund_fee`.
Os dois trechos já estão marcados como `# AJUSTE` (alterações manuais) — revisar com o time do lake.

## Relacionados
- Cálculo do commission: jobs em `Arquitetura/Data Lake/Jobs/` (`*-bronze-to-silver-*`)
- Validação por conta: [[validacao-conta-buygoods-12340]] · [[validacao-conta-buygoods-12501]]
- Silver doc: [[Fontes de Dados/Buygoods/doc_silver_buygoods]] · [[CLAUDE]] · [[log]]
