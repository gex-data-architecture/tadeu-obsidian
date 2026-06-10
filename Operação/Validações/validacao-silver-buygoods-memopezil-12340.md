---
tipo: validacao
par: tb_gex_buygoods_unified (silver) x extrato BuyGoods — conta Memopezil (account_id=12340)
data: 2026-06-10
periodo_silver: 2026-04-01 a 2026-06-09
moeda: USD
gerado_por: Operação/Validações/validacao_silver_buygoods_memopezil.py
tags: [validacao, reconciliacao, buygoods, silver, conta, memopezil]
---
# Validação campo a campo — Memopezil (account_id=12340)

> Silver `tb_gex_buygoods_unified` × extrato diário da plataforma (Excel). Alinhamento: **Excel(D) = silver(D−1)** na base de **timestamp da plataforma**. Somente leitura.

## De-para (campo Excel → silver)

| Campo Excel | Campo silver | Status |
|---|---|---|
| Sales | `total_collected_usd` | ✅ reconcilia (~−0,7%) |
| Commissions | `affiliate_amount_usd` | ✅ reconcilia (~−0,6%) |
| Sale Taxes | `iva_usd` | ✅ reconcilia (~−0,6%) |
| Fees | `taxes_usd` | ✅ reconcilia (~−0,7%) |
| Refunds | `total_refund_usd` (não-chargeback) | ⚠️ −12,6% — **lag de refunds recentes** (mai/jun) |
| Chargebacks | `total_refund_usd + chargeback_fee_usd` (chargeback) | ⚠️ −7,7% (mesmo lag) |
| Sale Tax Refunds | `iva_usd` dos refunded | ⚠️ −7% (acompanha o refund/lag) |
| Fee Voids | — | ❌ **não derivável** — a BuyGoods raramente estorna a fee (mantém a taxa) |
| Commission Voids | — | ❌ **não derivável** — afiliado mantém a comissão; void é exceção |
| Amount / Balance | — | ⛔ settlement (inclui allowances/holds) — não-transacional |
| JV Percentage / Alerts / Shipping/Handling / Product Notes | — | ⛔ meta / sem dado financeiro na silver |

## Total do período (campo a campo)

| Campo | Plataforma (Excel) | Silver | Δ | Δ% |
|---|--:|--:|--:|--:|
| Sales | 22.246.827,47 | 22.099.941,26 | -146.886,21 | -0.66% |
| Commissions | 11.743.876,13 | 11.670.939,79 | -72.936,34 | -0.62% |
| Sale Taxes | 1.460.566,59 | 1.451.272,95 | -9.293,64 | -0.64% |
| Fees | 1.785.924,47 | 1.774.368,18 | -11.556,29 | -0.65% |
| Refunds | 3.408.708,43 | 2.977.419,48 | -431.288,95 | -12.65% |
| Chargebacks | 178.444,94 | 164.738,78 | -13.706,16 | -7.68% |
| Fee Voids | 156.104,52 | 255.626,86 | 99.522,34 | +63.75% |
| Sale Tax Refunds | 223.744,12 | 208.184,89 | -15.559,23 | -6.95% |
| Commission Voids | 5.639,05 | 1.490.144,84 | 1.484.505,79 | +26325.46% |

> ✅ **Sale-side reconcilia** (Sales/Commissions/Sale Taxes/Fees ~−0,65% uniforme). ⚠️ **Refunds/Chargebacks** divergem por **lag dos estornos recentes** (mai/jun) ainda não totalmente ingeridos. ❌ **Voids** (Commission/Fee) não são deriváveis: dependem da política de void da BuyGoods (comissão/fee em geral **não** são estornadas), enquanto a silver só tem o valor original — por isso somar "afiliado/fee dos estornados" superestima o void.

## Por dia — Δ silver − plataforma (USD)

> Diferença por campo e por dia (rotulado pela data do **Excel**; silver = D−1). Use para localizar divergências.

| Dia | Sales | Commissions | Sale Taxes | Fees | Refunds | Chargebacks | Fee Voids | Sale Tax Refunds | Commission Voids |
|---|---|---|---|---|---|---|---|---|---|
| 02/04 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| 16/04 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| 17/04 | 0,00 | 0,00 | 0,00 | 0,01 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| 18/04 | 0,00 | 0,00 | 0,00 | -0,02 | -7,00 | 0,00 | 0,00 | 0,00 | 635,00 |
| 19/04 | 0,00 | 0,00 | 0,00 | 0,02 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| 20/04 | 0,00 | 0,00 | 0,00 | 0,02 | -2,00 | 0,00 | 11,70 | 13,46 | 240,00 |
| 21/04 | 0,00 | 0,00 | 0,00 | 0,00 | -3,00 | 0,00 | 0,00 | 0,00 | 190,00 |
| 22/04 | 0,00 | 0,00 | 0,00 | 0,06 | -3,00 | 0,00 | 0,00 | 0,00 | 420,00 |
| 23/04 | 185,96 | 0,00 | 0,00 | 18,71 | -5,00 | 0,00 | 0,00 | 0,00 | 1.190,00 |
| 24/04 | 0,00 | 0,00 | 0,00 | 0,33 | -24,00 | 0,00 | 20,58 | 24,26 | 2.990,00 |
| 25/04 | 0,00 | 240,00 | 0,00 | 0,23 | -21,00 | 0,00 | 20,75 | 34,01 | 2.820,00 |
| 26/04 | 0,00 | -240,00 | 0,00 | 0,31 | -40,00 | 0,00 | 0,00 | 0,00 | 4.965,00 |
| 27/04 | 0,00 | 0,00 | 0,00 | 0,35 | -48,00 | 0,00 | 0,00 | 0,00 | 5.820,00 |
| 28/04 | 0,00 | 0,00 | 0,00 | 0,36 | -113,49 | 0,00 | 37,22 | 35,55 | 8.145,00 |
| 29/04 | 0,00 | 0,00 | 0,00 | 0,39 | -47,00 | 0,00 | 154,87 | 158,05 | 6.290,00 |
| 30/04 | 0,00 | 0,00 | 0,00 | 0,41 | 316,00 | 0,00 | 94,13 | 109,32 | 6.545,00 |
| 01/05 | 0,00 | 0,00 | 0,00 | 0,49 | -69,00 | 0,00 | 190,53 | 96,54 | 8.480,00 |
| 02/05 | 0,00 | 0,00 | 0,00 | -0,23 | -209,00 | 0,00 | 41,78 | 42,93 | 27.220,00 |
| 03/05 | 0,00 | 0,00 | 0,00 | -0,37 | -719,90 | 0,00 | -56,03 | -96,59 | 11.525,00 |
| 04/05 | 0,00 | 0,00 | 0,00 | -0,46 | -76,00 | 0,00 | 29,11 | -29,95 | 10.740,00 |
| 05/05 | 0,00 | 0,00 | 10,44 | -0,18 | 334,81 | 0,00 | 407,21 | 391,73 | 24.455,00 |
| 06/05 | 220,14 | 240,00 | 2,70 | 17,27 | -166,00 | 0,00 | 197,67 | 231,49 | 23.170,00 |
| 07/05 | -220,14 | -240,00 | -13,14 | -17,75 | -130,00 | 0,00 | 252,09 | 277,21 | 17.495,00 |
| 08/05 | 0,00 | -960,00 | 0,00 | -0,67 | -181,00 | 0,00 | 353,02 | 446,85 | 23.830,00 |
| 09/05 | 0,00 | 0,00 | 0,00 | -0,27 | -350,95 | -105,00 | 154,77 | 88,43 | 24.685,00 |
| 10/05 | 0,00 | 0,00 | 0,00 | -0,33 | -111,00 | 0,00 | 15,70 | -23,71 | 16.085,00 |
| 11/05 | 0,00 | 0,00 | 0,00 | -0,53 | 154,53 | 0,00 | 40,39 | -47,09 | 20.365,00 |
| 12/05 | 0,00 | -230,00 | 0,00 | -0,58 | -258,53 | 0,00 | 111,01 | -114,27 | 38.675,00 |
| 13/05 | 618,14 | -480,00 | 0,00 | 16,99 | -97,73 | 0,00 | 392,18 | 306,24 | 33.575,00 |
| 14/05 | 0,00 | 0,00 | 0,00 | -0,68 | -107,95 | 0,00 | 260,96 | 134,05 | 47.485,00 |
| 15/05 | 0,00 | 0,00 | 0,00 | -0,26 | -1.667,47 | 0,00 | 204,68 | 238,04 | 47.265,00 |
| 16/05 | 0,00 | 0,00 | 0,00 | -0,28 | 363,97 | 0,00 | 764,30 | 709,75 | 51.805,00 |
| 17/05 | 0,00 | 0,00 | 0,00 | -0,58 | -197,74 | 0,00 | 180,28 | 50,62 | 38.960,00 |
| 18/05 | 0,00 | 0,00 | 0,00 | -0,27 | -194,13 | 0,00 | 281,61 | 319,37 | 36.475,00 |
| 19/05 | 0,00 | 0,00 | 0,00 | -0,35 | -87,37 | 0,00 | 559,34 | 622,99 | 57.820,00 |
| 20/05 | 0,00 | -176,12 | 0,00 | -0,46 | -304,71 | 0,00 | 687,57 | 693,30 | 49.510,00 |
| 21/05 | 0,00 | 0,00 | 0,00 | -0,35 | -482,05 | 0,00 | 783,17 | 853,58 | 61.940,00 |
| 22/05 | 0,00 | 0,00 | 0,00 | -0,38 | -231,44 | 0,00 | 848,53 | 1.061,08 | 60.185,00 |
| 23/05 | 0,00 | 0,00 | 0,00 | -0,01 | -720,43 | 0,00 | 490,38 | 691,20 | 63.230,00 |
| 24/05 | 0,00 | 0,00 | 0,00 | 0,15 | -157,13 | 0,00 | 97,40 | 126,35 | 36.435,00 |
| 25/05 | 0,00 | 0,00 | 0,00 | -0,19 | -295,89 | 0,00 | 239,85 | 124,73 | 23.998,09 |
| 26/05 | -21.636,35 | -10.670,47 | -1.349,57 | -1.697,93 | -26.037,02 | -349,58 | -1.472,52 | -950,37 | 31.600,00 |
| 27/05 | -48.594,30 | -22.640,00 | -3.158,73 | -3.806,73 | -87.695,19 | -3.408,84 | -383,42 | -5.466,86 | 8.983,88 |
| 28/05 | -50.016,03 | -24.206,12 | -3.111,58 | -3.929,35 | -109.783,75 | -1.784,87 | 1.994,92 | -6.561,28 | 12.375,00 |
| 29/05 | -23.090,87 | -11.279,35 | -1.354,95 | -1.810,63 | -67.891,07 | -1.876,64 | 4.207,38 | -3.884,61 | 22.470,88 |
| 30/05 | 0,00 | 0,00 | 0,00 | 0,07 | -21.567,13 | 0,00 | 8.152,02 | -771,54 | 46.620,65 |
| 31/05 | 0,00 | 0,00 | 0,00 | -0,08 | -6.588,39 | 0,00 | 4.338,43 | -480,54 | 26.630,00 |
| 01/06 | -4.352,76 | -2.076,12 | -318,81 | -342,69 | -13.072,70 | -354,73 | 2.883,43 | -630,61 | 17.485,00 |
| 02/06 | 0,00 | 0,00 | 0,00 | 0,07 | -15.581,09 | 0,00 | 7.659,49 | 90,22 | 46.153,88 |
| 03/06 | 0,00 | 0,00 | 0,00 | 0,06 | -12.884,98 | -252,95 | 9.330,91 | -635,44 | 57.968,88 |
| 04/06 | 0,00 | 0,00 | 0,00 | 0,05 | -12.304,45 | 0,00 | 9.756,10 | -338,58 | 53.380,00 |
| 05/06 | 0,00 | 0,00 | 0,00 | -0,03 | -13.463,99 | -698,43 | 9.388,83 | -719,54 | 52.875,65 |
| 06/06 | 0,00 | 0,00 | 0,00 | 0,07 | -11.689,29 | -156,98 | 9.929,52 | -481,81 | 55.585,00 |
| 07/06 | 0,00 | 0,00 | 0,00 | 0,04 | -5.376,02 | -1.210,48 | 4.884,61 | -543,25 | 27.770,00 |
| 08/06 | 0,00 | 0,00 | 0,00 | -0,06 | -651,51 | -647,91 | 3.615,40 | -204,28 | 21.628,88 |
| 09/06 | 0,00 | 0,00 | 0,00 | -0,08 | -9.767,57 | -350,32 | 8.808,32 | -555,80 | 55.740,00 |
| 10/06 | 0,00 | -218,16 | 0,00 | 0,03 | -10.975,20 | -2.509,43 | 8.562,17 | -994,46 | 51.580,00 |
| **Total** | **-146.886,21** | **-72.936,34** | **-9.293,64** | **-11.556,29** | **-431.288,95** | **-13.706,16** | **99.522,34** | **-15.559,23** | **1.484.505,79** |

## Observações

1. **Alinhamento crítico:** o Excel rotula o dia **D** com dados de **D−1**; e a silver precisa ser lida pelo `datetime_platform`/`datetime_refunded_platform` (o `created_at_date` está +1h e desalinha dias movimentados).
2. **Nomes "trocados" na silver:** o que a plataforma chama de **Commissions** (afiliado) é o `affiliate_amount_usd`; o **Amount** (líquido do vendor) é o `commission_usd`; e **Fees** (taxa BuyGoods) é o `taxes_usd`.
3. **Refunds/Chargebacks têm lag:** o início do período bate, mas os estornos de **fim de maio/junho** estão subnotificados na silver (ex.: 28/05 plataforma 132k vs silver 22k) — o pipeline de refund ainda não terminou de ingerir os estornos recentes. Reavaliar com um snapshot mais novo.
4. **Voids não são deriváveis da silver:** Commission Voids e Fee Voids dependem da **política da BuyGoods** (em geral comissão e fee NÃO são estornadas no refund). A plataforma reporta voids ~0; a silver só tem o valor original, então qualquer fórmula "imposto/fee/afiliado dos estornados" superestima.
5. **Amount/Balance** não são comparáveis: incluem **allowances/holds** (reservas) lançados pela BuyGoods, que não existem na base transacional.

## Reproduzir
- Plataforma: `Transactions_06-10-2026_450_12340.xlsx` (Downloads).
- Silver: este script (`validacao_silver_buygoods_memopezil.py`), read-only no MySQL.

## Relacionados
- Validação agregada (plataforma): [[validacao-silver-buygoods-plataforma-2026-06-09]]
- Silver doc: [[Fontes de Dados/Buygoods/doc_silver_buygoods]] · [[CLAUDE]] · [[log]]
