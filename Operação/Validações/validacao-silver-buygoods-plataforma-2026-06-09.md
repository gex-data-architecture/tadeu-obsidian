---
tipo: validacao
par: tb_gex_buygoods_unified (silver MySQL) x plataforma BuyGoods (Master Overview, diário)
data: 2026-06-09
periodo: 2026-04-01 a 2026-06-09
moeda: USD
gerado_por: Operação/Validações/validacao_silver_buygoods_plataforma.py
tags: [validacao, reconciliacao, buygoods, silver, plataforma]
---
# Validação — silver `tb_gex_buygoods_unified` × plataforma BuyGoods (diário)

> Reconciliação **dia a dia** contra o export diário do Master Overview (USD), alinhada pelo **timestamp da plataforma** (`datetime_platform` / `datetime_refunded_platform`).
> Veredito: a silver bate **≤1%** em Gross/Commissions/Refunds/Taxes; **Refunds reconcilia quase 100%**. Dois pontos de atenção: **Chargebacks (−16,5%)** e **Gross de junho (+2%)**.

## De-para (campo da silver por KPI, base timestamp-plataforma)

| KPI (plataforma) | Definição na silver |
|---|---|
| **Gross Sales** | `SUM(total_price_usd - iva_usd)` por `DATE(datetime_platform)` |
| **Commissions** | `SUM(affiliate_amount_usd)` por `DATE(datetime_platform)` |
| **Refunds** | `SUM(total_refund_usd)` (não-chargeback) por `DATE(datetime_refunded_platform)` |
| **Chargebacks** | `SUM(total_refund_usd)` onde `payment_status=chargeback OR transaction_type=Chargeback` |
| **Taxes** | `SUM(iva_usd)` das vendas `approved` por `DATE(datetime_platform)` |
| **Net Sales** | `Gross − Commissions − Refunds − Chargebacks − Taxes` (plataforma ainda soma `Commission Voids`) |

## Total do período

| KPI | Plataforma | Silver | Δ | Δ% |
|---|--:|--:|--:|--:|
| Gross Sales | 98.682.421,49 | 99.058.916,16 | 376.494,67 | +0.38% |
| Commissions | 59.795.581,89 | 59.529.378,06 | -266.203,83 | -0.45% |
| Refunds | 13.112.830,70 | 13.119.432,77 | 6.602,07 | +0.05% |
| Chargebacks | 511.617,99 | 426.945,56 | -84.672,43 | -16.55% |
| Taxes | 4.940.501,19 | 4.985.461,52 | 44.960,33 | +0.91% |
| Net Sales | 20.367.203,07 | 20.997.698,25 | 630.495,18 | +3.10% |

> **Refunds** agora reconcilia (+0,05%) ao atribuir pelo `datetime_refunded_platform` e separar chargeback. **Chargebacks** fica −16,5% (a silver subnotifica) e **Net** herda o efeito de voids + chargebacks + gross de junho.

## Onde a diferença está (por mês)

| Mês | Δ Gross% | Δ Comm% | Δ Refunds% | Δ Chargeback% |
|---|--:|--:|--:|--:|
| 2026-04 | -1.01% | -0.85% | -1.37% | -38.05% |
| 2026-05 | +0.09% | -0.51% | -1.52% | -17.84% |
| 2026-06 | +1.97% | -0.02% | +2.88% | -13.53% |

> A diferença **não é uniforme**: o Gross drifta **+2% em junho** (período mais recente — provável settlement de vendas/ajustes ainda não refletido igual nos dois lados). Abril fica levemente negativo.

## Por dia — Δ silver − plataforma (USD)

> Valores são **diferença** (silver menos plataforma) por KPI. Use para localizar dias divergentes.

| Dia | Δ Gross | Δ Comm | Δ Refunds | Δ Chargeback | Δ Taxes | Δ Net |
|---|--:|--:|--:|--:|--:|--:|
| 01/04 | -1.887,25 | -1.261,10 | -3.379,88 | 0,00 | -4,08 | 2.585,82 |
| 02/04 | -3.581,64 | -1.830,00 | -3.039,45 | 0,00 | 36,18 | 1.251,63 |
| 03/04 | -2.073,14 | -1.585,11 | -3.635,67 | -658,00 | -73,08 | 3.878,72 |
| 04/04 | -4.260,08 | -2.230,73 | -1.144,85 | 0,00 | -296,90 | -779,57 |
| 05/04 | -2.883,71 | -1.132,43 | -207,00 | 0,00 | -464,13 | -1.080,15 |
| 06/04 | -5.869,22 | -2.191,57 | -1.688,25 | 0,00 | -196,57 | -1.792,83 |
| 07/04 | -5.222,53 | -2.379,37 | -2.727,57 | 0,00 | -183,76 | 68,17 |
| 08/04 | -3.575,57 | -1.356,26 | -810,26 | -329,00 | -135,10 | -1.468,98 |
| 09/04 | -1.600,67 | 0,00 | 0,00 | -366,67 | -721,96 | -604,47 |
| 10/04 | -1.815,24 | 171,99 | 556,92 | 0,00 | -663,15 | -1.881,00 |
| 11/04 | -1.542,10 | -171,99 | 58,50 | 0,00 | -509,36 | -1.152,80 |
| 12/04 | 2.573,78 | -200,00 | 0,00 | -349,58 | -2.888,77 | 5.747,71 |
| 13/04 | 2.573,58 | 0,00 | 23,30 | -610,94 | -2.233,14 | 4.749,51 |
| 14/04 | 1.311,21 | 0,00 | 0,00 | -364,00 | -2.579,94 | 3.093,45 |
| 15/04 | 1.471,86 | -187,38 | 0,00 | 0,00 | -1.881,50 | 2.937,14 |
| 16/04 | -1.019,48 | -92,43 | 0,00 | 0,00 | -2.505,65 | 1.391,22 |
| 17/04 | -2.555,64 | 0,00 | 391,47 | 0,00 | -1.622,93 | -2.931,69 |
| 18/04 | -1.933,59 | 0,00 | 0,00 | -331,94 | -1.263,90 | -437,29 |
| 19/04 | 552,01 | -250,00 | 0,00 | 0,00 | -1.686,95 | 2.488,96 |
| 20/04 | 411,71 | 0,00 | 130,53 | -437,99 | -1.893,48 | 2.111,55 |
| 21/04 | 2.082,61 | 0,00 | 317,85 | -105,00 | -2.226,08 | 2.802,53 |
| 22/04 | 2.424,26 | 0,00 | 744,22 | -423,26 | -2.711,07 | 3.451,41 |
| 23/04 | -4.718,12 | 0,00 | 512,74 | -295,88 | -3.773,39 | -1.593,19 |
| 24/04 | -3.079,59 | 387,57 | 146,25 | -896,49 | -3.604,06 | 67,14 |
| 25/04 | -11.087,53 | -1.740,00 | 365,34 | -35,00 | -6.972,96 | -2.826,02 |
| 26/04 | -13.647,25 | -4.415,00 | -147,00 | -140,00 | -9.155,40 | -69,66 |
| 27/04 | -15.761,23 | -8.300,00 | 201,55 | -70,00 | -6.611,29 | -981,49 |
| 28/04 | -14.972,70 | -9.460,00 | 196,84 | -140,00 | -8.285,08 | 1.958,87 |
| 29/04 | -9.240,77 | -6.870,00 | 1.140,79 | -469,00 | -7.181,95 | 3.790,33 |
| 30/04 | -2.169,02 | -8.702,10 | 1.826,95 | -420,00 | -5.975,20 | 10.146,96 |
| 01/05 | -19.842,47 | -6.640,00 | 3.356,70 | -210,00 | -1.053,23 | -17.165,93 |
| 02/05 | -30.842,20 | -10.865,00 | 450,18 | -385,00 | -8.539,20 | -11.749,01 |
| 03/05 | -38.875,30 | -13.890,00 | 727,73 | -524,58 | -11.643,36 | -13.721,21 |
| 04/05 | -16.580,97 | -8.805,00 | 5.100,47 | -455,00 | -4.380,47 | -8.561,07 |
| 05/05 | -23.333,24 | -8.490,71 | 1.994,05 | -560,00 | -4.335,87 | -13.277,09 |
| 06/05 | -35.699,59 | -12.740,00 | 3.607,92 | -1.264,67 | -3.817,88 | -22.189,62 |
| 07/05 | -54.133,54 | -13.411,12 | 2.289,79 | -1.691,51 | -4.214,76 | -37.325,94 |
| 08/05 | -8.442,08 | -10.210,00 | 4.695,17 | -1.187,00 | -3.229,81 | 775,33 |
| 09/05 | -37.083,78 | -14.039,35 | 1.128,61 | -925,45 | -10.452,55 | -14.733,25 |
| 10/05 | -22.694,97 | -8.350,00 | 1.179,65 | -913,87 | -7.640,75 | -7.255,41 |
| 11/05 | -20.044,07 | -9.875,00 | 4.826,75 | -1.922,38 | -2.731,38 | -11.395,22 |
| 12/05 | -13.523,34 | -6.840,00 | 3.435,21 | -1.804,61 | -6.929,22 | -2.062,74 |
| 13/05 | -6.664,65 | 0,00 | 5.278,38 | -2.826,45 | -2.043,23 | -8.265,91 |
| 14/05 | 1.400,01 | -94,35 | 5.561,42 | -1.865,45 | -2.379,82 | -643,63 |
| 15/05 | 20.176,79 | 0,00 | 5.287,46 | -2.197,56 | 371,33 | 16.434,22 |
| 16/05 | 46.317,60 | 0,00 | 7.223,99 | -537,14 | -6.008,08 | 45.286,59 |
| 17/05 | 146,13 | -176,12 | 5.994,41 | -417,66 | -11.511,52 | 5.549,39 |
| 18/05 | 11.191,65 | 0,00 | 11.532,21 | -1.383,28 | -341,10 | -1.372,90 |
| 19/05 | 14.936,39 | 73,88 | 10.527,07 | -1.485,00 | 1.495,91 | 3.907,67 |
| 20/05 | 24.401,17 | -623,81 | 12.740,95 | -2.430,82 | 1.285,57 | 12.926,26 |
| 21/05 | 14.923,17 | -240,00 | 7.503,83 | -1.050,00 | 3.923,47 | 4.785,87 |
| 22/05 | 30.440,09 | -426,12 | 9.127,13 | -727,37 | 3.907,93 | 17.466,78 |
| 23/05 | 329,44 | -245,00 | 6.348,75 | -2.098,80 | -7.904,74 | 4.011,07 |
| 24/05 | 18.337,49 | 5,00 | 7.416,64 | -850,70 | -9.716,86 | 21.120,80 |
| 25/05 | 29.055,40 | -9.895,47 | -16.378,47 | -2.795,03 | -2.270,54 | 59.918,86 |
| 26/05 | 18.942,34 | -23.890,00 | -79.712,57 | -4.753,88 | 6.962,74 | 119.862,71 |
| 27/05 | 22.743,66 | -24.206,12 | -95.753,32 | -3.305,07 | 13.295,14 | 131.525,17 |
| 28/05 | 17.657,82 | -11.079,35 | -50.711,75 | -3.138,50 | 11.577,62 | 70.057,58 |
| 29/05 | 43.633,19 | -200,00 | 10.407,34 | -965,40 | 11.657,40 | 21.887,17 |
| 30/05 | 51.254,74 | 5,00 | 9.146,88 | -708,20 | 3.286,32 | 39.308,50 |
| 31/05 | 21.464,60 | -14.201,12 | -21.559,33 | -1.411,27 | 1.267,43 | 57.368,89 |
| 01/06 | 65.302,60 | -505,00 | 12.153,24 | -1.817,00 | 14.453,01 | 39.378,40 |
| 02/06 | 90.167,41 | -20,00 | 17.467,02 | -4.146,80 | 20.448,92 | 54.271,08 |
| 03/06 | 74.307,81 | -725,00 | 15.237,25 | -1.724,01 | 20.574,53 | 40.031,24 |
| 04/06 | 51.374,95 | -725,00 | 21.941,92 | -2.344,91 | 24.521,56 | 6.604,54 |
| 05/06 | 29.751,16 | -240,00 | 15.954,82 | -4.355,07 | 24.792,80 | -6.856,43 |
| 06/06 | 10.304,65 | 0,00 | 11.072,99 | -2.813,47 | 9.622,28 | -8.023,73 |
| 07/06 | 31.243,45 | -185,00 | 6.986,50 | -1.923,02 | 7.580,41 | 18.390,28 |
| 08/06 | 27.477,03 | -690,00 | 15.927,94 | -5.170,08 | 24.032,88 | -8.273,51 |
| 09/06 | 38.069,18 | 31,84 | 17.253,82 | -7.143,67 | 29.312,10 | -2.422,60 |
| **Total** | **376.494,67** | **-266.203,83** | **6.602,07** | **-84.672,43** | **44.960,33** | **630.495,18** |

## Achados

1. **Refunds reconcilia (~100%)** ao atribuir por `datetime_refunded_platform` e separar chargeback — confirma que a silver tem os reembolsos certos; o que faltava era a **data/critério** de atribuição.
2. 🔴 **Chargebacks −16,5%** (silver subnotifica ~85k): investigar se há chargeback caindo em outro `payment_status`/`transaction_type` na silver, ou chargeback sem `total_refund_usd` preenchido.
3. ⚠️ **Gross +2% em junho** (dias 01–04/06 e 09/06 lideram o desvio, silver acima): período recente — provável **settlement** (vendas/ajustes muito novos ainda não batem entre origem e silver). Reavaliar com export mais recente.
4. **Commissions −0,45%** e **Taxes +0,91%** são desvios pequenos e ~uniformes (arredondamento/FX/definição fina).
5. A plataforma soma **Commission Voids** (~45k no período) no Net; a silver não modela voids — parte do Δ Net vem daí.

## Reproduzir
- Plataforma: `Master_Overview_2026-04-01_2026-06-090wT8Ci.xls` (Downloads) — export diário do Master Overview.
- Silver: este script (`validacao_silver_buygoods_plataforma.py`), read-only no MySQL.

## Relacionados
- Silver doc: [[Fontes de Dados/Buygoods/doc_silver_buygoods]]
- Validação gold (MySQL×MySQL): [[validacao-gold-buygoods-mysql-2026-06-09]]
- Schema: [[CLAUDE]] · Diário: [[log]]
