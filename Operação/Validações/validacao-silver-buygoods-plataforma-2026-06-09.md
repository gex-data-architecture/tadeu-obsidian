---
tipo: validacao
par: tb_gex_buygoods_unified (silver MySQL) x plataforma BuyGoods (Master Overview)
data: 2026-06-09
periodo: 2026-04-01 a 2026-06-09
moeda: USD
gerado_por: Operação/Validações/validacao_silver_buygoods_plataforma.py
tags: [validacao, reconciliacao, buygoods, silver, plataforma]
---
# Validação — silver `tb_gex_buygoods_unified` × plataforma BuyGoods

> Reconciliação dos KPIs do **Master Overview** (01/04→09/06/2026, USD) contra a silver no MySQL.
> Somente leitura. A silver **reproduz a plataforma dentro de ~0,3%–1,2%** por KPI — diferenças de definição/atribuição de data/fuso, **não** de dados faltando.

## De-para descoberto (campo da silver por KPI)

| KPI (plataforma) | Definição na silver |
|---|---|
| **Gross Sales** | `SUM(total_price_usd - iva_usd)` por `created_at_date` |
| **Refunds & Chargebacks** | `SUM(total_refund_usd)` por **`date_refunded`** (não pela data da venda) |
| **Commissions** | `SUM(affiliate_amount_usd)` (todas as linhas) por `created_at_date` |
| **Taxes** | `SUM(iva_usd)` das vendas `payment_status=approved` (não o `taxes_usd`) |
| **Net Sales** | `Gross − Refunds − Commissions − Taxes` (calculado) |

## Geral (total do período)

| KPI | Plataforma (USD) | Silver (USD) | Δ | Δ% |
|---|--:|--:|--:|--:|
| Gross Sales | 98.681.080,46 | 98.966.270,80 | 285.190,34 | +0.29% |
| Refunds & Chargebacks | 13.624.448,77 | 13.460.386,47 | -164.062,30 | -1.20% |
| Commissions | 59.750.058,50 | 59.478.848,06 | -271.210,44 | -0.45% |
| Taxes | 4.940.464,79 | 4.980.909,45 | 40.444,66 | +0.82% |
| Net Sales (calc) | 20.366.108,40 | 21.046.126,82 | 680.018,42 | +3.34% |

> **Net** acumula mais desvio relativo (+3,3%) por ser um **resíduo pequeno de números grandes** — os erros de cada componente se somam. Gross/Refunds/Commissions/Taxes ficam todos ≤1,2%.

## Por dia (lado silver — USD)

> A plataforma só forneceu o **total** do período (tela do Master Overview); os valores **diários** abaixo são da silver, com **Net calculado**. O comparativo diário plataforma×silver será fechado quando chegar o Excel.

| Dia | Gross | Refunds & CB | Commissions | Taxes | **Net (calc)** |
|---|--:|--:|--:|--:|--:|
| 01/04 | 22.807,85 | 583,71 | 15.290,16 | 1.198,15 | 5.735,83 |
| 02/04 | 15.962,05 | 1.225,92 | 10.505,15 | 1.043,39 | 3.187,59 |
| 03/04 | 14.375,88 | 1.021,67 | 9.519,94 | 704,99 | 3.129,28 |
| 04/04 | 22.411,52 | 2.250,45 | 11.946,78 | 1.401,63 | 6.812,66 |
| 05/04 | 11.868,54 | 79,00 | 7.005,49 | 566,48 | 4.217,57 |
| 06/04 | 23.264,37 | 2.716,82 | 12.628,43 | 1.392,03 | 6.527,09 |
| 07/04 | 18.473,38 | 1.306,39 | 11.055,23 | 1.372,48 | 4.739,28 |
| 08/04 | 26.214,44 | 2.044,79 | 15.293,89 | 1.596,45 | 7.279,31 |
| 09/04 | 48.233,93 | 5.184,83 | 29.993,92 | 2.620,07 | 10.435,11 |
| 10/04 | 64.257,37 | 5.945,74 | 41.255,85 | 3.734,09 | 13.321,69 |
| 11/04 | 76.126,02 | 5.351,35 | 46.782,24 | 4.326,58 | 19.665,85 |
| 12/04 | 297.144,75 | 11.530,90 | 165.700,79 | 11.674,24 | 108.238,82 |
| 13/04 | 241.186,13 | 18.087,00 | 144.172,34 | 9.079,77 | 69.847,02 |
| 14/04 | 273.975,51 | 23.564,58 | 175.589,05 | 10.789,32 | 64.032,56 |
| 15/04 | 319.751,02 | 30.596,26 | 204.982,43 | 13.604,71 | 70.567,62 |
| 16/04 | 332.288,93 | 28.207,22 | 219.191,21 | 15.318,55 | 69.571,95 |
| 17/04 | 190.291,96 | 27.144,91 | 123.913,16 | 9.518,86 | 29.715,03 |
| 18/04 | 182.295,25 | 11.765,03 | 129.664,94 | 9.388,64 | 31.476,64 |
| 19/04 | 241.134,15 | 9.418,29 | 166.091,86 | 10.914,39 | 54.709,61 |
| 20/04 | 247.849,74 | 21.095,68 | 167.996,61 | 11.769,12 | 46.988,33 |
| 21/04 | 298.666,22 | 28.235,12 | 191.755,23 | 15.388,94 | 63.286,93 |
| 22/04 | 359.366,20 | 35.063,04 | 225.602,47 | 18.375,42 | 80.325,27 |
| 23/04 | 475.122,75 | 41.836,83 | 279.603,36 | 25.705,41 | 127.977,15 |
| 24/04 | 487.382,46 | 45.552,40 | 296.332,20 | 25.968,80 | 119.529,06 |
| 25/04 | 767.270,36 | 37.113,59 | 488.906,75 | 40.492,61 | 200.757,41 |
| 26/04 | 941.311,27 | 42.374,00 | 597.030,01 | 47.538,95 | 254.368,31 |
| 27/04 | 921.777,81 | 75.802,74 | 583.110,29 | 45.712,74 | 217.152,04 |
| 28/04 | 1.020.539,50 | 67.166,48 | 649.897,76 | 49.456,61 | 254.018,65 |
| 29/04 | 955.569,55 | 73.881,55 | 615.636,23 | 45.523,87 | 220.527,90 |
| 30/04 | 933.466,77 | 82.377,97 | 579.014,76 | 44.951,74 | 227.122,30 |
| 01/05 | 1.067.591,76 | 202.625,66 | 647.628,77 | 53.441,85 | 163.895,48 |
| 02/05 | 1.267.704,75 | 96.730,49 | 782.891,34 | 63.837,37 | 324.245,55 |
| 03/05 | 1.446.199,37 | 78.548,20 | 920.497,24 | 70.040,36 | 377.113,57 |
| 04/05 | 1.339.858,62 | 155.168,51 | 842.742,92 | 68.096,35 | 273.850,84 |
| 05/05 | 1.197.715,17 | 145.780,59 | 761.671,77 | 60.955,01 | 229.307,80 |
| 06/05 | 1.213.536,52 | 158.919,87 | 776.105,03 | 61.271,64 | 217.239,98 |
| 07/05 | 1.487.786,16 | 180.722,79 | 932.794,67 | 79.298,86 | 294.969,84 |
| 08/05 | 1.385.402,49 | 173.890,75 | 846.330,78 | 67.704,40 | 297.476,56 |
| 09/05 | 1.667.328,59 | 119.637,13 | 1.039.172,94 | 82.045,02 | 426.473,50 |
| 10/05 | 1.675.045,80 | 101.671,85 | 995.140,74 | 85.899,26 | 492.333,95 |
| 11/05 | 1.676.799,50 | 219.810,74 | 1.032.496,09 | 88.610,60 | 335.882,07 |
| 12/05 | 1.931.567,25 | 201.493,42 | 1.187.932,85 | 101.175,19 | 440.965,79 |
| 13/05 | 1.981.358,18 | 243.293,86 | 1.194.401,50 | 105.072,73 | 438.590,09 |
| 14/05 | 1.964.565,56 | 267.934,81 | 1.173.153,28 | 102.778,55 | 420.698,92 |
| 15/05 | 1.815.058,56 | 284.145,74 | 1.099.929,55 | 91.349,60 | 339.633,67 |
| 16/05 | 2.340.535,65 | 222.604,30 | 1.373.311,54 | 119.110,97 | 625.508,84 |
| 17/05 | 2.653.525,88 | 182.237,42 | 1.557.005,53 | 133.293,97 | 780.988,96 |
| 18/05 | 2.301.730,94 | 352.071,78 | 1.376.919,24 | 118.561,81 | 454.178,11 |
| 19/05 | 2.316.536,96 | 315.708,45 | 1.370.568,81 | 118.862,69 | 511.397,01 |
| 20/05 | 2.434.880,84 | 365.583,03 | 1.450.894,51 | 121.182,78 | 497.220,52 |
| 21/05 | 2.472.921,34 | 350.536,40 | 1.469.070,60 | 123.281,60 | 530.032,74 |
| 22/05 | 2.570.735,56 | 375.419,62 | 1.523.627,69 | 125.732,86 | 545.955,39 |
| 23/05 | 3.217.148,84 | 294.107,84 | 1.911.872,84 | 155.054,63 | 856.113,53 |
| 24/05 | 3.146.171,70 | 170.941,95 | 1.923.776,63 | 148.727,88 | 902.725,24 |
| 25/05 | 3.189.229,44 | 304.011,64 | 1.893.583,50 | 155.121,60 | 836.512,70 |
| 26/05 | 3.340.396,39 | 353.328,40 | 1.954.015,14 | 161.947,36 | 871.105,49 |
| 27/05 | 3.079.518,16 | 456.334,28 | 1.844.280,26 | 149.489,08 | 629.414,54 |
| 28/05 | 2.944.832,50 | 432.539,62 | 1.732.573,78 | 146.402,79 | 633.316,31 |
| 29/05 | 2.804.630,16 | 488.822,97 | 1.656.247,71 | 139.580,04 | 519.979,44 |
| 30/05 | 2.784.886,42 | 299.979,24 | 1.668.479,84 | 139.102,96 | 677.324,38 |
| 31/05 | 2.775.529,46 | 177.398,04 | 1.640.755,46 | 139.844,34 | 817.531,62 |
| 01/06 | 2.712.951,46 | 473.091,33 | 1.586.782,10 | 133.934,65 | 519.143,38 |
| 02/06 | 2.481.993,68 | 574.039,10 | 1.441.621,75 | 123.486,45 | 342.846,38 |
| 03/06 | 2.549.329,04 | 567.623,54 | 1.505.058,01 | 126.731,41 | 349.916,08 |
| 04/06 | 2.459.577,55 | 654.717,61 | 1.463.752,82 | 126.222,40 | 214.884,72 |
| 05/06 | 2.136.477,13 | 667.098,17 | 1.257.477,00 | 112.178,67 | 99.723,29 |
| 06/06 | 2.462.791,13 | 374.247,19 | 1.446.443,19 | 134.143,63 | 507.957,12 |
| 07/06 | 2.516.706,53 | 312.275,14 | 1.477.797,88 | 132.831,51 | 593.802,00 |
| 08/06 | 2.373.743,07 | 629.310,62 | 1.370.651,52 | 125.757,61 | 248.023,32 |
| 09/06 | 1.951.587,01 | 697.460,12 | 1.133.922,71 | 107.619,94 | 12.584,24 |
| **Total** | **98.966.270,80** | **13.460.386,47** | **59.478.848,06** | **4.980.909,45** | **21.046.126,82** |

## Observações

- **Mapeamento não é óbvio:** "Taxes" = `iva_usd` (o `taxes_usd` somaria ~9M, ~2x); "Commissions" = `affiliate_amount_usd` (o `commission_usd` é ~37M, é outro conceito — provável valor do vendor/fee).
- **Reembolso é por `date_refunded`:** trocar a data de atribuição derrubou o erro de **−4,0% para −1,2%** (reembolsos de vendas antigas processados dentro do período).
- **Resíduos com assinatura de fuso:** `created_at` é `timestamp`; a plataforma agrupa o "dia" no fuso dela. Nas bordas de cada dia, transações caem em dias diferentes → gap pequeno e bidirecional ao longo de 70 dias. Some FX/arredondamento.
- **Tipos de transação na silver:** Sale, Cancel, Chargeback, Refund, Fulfillment, Rebill — a plataforma filtra/atribui por tipo (Gross líquido de IVA; Taxes só de approved).
- **Grão:** 1 linha por `transaction_id` (411.186 linhas = 411.186 tx no período).

## ⚠️ Pendências para fechar ao centavo
- **Excel da conta master** (valores diários e por campo) → reconciliação diária plataforma×silver e validação além dos 5 KPIs (por produto/oferta/afiliado).
- Confirmar o **fuso** usado pela plataforma para fechar o dia (provável causa dos resíduos de borda).

## Como reproduzir (read-only)
```sql
WITH s AS (
  SELECT created_at_date d,
         SUM(total_price_usd - iva_usd) gross,
         SUM(affiliate_amount_usd) commissions,
         SUM(CASE WHEN payment_status='approved' THEN iva_usd ELSE 0 END) taxes
  FROM instituto_experience.tb_gex_buygoods_unified
  WHERE created_at_date BETWEEN '2026-04-01' AND '2026-06-09'
  GROUP BY created_at_date
),
r AS (
  SELECT date_refunded d, SUM(total_refund_usd) refunds
  FROM instituto_experience.tb_gex_buygoods_unified
  WHERE date_refunded BETWEEN '2026-04-01' AND '2026-06-09'
  GROUP BY date_refunded
)
SELECT s.d AS dia,
  ROUND(s.gross,2) gross, ROUND(COALESCE(r.refunds,0),2) refunds,
  ROUND(s.commissions,2) commissions, ROUND(s.taxes,2) taxes,
  ROUND(s.gross - COALESCE(r.refunds,0) - s.commissions - s.taxes,2) net_calc
FROM s LEFT JOIN r ON r.d = s.d
ORDER BY s.d
```

## Relacionados
- Silver doc: [[Fontes de Dados/Buygoods/doc_silver_buygoods]]
- Validação gold (MySQL×MySQL): [[validacao-gold-buygoods-mysql-2026-06-09]]
- Schema: [[CLAUDE]] · Diário: [[log]]
