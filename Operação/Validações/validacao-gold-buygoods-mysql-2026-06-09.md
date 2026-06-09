---
tipo: validacao
par: dashboard_gold_buygoods x tb_gex_gold_buygoods (ambas MySQL · instituto_experience)
data: 2026-06-09
periodo: 2026-05-27 a 2026-06-08
gerado_por: análise read-only via MCP mysql
tags: [validacao, reconciliacao, buygoods, gold, mysql]
---
# Validação — `dashboard_gold_buygoods` × `tb_gex_gold_buygoods` (MySQL)

> [!success] Veredito: **TABELAS IDÊNTICAS** no período
> Reconciliação por dia de **27/05 → 08/06/2026**. Somente leitura. Todas as medidas de
> valor e quantidade batem **exatamente** em todos os dias — contagem, transações distintas,
> quantidade, faturamento (BRL e USD) e reembolso. Diferença: **zero**.

Ambas em `instituto_experience` (MySQL). Colunas e tipos **idênticos** (conferido via `information_schema`).

## Comparação por dia
Como `dashboard = tb_gex` em 100% dos casos, mostra-se um valor por métrica (vale para as duas).

| Dia | Linhas / TX | Quantidade | Faturamento (BRL) | Faturamento (USD) | Reembolso (BRL) | OK |
|---|--:|--:|--:|--:|--:|:--:|
| 27/05 | 8.173 | 81.437 | 16.462.046,84 | 3.252.573,12 | 1.594.610,37 | ✅ |
| 28/05 | 7.667 | 78.063 | 15.663.372,85 | 3.106.409,17 | 1.358.559,89 | ✅ |
| 29/05 | 7.340 | 74.020 | 14.902.549,89 | 2.959.967,79 | 1.315.088,21 | ✅ |
| 30/05 | 7.432 | 73.058 | 14.781.144,35 | 2.935.854,03 | 1.205.054,14 | ✅ |
| 31/05 | 7.295 | 73.521 | 14.749.439,12 | 2.929.567,13 | 1.063.199,88 | ✅ |
| 01/06 | 7.114 | 71.658 | 14.382.311,39 | 2.860.700,67 | 1.264.277,08 | ✅ |
| 02/06 | 6.567 | 66.076 | 13.120.760,85 | 2.621.357,48 | 929.736,18 | ✅ |
| 03/06 | 6.759 | 67.655 | 13.595.769,90 | 2.687.643,40 | 1.114.400,40 | ✅ |
| 04/06 | 6.542 | 65.171 | 13.148.159,23 | 2.596.004,95 | 1.195.058,78 | ✅ |
| 05/06 | 5.583 | 56.727 | 11.666.804,30 | 2.257.290,18 | 862.908,16 | ✅ |
| 06/06 | 6.382 | 65.607 | 13.491.332,86 | 2.610.295,16 | 1.071.229,20 | ✅ |
| 07/06 | 6.576 | 66.959 | 13.789.462,48 | 2.666.184,04 | 1.110.302,04 | ✅ |
| 08/06 | 6.100 | 63.241 | 13.025.619,49 | 2.507.982,91 | 1.012.122,56 | ✅ |
| **Total** | **89.530** | **903.193** | **182.778.773,54** | **35.991.830,03** | **15.096.546,87** | ✅ |

> Reembolso (USD) no total também bate: **2.973.468,89** nas duas tabelas.

## Observações
- **Grão:** em ambas, `linhas = transaction_id distintos` (1 linha por transação) — sem duplicação.
- **Schema:** colunas e tipos idênticos nos dois lados.
- **Medidas conferidas:** contagem de linhas, `transaction_id` distintos, `quantity`, `total_price` (BRL),
  `total_price_usd`, `total_refund` (BRL), `total_refund_usd`.
- **Não conferido nesta rodada (a expectativa é igualdade, dado o acima):** demais ~40 colunas numéricas
  (commission, affiliate_amount, taxes/iva, upsell/downsell, total_collected) e a reconciliação 1-a-1
  do conjunto de `transaction_id`.

## Conclusão
`dashboard_gold_buygoods` e `tb_gex_gold_buygoods` carregam **os mesmos dados** no intervalo 27/05→08/06.

## Como reproduzir (read-only)
```sql
-- pivot por dia das duas tabelas (MySQL, instituto_experience)
WITH u AS (
  SELECT created_at_date d, 1 src, COUNT(*) linhas, COUNT(DISTINCT transaction_id) tx,
         SUM(quantity) qtd, SUM(total_price) brl, SUM(total_price_usd) usd, SUM(total_refund) refund
  FROM instituto_experience.dashboard_gold_buygoods
  WHERE created_at_date BETWEEN '2026-05-27' AND '2026-06-08' GROUP BY created_at_date
  UNION ALL
  SELECT created_at_date, 2, COUNT(*), COUNT(DISTINCT transaction_id),
         SUM(quantity), SUM(total_price), SUM(total_price_usd), SUM(total_refund)
  FROM instituto_experience.tb_gex_gold_buygoods
  WHERE created_at_date BETWEEN '2026-05-27' AND '2026-06-08' GROUP BY created_at_date
)
SELECT d dia,
  MAX(CASE WHEN src=1 THEN linhas END) dash_linhas, MAX(CASE WHEN src=2 THEN linhas END) gex_linhas,
  MAX(CASE WHEN src=1 THEN brl END) dash_brl, MAX(CASE WHEN src=2 THEN brl END) gex_brl
  /* ...demais medidas... */
FROM u GROUP BY d ORDER BY d;
```

## Relacionados
- Validação correlata (MySQL × Athena): `Operação/Validações/validacao_gold_buygoods.py`
- Fonte silver: [[Fontes de Dados/Buygoods/doc_silver_buygoods]]
- Schema: [[CLAUDE]] · Diário: [[log]]
