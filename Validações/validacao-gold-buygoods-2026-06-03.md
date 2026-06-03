---
tipo: validacao
par: dashboard_gold_buygoods (MySQL) x tb_gex_gold_buygoods (Athena)
data: 2026-06-03
gerado_por: Validações/validacao_gold_buygoods.py
tags: [validacao, reconciliacao, buygoods, gold]
---
# Validação — `dashboard_gold_buygoods` (MySQL) × `tb_gex_gold_buygoods` (Athena)

> Reconciliação completa rodada em **2026-06-03**. Somente leitura nas duas pontas.
> MySQL: `instituto_experience.dashboard_gold_buygoods` (gerada por procedure).
> Athena: `gex_db_prod_gold.tb_gex_gold_buygoods` (camada gold do data lake).

## Veredito

### ✅ TABELAS IGUAIS

| Bloco | Resultado |
|---|---|
| Contagem de linhas | ✅ (MySQL 226,001 / Athena 226,001) |
| `transaction_id` distintos | ✅ (MySQL 226,001 / Athena 226,001) |
| Medidas numéricas (somas) | ✅ |
| Quebra por dia | ✅ |
| `transaction_id` só no MySQL | ✅ 0 |
| `transaction_id` só no Athena | ✅ 0 |

## 1. Contagens e período

| Métrica | MySQL | Athena | Diferença | Status |
|---|--:|--:|--:|:--:|
| Linhas (grão) | 226,001 | 226,001 | +0 | ✅ |
| `transaction_id` distintos | 226,001 | 226,001 | +0 | ✅ |
| Dias distintos (`created_at_date`) | 65 | 65 | +0 | ✅ |
| Data mínima | 2026-03-31 | 2026-03-31 | — | ✅ |
| Data máxima | 2026-06-03 | 2026-06-03 | — | ✅ |

## 2. Medidas numéricas (soma total de cada coluna)

| Coluna | MySQL | Athena | Diferença | % | Status |
|---|--:|--:|--:|--:|:--:|
| `product_cost` | 54,992,270.7575 | 54,992,270.7575 | +0.0000 | +0.0000% | ✅ |
| `product_cost_usd` | 10,993,630.00 | 10,993,630.00 | +0.00 | +0.0000% | ✅ |
| `quantity` | 2,198,726 | 2,198,726 | +0 | +0.0000% | ✅ |
| `quantity_principal` | 1,136,072 | 1,136,072 | +0 | +0.0000% | ✅ |
| `total_price` | 441,989,862.9019 | 441,989,862.9019 | +0.0000 | +0.0000% | ✅ |
| `total_price_usd` | 88,368,439.39 | 88,368,439.39 | +0.00 | +0.0000% | ✅ |
| `taxes` | 38,308,020.5587 | 38,308,020.5587 | +0.0000 | +0.0000% | ✅ |
| `taxes_usd` | 7,659,490.92 | 7,659,490.92 | +0.00 | +0.0000% | ✅ |
| `total_refund` | 48,705,774.3101 | 48,705,774.3101 | +0.0000 | +0.0000% | ✅ |
| `total_refund_usd` | 9,750,504.30 | 9,750,504.30 | +0.00 | +0.0000% | ✅ |
| `commission` | 159,025,476.7841 | 159,025,476.7841 | +0.0000 | +0.0000% | ✅ |
| `commission_usd` | 31,787,894.35 | 31,787,894.35 | +0.00 | +0.0000% | ✅ |
| `affiliate_amount` | 248,587,416.1649 | 248,587,416.1649 | +0.0000 | +0.0000% | ✅ |
| `affiliate_amount_usd` | 49,708,598.07 | 49,708,598.07 | +0.00 | +0.0000% | ✅ |
| `revenue_afiliado` | 3,463,066.0570 | 3,463,066.0570 | +0.0000 | +0.0000% | ✅ |
| `revenue_afiliado_usd` | 692,930.00 | 692,930.00 | +0.00 | +0.0000% | ✅ |
| `has_upsell` | 60,654 | 60,654 | +0 | +0.0000% | ✅ |
| `has_upsell2` | 28,366 | 28,366 | +0 | +0.0000% | ✅ |
| `has_upsell3` | 5,649 | 5,649 | +0 | +0.0000% | ✅ |
| `has_downsell` | 19,537 | 19,537 | +0 | +0.0000% | ✅ |
| `has_downsell2` | 8,069 | 8,069 | +0 | +0.0000% | ✅ |
| `has_downsell3` | 1,053 | 1,053 | +0 | +0.0000% | ✅ |
| `has_order_bump` | 0 | 0 | +0 | — | ✅ |
| `total_price_upsell` | 99,222,004.73 | 99,222,004.73 | +0.00 | +0.0000% | ✅ |
| `total_price_upsell_usd` | 19,836,245.70 | 19,836,245.70 | +0.00 | +0.0000% | ✅ |
| `total_price_upsell2` | 24,815,119.79 | 24,815,119.79 | +0.00 | +0.0000% | ✅ |
| `total_price_upsell2_usd` | 4,959,299.40 | 4,959,299.40 | +0.00 | +0.0000% | ✅ |
| `total_price_upsell3` | 2,733,582.83 | 2,733,582.83 | +0.00 | +0.0000% | ✅ |
| `total_price_upsell3_usd` | 545,211.00 | 545,211.00 | +0.00 | +0.0000% | ✅ |
| `total_price_downsell` | 17,217,413.37 | 17,217,413.37 | +0.00 | +0.0000% | ✅ |
| `total_price_downsell_usd` | 3,439,158.54 | 3,439,158.54 | +0.00 | +0.0000% | ✅ |
| `total_price_downsell2` | 3,780,988.34 | 3,780,988.34 | +0.00 | +0.0000% | ✅ |
| `total_price_downsell2_usd` | 755,666.28 | 755,666.28 | +0.00 | +0.0000% | ✅ |
| `total_price_downsell3` | 346,791.89 | 346,791.89 | +0.00 | +0.0000% | ✅ |
| `total_price_downsell3_usd` | 68,995.00 | 68,995.00 | +0.00 | +0.0000% | ✅ |
| `total_price_order_bump` | 0.00 | 0.00 | +0.00 | — | ✅ |
| `total_price_order_bump_usd` | 0.00 | 0.00 | +0.00 | — | ✅ |
| `is_house_traffic` | 2,787 | 2,787 | +0 | +0.0000% | ✅ |
| `total_collected_usd` | 93,218,986.56 | 93,218,986.56 | +0.00 | +0.0000% | ✅ |
| `iva` | 24,264,416.6709 | 24,264,416.6709 | +0.0000 | +0.0000% | ✅ |
| `iva_usd` | 4,852,673.61 | 4,852,673.61 | +0.00 | +0.0000% | ✅ |
| `refund_fee` | 191,367.7987 | 191,367.7987 | +0.0000 | +0.0000% | ✅ |
| `refund_fee_usd` | 38,302.00 | 38,302.00 | +0.00 | +0.0000% | ✅ |
| `chargeback_fee` | 178,036.8065 | 178,036.8065 | +0.0000 | +0.0000% | ✅ |
| `chargeback_fee_usd` | 35,735.00 | 35,735.00 | +0.00 | +0.0000% | ✅ |

## 3. Quebra por dia

✅ Todos os **66 dias** batem em contagem e em `SUM(total_price_usd)`.

## 4. Reconciliação por `transaction_id`

| | Quantidade |
|---|--:|
| Distintos no MySQL | 226,001 |
| Distintos no Athena | 226,001 |
| Em ambos (interseção) | 226,001 |
| **Só no MySQL** | 0 |
| **Só no Athena** | 0 |

## 5. Schema

Ambas têm **75 colunas com os mesmos nomes**. Diferença esperada só na representação de tipo: 
MySQL usa `text/mediumtext/longtext` p/ strings e `date` p/ `created_at_date`; no Athena são `string` 
e `created_at_date` é **chave de partição**. Não é divergência de dados.

## 6. Conclusão

As duas tabelas representam **os mesmos dados** em todos os ângulos checados (linhas, transações distintas, somas de todas as medidas, quebra diária e conjunto de `transaction_id`).

## Relacionados
[[00-Data-Lake]] · [[00-Indice]] · `gex_db_prod_gold/tb_gex_gold_buygoods` · procedure que gera `dashboard_gold_buygoods`
