---
name: validar-conta-buygoods
description: Valida/reconcilia a silver `instituto_experience.tb_gex_buygoods_unified` para UMA conta de vendor (account_id) contra o extrato diário "Transactions" do BuyGoods (Excel por conta, com Sales/Commissions/Refunds/Chargebacks/Fees/Sale Taxes/Voids/Amount por dia). Validação **campo a campo, total E por dia**. Use SEMPRE que o usuário falar em "validar a conta", "validar o account", "validar o extrato do BuyGoods", "conferir os dados de uma conta/vendor", "validar Memopezil", "extrato Transactions", "bater a silver com a conta X", ou der um Excel de uma conta específica — mesmo sem dizer "skill". É SOMENTE LEITURA no MySQL (MCP `mysql`). Para validar a plataforma inteira (Master Overview agregado), use a skill `validar-plataforma-buygoods`.
---

# validar-conta-buygoods

Reconcilia a silver de **uma conta** (`account_id`) com o extrato diário **"Transactions"** do BuyGoods.
Entrega de-para, **total campo a campo**, **por dia** (Δ de cada campo) e **Refunds por dia** (P×S).

## Entrada
- Excel **Transactions** do BuyGoods (uma conta). Colunas: `Date, Sales, Commissions, Refunds, Chargebacks,
  Commissions Voids, Fee Voids, Fees, Sale Tax Refunds, Sale Taxes, Shipping/Handling, Amount, Balance, JV%, Alerts, Product Notes`.
- `account_id`: passado como 2º argumento **ou** lido do fim do nome do arquivo (`Transactions_..._<acc>.xlsx`).
- ⚠️ **O Excel rotula o dia `D` com os valores de `D-1`** → o script usa `silver = Excel − 1 dia`.

## De-para (campo Excel → silver), base timestamp-plataforma
| Campo Excel | Silver | Obs |
|---|---|---|
| Sales | `total_collected_usd` | ✅ |
| Commissions | `affiliate_amount_usd` | ✅ (nome "trocado": é o afiliado) |
| Sale Taxes | `iva_usd` | ✅ |
| Fees | `taxes_usd` | ✅ (taxa BuyGoods) |
| Refunds | `total_refund_usd` (não-cbk) | por `datetime_refunded_platform` |
| Chargebacks | `total_refund_usd + chargeback_fee_usd` (cbk) | idem |
| Sale Tax Refunds | `iva_usd` dos refunded | idem |
| Fee Voids / Commission Voids | — | ❌ **não deriváveis** (política de void; comissão/fee em geral não estornam) |
| Amount / Balance | — | ⛔ settlement (allowances/holds), não-transacional |

> **Amount** (líquido do vendor) corresponde ao `commission_usd` da silver — nome trocado —, mas no extrato
> diário inclui allowances/holds, então não é comparável direto.

## Como rodar
```powershell
python "C:\Users\tadeu\DataTeamDocs\.claude\skills\validar-conta-buygoods\scripts\validar_conta.py" [caminho_do_excel] [account_id]
```
Sem args, usa o `Transactions_*.xlsx` mais recente em `Downloads` e infere o `account_id` do nome.
Requer `pandas`, `openpyxl`, `pymysql` (creds do MCP `mysql`).

## Saída
- Nota `Operação/Validações/validacao-conta-buygoods-<account_id>.md` com de-para (Δ% por campo), **Total**,
  **por dia** e **Refunds por dia**. O script **auto-detecta quebra com data** nos refunds (1º dia com Δ < −20%).

## Interpretação
- Sale-side (Sales/Commissions/Sale Taxes/Fees) deve bater ~≤1%.
- **Refunds/Chargebacks**: se reconciliam até uma data e despencam depois (e o pior NÃO é o mais recente),
  é **quebra de ingestão de estornos** a partir dessa data — não lag. Investigar o pipeline.
- **Voids**: divergência esperada — a silver não modela voids.

## Após rodar
- Acrescente uma linha no `log.md` com o veredito.
