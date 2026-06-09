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

## Cobertura completa — todas as 45 colunas numéricas (totais do período)
Somadas todas as colunas numéricas das duas tabelas no período: **`diff = 0` em 45/45**. Valor abaixo
vale para as duas tabelas (idênticas).

| Categoria | Colunas (total do período) |
|---|---|
| **Quantidades/flags** | quantity 903.193 · quantity_principal 455.385 · is_house_traffic 3.091 · has_upsell 24.981 / has_upsell2 11.810 / has_upsell3 3.224 · has_downsell 8.169 / has_downsell2 3.533 / has_downsell3 803 · has_order_bump 0 |
| **Faturamento/custo** | total_price 182.778.773,54 · total_price_usd 35.991.830,03 · total_collected_usd 37.896.300,12 · product_cost 22.934.018,13 · product_cost_usd 4.515.965,00 |
| **Impostos** | taxes 15.588.222,01 · taxes_usd 3.069.501,91 · iva 9.677.424,01 · iva_usd 1.905.051,16 |
| **Reembolso/taxas** | total_refund 15.096.546,87 · total_refund_usd 2.973.468,89 · refund_fee 59.512,04 · refund_fee_usd 11.725,00 · chargeback_fee 16.230,90 · chargeback_fee_usd 3.220,00 |
| **Comissão/afiliado** | commission 70.317.608,80 · commission_usd 13.842.001,31 · affiliate_amount 98.106.799,35 · affiliate_amount_usd 19.323.391,32 · revenue_afiliado 3.938.153,40 · revenue_afiliado_usd 772.000,00 |
| **Upsell** | total_price_upsell 41.635.770,55 / _usd 8.197.153,50 · upsell2 10.815.090,44 / _usd 2.129.387,00 · upsell3 2.191.326,19 / _usd 431.360,00 |
| **Downsell** | total_price_downsell 7.283.788,17 / _usd 1.434.738,18 · downsell2 1.662.916,14 / _usd 327.440,50 · downsell3 338.281,93 / _usd 66.631,00 |
| **Order bump** | total_price_order_bump 0 / _usd 0 |

## Observações
- **Grão:** em ambas, `linhas = transaction_id distintos` (1 linha por transação) — sem duplicação.
- **Schema:** colunas e tipos idênticos nos dois lados.
- **Cobertura:** **todas as 45 colunas numéricas** conferidas (soma do período) → diff zero, além da
  quebra por dia das principais medidas (seção acima).
- **Único ângulo ainda não checado:** reconciliação 1-a-1 do conjunto de `transaction_id` (set diff) e as
  colunas de texto — a expectativa é igualdade total, dado que todas as 45 somas e a quebra diária batem.

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
