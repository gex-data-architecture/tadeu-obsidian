---
name: validar-plataforma-buygoods
description: Valida/reconcilia a silver `instituto_experience.tb_gex_buygoods_unified` (TODA a plataforma) contra o export diário do **Master Overview** do BuyGoods (Excel com totais por dia: Gross Sales/Commissions/Refunds/Chargebacks/Commission Voids/Taxes/Net Sales). Gera **validação total E por dia**. Use SEMPRE que o usuário falar em "validar a plataforma do BuyGoods", "validar o Master Overview", "reconciliar a silver com a plataforma", "conferir Gross/Net/Refunds da BuyGoods", "bater os números do BuyGoods", "validação total e por dia da plataforma" — mesmo sem dizer "skill". É SOMENTE LEITURA no MySQL (MCP `mysql`). Para validar UMA conta específica (extrato por account), use a skill `validar-conta-buygoods`.
---

# validar-plataforma-buygoods

Reconcilia a **silver agregada** (toda a plataforma) com o **Master Overview** do BuyGoods.
Entrega **sempre** o total do período **e** a quebra **por dia** (P×S lado a lado), mais um locador por mês.

## Entrada
- Excel do **Master Overview** (export diário do BuyGoods). Colunas: `Date, Gross Sales, Commissions,
  Refunds, Chargebacks, Commission Voids, Taxes, AOV, Net Sales` (+ linha `Total`, ignorada).
- O período é **derivado do próprio Excel** (min/max da coluna `Date`).

## De-para (KPI plataforma → silver), base timestamp-plataforma
| KPI | Silver |
|---|---|
| Gross Sales | `total_price_usd - iva_usd` por `DATE(datetime_platform)` |
| Commissions | `affiliate_amount_usd` por `DATE(datetime_platform)` |
| Taxes | `iva_usd` dos `approved` por `DATE(datetime_platform)` |
| Refunds | `total_refund_usd` (não-chargeback) por `DATE(datetime_refunded_platform)` |
| Chargebacks | `total_refund_usd + chargeback_fee_usd` (chargeback), mesma data |
| Net Sales | `Gross − Commissions − Refunds − Chargebacks − Taxes` (plataforma soma Commission Voids) |

> ⚠️ A data do Master Overview casa **direto** com a silver (sem shift). Alinhar pelo
> `datetime_platform` (não `created_at_date`, que está +1h e desalinha dias movimentados).

## Como rodar
```powershell
python "C:\Users\tadeu\DataTeamDocs\.claude\skills\validar-plataforma-buygoods\scripts\validar_plataforma.py" [caminho_do_excel]
```
Sem argumento, usa o `Master_Overview_*.xls*` mais recente em `Downloads`.
Requer `pandas`, `xlrd>=2.0.1` (.xls) / `openpyxl` (.xlsx), `pymysql` (creds do MCP `mysql` no `.claude.json`).

## Saída
- Nota `Operação/Validações/validacao-plataforma-buygoods-<fim>.md` com: de-para, **Total**, **por mês**
  (locador), **por dia** (P×S + Δ Net) e **achados automáticos** (maiores desvios).

## Interpretação
- Desvio pequeno e ~uniforme → arredondamento/FX/definição fina (ok).
- Desvio concentrado no **período recente** → provável **settlement** (reavaliar com export mais novo).
- **Quebra com data fixa** (reconcilia até X, despenca depois) → investigar **ingestão** a partir de X.

## Após rodar
- Acrescente uma linha no `log.md` com o veredito (Δ% por KPI).
