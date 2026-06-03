---
tipo: doc-tecnico
camada: gold
plataforma: Buygoods
tabela_alvo: dashboard_gold_buygoods
tabela_origem: tb_gex_buygoods_unified
versao: "2.0"
convertido_de: doc_gold_buygoods.docx
tags: [fonte, buygoods, gold, doc-tecnico]
---

# Especificação Técnica Oficial — Camada Gold (BuyGoods)
Camada Gold — Pipeline BuyGoods
gold_buygoods (agregação por compra)
| Versão | 2.0 — Nova fonte unified, agrupamento por janela temporal, refund bruto, UTMs do silver |
|---|---|
| Data | Junho 2026 |
| Status | Pronto para implementação |
| Tabela alvo | instituto_experience.dashboard_gold_buygoods |
| Tabela de origem | instituto_experience.tb_gex_buygoods_unified |
| Engine | MySQL 8 / MariaDB (funções TIMESTAMPDIFF, TIME_FORMAT, REGEXP, LAG/SUM OVER) |
| Granularidade | 1 linha por compra (purchase_group) |
| Chave primária | purchase_group_id (= client_email + account_id + grupo temporal) |
| Estratégia | Agregação por janela temporal de 240 min sobre (client_email, account_id) |
| Total de colunas | 75 (64 espelhadas da gold_clickbank + 11 exclusivas BuyGoods) |
| Ordem de colunas | Posições 1-64 IDÊNTICAS à gold_clickbank. Posições 65-75: novas colunas BG no final. |
| Conceito-chave | Agrupa múltiplos transaction_id da mesma sessão de checkout (PP + UP + DW + OB) em uma única linha consolidada |

## 1. Princípios Norteadores
🔄  PARIDADE COM CLICKBANK: A ordem das colunas 1-64 é IDÊNTICA à gold_clickbank, posição a posição. Isso permite UNION ALL direto entre as duas tabelas na camada de consumo. Colunas inexistentes no BuyGoods (coupon_code, src, vendor_name) são preenchidas com NULL para preservar a paridade. Os campos utm_* passaram a ser populados diretamente da silver unified (deixaram de ser NULL).
➕  COLUNAS EXCLUSIVAS NO FINAL: Colunas que só existem no BuyGoods (purchase_group_id, account_id, datetime_platform, total_collected_usd, iva/iva_usd, refund_fee, chargeback_fee, affiliate_id) ficam nas posições 65-75. Quando houver UNION com clickbank, basta selecionar até a posição 64 ou tratar essas colunas como NULL no lado CB.
🎯  GRANULARIDADE: A Gold consolida o nível "transação" da Silver para "compra". Uma compra contém o produto principal e seus upsells/downsells/order bumps adicionados no mesmo checkout, agrupados por uma janela temporal de 240 minutos sobre (client_email, account_id).
🔗  CHAVE DE AGRUPAMENTO: O agrupamento usa uma janela temporal de 240 minutos sobre (client_email, account_id). Transações do mesmo cliente e mesma conta cujo intervalo entre criações seja maior que 240 minutos iniciam um novo grupo de compra. A chave final purchase_group_id é a concatenação client_email + account_id + id sequencial do grupo temporal.
🏷️  CLASSIFICAÇÃO FUNNEL_TYPE: Cada linha da Silver é classificada como main, upsell1/2/3, downsell1/2/3, order_bump, funil_sem_offer ou other. Ordem de precedência: (1) offer_name (canônico no futuro), (2) product_codename (fallback técnico), (3) sales_type (fallback final).
💰  REFUND BRUTO: total_refund e total_refund_usd são a soma direta dos refunds da Silver (ROUND(SUM(total_refund))), sem dedução de iva e taxes. O estorno líquido de impostos deixou de ser calculado nesta versão; os campos representam o valor bruto devolvido. iva, taxes, refund_fee e chargeback_fee permanecem disponíveis em colunas próprias para reconstrução do líquido na camada de consumo.
🏠  HOUSE TRAFFIC: Quando is_house_traffic = 1 na Silver, commission absorve affiliate_amount, affiliate_amount é zerado, e o valor original é preservado em revenue_afiliado. O campo is_house_traffic na Gold é retornado como INT 0/1 (não boolean).
## 2. Lógica de Agrupamento
### 2.1 Chave de Agrupamento
GROUP BY client_email, account_id, purchase_group_id_final. O purchase_group_id_final é gerado por uma janela temporal: as transações são ordenadas por (created_at_ts, transaction_id) dentro de cada (client_email, account_id); sempre que o intervalo para a transação anterior ultrapassa 240 minutos (ou é a primeira), inicia-se um novo grupo. Cada grupo representa uma sessão de checkout no BuyGoods, incluindo o produto principal e todos os upsells/downsells/order bumps adicionados na mesma janela.
Alinhamento com o ClickBank: esta versão passa a usar a mesma heurística de janela temporal de 240 minutos do ClickBank. A diferença está na partição — aqui usa-se (client_email, account_id), enquanto o ClickBank usa (client_email, vendor_name). O campo upsell_parent_receipt deixou de ser usado como chave de agrupamento.
### 2.2 Classificação funnel_type (ordem de avaliação)
| Origem | Regra # | Lógica |
|---|---|---|
| offer_name | Regra 1 | sales_type = 'venda de funil' AND offer_name ILIKE '%upsell N%' / '%downsell N%' → upsellN / downsellN. sales_type = 'order bump' → order_bump. |
| product_codename | Regra 2 | Fallback técnico via regex: UP1_/UP2_/UP3_/DW1_/DW2_/DW3_/PP_ (com underscore) ou UP1N+, UP2N+, ..., PPN+ (concatenado). Captura sinal do funil quando offer_name ainda não está populado. |
| sales_type | Regra 3 | Fallback final: sales_type LIKE 'produto principal%' → main. sales_type = 'venda de funil' sem match → funil_sem_offer. Restante → other. |

Importante: o CASE WHEN avalia em ordem. A regra 1 (offer_name) vem primeiro porque é a fonte canônica futura. A regra 2 (codename) é o fallback intermediário e captura a maioria dos casos atuais. A regra 3 (sales_type) só atua quando nada mais resolveu, evitando que 99% das linhas caiam falsamente em "main".
## 3. Mapeamento Campo a Campo — Gold
As tabelas abaixo seguem EXATAMENTE a ordem de colunas da gold_clickbank (posições 1 a 64). As posições 65 a 75 contêm as novas colunas exclusivas do BuyGoods.
### 3.1 Identificação (posições 1-2)
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 1 | transaction_id | VARCHAR(20) | MIN(transaction_id) do grupo — escolhe um id representativo da compra. | AGREGADO |
| 2 | payment_status | VARCHAR(20) | Hierarquia: se todas as linhas têm o mesmo status → MAX(status). Se há chargeback no grupo → 'chargeback'. Caso contrário → 'refunded_partial'. | CALCULADO |

### 3.2 Dados do Cliente (posições 3-10)
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 3 | client_name | VARCHAR(200) | MAX(client_name) do grupo. Constante dentro de uma compra. | AGREGADO |
| 4 | client_email | VARCHAR(200) | Chave de agrupamento (GROUP BY). Constante dentro de uma compra. | AGREGADO |
| 5 | client_phone | VARCHAR(30) | MAX(client_phone) do grupo. | AGREGADO |
| 6 | client_zip | VARCHAR(20) | MAX(client_zip) do grupo. | AGREGADO |
| 7 | client_country | VARCHAR(60) | CASE sobre MAX(client_country): mapeia o código ISO de 2 letras para o nome do país por extenso (ex.: BR → Brazil, US → United States). Códigos não mapeados retornam o próprio MAX(client_country). | CALCULADO |
| 8 | client_state | VARCHAR(60) | MAX(client_state) do grupo. | AGREGADO |
| 9 | client_city | VARCHAR(60) | MAX(client_city) do grupo. | AGREGADO |
| 10 | client_street | VARCHAR(200) | MAX(client_street) do grupo. | AGREGADO |

### 3.3 Produto Principal e Quantidades (posições 11-17)
Os campos product_name, offer_name e product_sku referem-se ao produto da linha funnel_type = main. Quando há múltiplos mains no mesmo grupo (situação atual, antes do offer_name estar 100% preenchido), MAX() escolhe um representativo. Quando não há main no grupo, há fallback (COALESCE): herda o main do grupo de compra anterior do mesmo cliente/conta (main mais recente com grupo_ts <= início do grupo atual). Só retornam NULL se não houver nenhum main anterior.
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 11 | product_name | VARCHAR(200) | COALESCE( MAX(CASE WHEN funnel_type = 'main' THEN product_name END), main do grupo anterior do mesmo cliente/conta ). Se o grupo não tem main, herda o product_name do main mais recente (grupo_ts <= início do grupo atual) via subconsulta em main_por_grupo. | CALCULADO |
| 12 | offer_name | VARCHAR(500) | COALESCE( MAX(CASE WHEN funnel_type = 'main' THEN offer_name END), main_offer_name do grupo anterior ). Mesma lógica de herança do product_name quando o grupo não tem main. | CALCULADO |
| 13 | product_sku | VARCHAR(100) | COALESCE( MAX(CASE WHEN funnel_type = 'main' THEN product_sku END), main_product_sku do grupo anterior ). Mesma lógica de herança quando o grupo não tem main. | CALCULADO |
| 14 | product_cost | DECIMAL(12,4) | ROUND(SUM(product_cost), 4). Custo total da compra em BRL. | AGREGADO |
| 15 | product_cost_usd | DECIMAL(10,2) | ROUND(SUM(product_cost_usd), 2). Custo total em USD. | AGREGADO |
| 16 | quantity | INT | SUM(quantity) — soma de TODAS as unidades vendidas na compra (principal + upsells + bumps). | AGREGADO |
| 17 | quantity_principal | INT | MAX(CASE WHEN funnel_type = 'main' THEN quantity END). Apenas do produto principal. | CALCULADO |

### 3.4 Financeiro — Vendas e Impostos (posições 18-21)
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 18 | total_price | DECIMAL(12,4) | ROUND(SUM(total_price), 4). Preço de produto somado (BRL). | AGREGADO |
| 19 | total_price_usd | DECIMAL(10,2) | ROUND(SUM(total_price_usd), 2). Preço de produto somado (USD). | AGREGADO |
| 20 | taxes | DECIMAL(12,4) | ROUND(SUM(taxes), 4). Taxa de plataforma BuyGoods em BRL. | AGREGADO |
| 21 | taxes_usd | DECIMAL(10,2) | ROUND(SUM(taxes_usd), 2). Taxa de plataforma em USD. | AGREGADO |

### 3.5 Refunds — Valor Líquido (posições 22-23)
Os campos total_refund e total_refund_usd retornam o valor BRUTO — soma direta dos refunds da Silver, sem dedução de iva e taxes. A dedução de impostos (líquido) deixou de ser aplicada nesta versão.
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 22 | total_refund | DECIMAL(12,4) | ROUND(SUM(total_refund), 4). Refund bruto em BRL. | AGREGADO |
| 23 | total_refund_usd | DECIMAL(10,2) | ROUND(SUM(total_refund_usd), 2). Refund bruto em USD. | AGREGADO |

### 3.6 Comissão e Afiliado (posições 24-29)
A regra de is_house_traffic na Silver muda o comportamento. Em tráfego próprio (house traffic), commission absorve affiliate_amount e affiliate_amount é zerado. O valor original é preservado em revenue_afiliado para visão CPA/Afiliado.
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 24 | commission | DECIMAL(12,4) | ROUND( SUM(CASE WHEN is_house_traffic = 1 THEN COALESCE(commission, 0) + COALESCE(affiliate_amount, 0) ELSE commission END), 4 ). BRL. | CALCULADO |
| 25 | commission_usd | DECIMAL(10,2) | Mesma fórmula em USD, arredondado a 2 casas. | CALCULADO |
| 26 | affiliate_amount | DECIMAL(12,4) | ROUND( SUM(CASE WHEN is_house_traffic = 1 THEN 0 ELSE affiliate_amount END), 4 ). BRL. | CALCULADO |
| 27 | affiliate_amount_usd | DECIMAL(10,2) | Mesma fórmula em USD. | CALCULADO |
| 28 | revenue_afiliado | DECIMAL(12,4) | ROUND( SUM(CASE WHEN is_house_traffic = 1 THEN COALESCE(affiliate_amount, 0) ELSE 0 END), 4 ). Preserva affiliate_amount original em house traffic. BRL. | CALCULADO |
| 29 | revenue_afiliado_usd | DECIMAL(10,2) | Mesma fórmula em USD. | CALCULADO |

### 3.7 Flags de Funil (posições 30-36)
Indicam presença de cada tipo de upsell/downsell/order_bump no grupo. Valor é a contagem de linhas daquele tipo.
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 30 | has_upsell | INT | SUM(CASE WHEN funnel_type = 'upsell1' THEN 1 ELSE 0 END). | CALCULADO |
| 31 | has_upsell2 | INT | SUM(CASE WHEN funnel_type = 'upsell2' THEN 1 ELSE 0 END). | CALCULADO |
| 32 | has_upsell3 | INT | SUM(CASE WHEN funnel_type = 'upsell3' THEN 1 ELSE 0 END). | CALCULADO |
| 33 | has_downsell | INT | SUM(CASE WHEN funnel_type = 'downsell1' THEN 1 ELSE 0 END). | CALCULADO |
| 34 | has_downsell2 | INT | SUM(CASE WHEN funnel_type = 'downsell2' THEN 1 ELSE 0 END). | CALCULADO |
| 35 | has_downsell3 | INT | SUM(CASE WHEN funnel_type = 'downsell3' THEN 1 ELSE 0 END). | CALCULADO |
| 36 | has_order_bump | INT | SUM(CASE WHEN funnel_type = 'order_bump' THEN 1 ELSE 0 END). | CALCULADO |

### 3.8 Valor por Tipo de Funil (posições 37-50)
Permite responder "quanto faturei em upsell 1?", "qual o ticket médio de downsell 2?", etc. Cada par BRL e USD, arredondado a 2 casas.
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 37 | total_price_upsell | DECIMAL(12,2) | SUM(CASE WHEN funnel_type='upsell1' THEN total_price ELSE 0 END). BRL. | CALCULADO |
| 38 | total_price_upsell_usd | DECIMAL(10,2) | Idem em USD. | CALCULADO |
| 39 | total_price_upsell2 | DECIMAL(12,2) | Análogo para upsell2 (BRL). | CALCULADO |
| 40 | total_price_upsell2_usd | DECIMAL(10,2) | Análogo para upsell2 (USD). | CALCULADO |
| 41 | total_price_upsell3 | DECIMAL(12,2) | Análogo para upsell3 (BRL). | CALCULADO |
| 42 | total_price_upsell3_usd | DECIMAL(10,2) | Análogo para upsell3 (USD). | CALCULADO |
| 43 | total_price_downsell | DECIMAL(12,2) | Análogo para downsell1 (BRL). | CALCULADO |
| 44 | total_price_downsell_usd | DECIMAL(10,2) | Análogo para downsell1 (USD). | CALCULADO |
| 45 | total_price_downsell2 | DECIMAL(12,2) | Análogo para downsell2 (BRL). | CALCULADO |
| 46 | total_price_downsell2_usd | DECIMAL(10,2) | Análogo para downsell2 (USD). | CALCULADO |
| 47 | total_price_downsell3 | DECIMAL(12,2) | Análogo para downsell3 (BRL). | CALCULADO |
| 48 | total_price_downsell3_usd | DECIMAL(10,2) | Análogo para downsell3 (USD). | CALCULADO |
| 49 | total_price_order_bump | DECIMAL(12,2) | Análogo para order_bump (BRL). | CALCULADO |
| 50 | total_price_order_bump_usd | DECIMAL(10,2) | Análogo para order_bump (USD). | CALCULADO |

### 3.9 Datas, Cupom e Refund (posições 51-54)
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 51 | coupon_code | VARCHAR(100) | Sempre NULL no BuyGoods. Campo existe na gold_clickbank; preservado para paridade de schema. | NULL |
| 52 | created_at_date | DATE | DATE( MIN(created_at_ts) ), onde created_at_ts = TIMESTAMP(CONCAT(created_at_date, ' ', created_at_hour)). Data da primeira transação do grupo. | CALCULADO |
| 53 | created_at_hour | VARCHAR(8) | TIME_FORMAT( TIME(MIN(created_at_ts)), '%H:%i:%s' ). Hora da primeira transação. | CALCULADO |
| 54 | date_refunded | VARCHAR(19) | MAX(date_refunded) do grupo — última data em que houve refund/chargeback dentro da compra. | AGREGADO |

### 3.10 UTMs e Source (posições 55-60)
Os campos utm_* passaram a ser populados diretamente da silver unified (tb_gex_buygoods_unified) via MAX(utm_*). Apenas src permanece NULL no BuyGoods. As informações de atribuição complementares (affiliate_id) ficam nas colunas exclusivas (posições 65-75).
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 55 | utm_source | VARCHAR(200) | MAX(utm_source). Populado direto da silver unified. | AGREGADO |
| 56 | utm_medium | VARCHAR(200) | MAX(utm_medium). Populado direto da silver unified. | AGREGADO |
| 57 | utm_content | VARCHAR(200) | MAX(utm_content). Populado direto da silver unified. | AGREGADO |
| 58 | utm_term | VARCHAR(200) | MAX(utm_term). Populado direto da silver unified. | AGREGADO |
| 59 | utm_campaign | VARCHAR(200) | MAX(utm_campaign). Populado direto da silver unified. | AGREGADO |
| 60 | src | VARCHAR(200) | Sempre NULL no BuyGoods. | NULL |

### 3.11 Metadados (posições 61-64)
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 61 | platform | VARCHAR(20) | MAX(platform). No BuyGoods, sempre 'buygoods'. | AGREGADO |
| 62 | affiliate_name | VARCHAR(200) | MAX(affiliate_name) do grupo. | AGREGADO |
| 63 | vendor_name | VARCHAR(100) | Sempre NULL no BuyGoods (a coluna vendor_name está vazia no silver). Preservado para paridade de schema. | NULL |
| 64 | is_house_traffic | INT (0/1) | CAST(MAX(CASE WHEN is_house_traffic = 1 THEN 1 ELSE 0 END) AS SIGNED). Boolean do silver convertido para 0/1. | CALCULADO |

## 4. Novas Colunas Exclusivas do BuyGoods (posições 65-75)
Estes campos existem na Gold do BuyGoods, mas NÃO existem na gold_clickbank. Ficam após a coluna 64 para não quebrar a ordem espelhada. Em consultas que precisam unir as duas tabelas (UNION ALL), o lado ClickBank pode tratar essas colunas como NULL.
### 4.1 Identificadores e Metadados BuyGoods (posições 65-67)
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 65 | purchase_group_id | VARCHAR(100) | CONCAT(client_email, '_', account_id, '_', purchase_group_id_final). PK natural da Gold BuyGoods — identifica a sessão de checkout (janela temporal de 240 min). Não tem equivalente direto no ClickBank. | CALCULADO |
| 66 | account_id | BIGINT | Chave de agrupamento (GROUP BY). Constante dentro de uma compra. No futuro será resolvido para vendor_name via JOIN com buygoods_accounts. | AGREGADO |
| 67 | datetime_platform | VARCHAR(19) | MIN(datetime_platform). Data/hora original da plataforma BuyGoods da primeira transação do grupo. | AGREGADO |

### 4.2 Financeiro Exclusivo BuyGoods (posições 68-74)
Campos financeiros que existem apenas no BuyGoods (não existem no ClickBank). Inclui o IVA brasileiro (separado da taxa de plataforma), as taxas de refund e chargeback (cobranças adicionais da BuyGoods), e o total_collected (valor efetivamente cobrado).
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 68 | total_collected_usd | DECIMAL(10,2) | ROUND(SUM(total_collected_usd), 2). Valor efetivamente cobrado do cliente (inclui IVA brasileiro). Diferente de total_price_usd, que é o subtotal do produto. | AGREGADO |
| 69 | iva | DECIMAL(12,4) | ROUND(SUM(iva), 4). Imposto sobre venda (Brasil) em BRL. Vem do BG.taxes do payload (renomeado no silver). | AGREGADO |
| 70 | iva_usd | DECIMAL(10,2) | ROUND(SUM(iva_usd), 2). Idem em USD. | AGREGADO |
| 71 | refund_fee | DECIMAL(12,4) | ROUND(SUM(refund_fee), 4). Soma das taxas de refund cobradas (BuyGoods cobra USD 1,00 por refund). BRL. | AGREGADO |
| 72 | refund_fee_usd | DECIMAL(10,2) | ROUND(SUM(refund_fee_usd), 2). Idem em USD. | AGREGADO |
| 73 | chargeback_fee | DECIMAL(12,4) | ROUND(SUM(chargeback_fee), 4). Soma das multas de chargeback (hoje USD 35 fixo, dinâmico). BRL. | AGREGADO |
| 74 | chargeback_fee_usd | DECIMAL(10,2) | ROUND(SUM(chargeback_fee_usd), 2). Idem em USD. | AGREGADO |

### 4.3 Atribuição BuyGoods (posição 75)
affiliate_id é a PK real do afiliado no BuyGoods (mesmo affiliate_name pode ter aff_ids diferentes). Os subids deixaram de existir nesta versão; a atribuição por campanha agora é coberta pelos campos utm_* (posições 55-59), populados direto da silver unified.
| # | Campo Gold | Tipo | Regra / Lógica de Transformação | Categ. |
|---|---|---|---|---|
| 75 | affiliate_id | BIGINT | MAX(affiliate_id) do grupo. PK real do afiliado no BG (não confiar só em affiliate_name). | AGREGADO |

## 5. Regras Especiais Detalhadas
### 5.1 Cálculo do total_refund (bruto)
Nesta versão, total_refund e total_refund_usd passaram a ser o valor BRUTO — a soma direta dos refunds da Silver, sem deduzir iva e taxes. A dedução de impostos (cálculo do líquido) que existia na v1.x foi removida. Quem precisar do impacto líquido em P&L pode reconstruí-lo na camada de consumo usando as colunas iva, taxes, refund_fee e chargeback_fee, todas disponíveis na Gold.
Fórmula aplicada nos campos total_refund e total_refund_usd:
total_refund = ROUND(SUM(total_refund), 4) e total_refund_usd = ROUND(SUM(total_refund_usd), 2). Sem subtração de iva ou taxes.
Em compras sem refund/chargeback, o SUM resulta em 0 → total_refund = 0. Em compras com refund integral, total_refund mostra o valor bruto devolvido ao cliente (ex.: refund de USD 230,29 aparece como USD 230,29, sem desconto de impostos).
Importante: como total_refund agora é o valor bruto, a reconciliação contábil com a plataforma BuyGoods (valor devolvido ao cliente) é direta. Caso se queira o impacto líquido em P&L (descontando os impostos estornados), ele pode ser derivado na camada de consumo como total_refund − iva (linhas refund/cb) − taxes (idem). Se essa visão líquida for frequente, considerar adicionar um campo derivado (total_refund_liquido_usd) numa versão futura.
### 5.2 Hierarquia de payment_status agregado
Quando o grupo tem múltiplas transações com payment_status diferentes:
• Todas as linhas com o mesmo status → retorna esse status (MAX equivale a um único valor).
• Alguma linha do grupo é 'chargeback' → retorna 'chargeback' (status mais severo).
• Caso contrário → retorna 'refunded_partial' (mistura de aprovado com refund).
### 5.3 Lógica de is_house_traffic na comissão
No tráfego próprio (house traffic), não há afiliado externo. Para que a comissão consolidada represente o ganho real do vendor:
• commission = commission_original + affiliate_amount (absorve o valor)
• affiliate_amount = 0 (zera, pois não há afiliado externo)
• revenue_afiliado = affiliate_amount_original (preserva para visão CPA)
No tráfego de afiliado externo, mantém-se a separação: commission é só do vendor, affiliate_amount é só do afiliado, revenue_afiliado = 0.
### 5.4 Tratamento de grupos com múltiplos main
Cenário atual (Mai/2026): como o silver ainda não tem offer_name 100% populado, ~36% dos grupos podem ter mais de uma linha classificada como main. Comportamento da Gold:
• product_name / offer_name / product_sku: MAX() escolhe um valor representativo (lexicográfico).
• total_price e demais campos financeiros: SUM() consolida todos os mains (não há perda de valor financeiro).
• Conforme o offer_name for sendo preenchido na Silver, esses casos vão sendo reclassificados corretamente (a regra do funnel_type fará a reclassificação automaticamente).
### 5.5 Conversão is_house_traffic boolean → 0/1
No Silver, is_house_traffic é um boolean (TRUE/FALSE). Na Gold, é convertido para INT (0/1) para garantir paridade com a gold_clickbank (que usa TINYINT(1)). A regra interna de cálculo de commission/affiliate compara is_house_traffic = 1 (inteiro), conforme o código V2.
## 6. Filtro de Período
A query aplica o filtro de data diretamente na CTE base (não há mais CTE params). Sem data_fim — traz tudo a partir da data informada, com a opção de incluir registros com created_at_date IS NULL (fallback de segurança).
WHERE (cb.created_at_date >= '2026-01-01' OR cb.created_at_date IS NULL)
O filtro é aplicado na CTE base, antes da agregação, para reduzir o volume de dados processado.
## 7. Validação Empírica
Amostra usada na validação: 34.265 linhas da Silver (período Mai/2026).
Resultado da agregação:
• Total de grupos (compras): 22.114
• Grupos com pelo menos 1 upsell/downsell: 8.457 (38%)
• Total faturado consolidado (USD): aprox. 8,77 milhões

Distribuição de funnel_type após aplicação da regra (3 níveis):
• main: 22.059 linhas
• upsell1: 6.009 | upsell2: 2.866 | upsell3: 436
• downsell1: 2.002 | downsell2: 824 | downsell3: 69

Comparação com a regra antiga (sales_type primeiro):
• Antes: 314 linhas como upsell/downsell (apenas as com sales_type = Venda de Funil).
• Depois: 12.206 linhas como upsell/downsell. Aumento de 38x na cobertura, graças ao fallback via product_codename.

Validação de paridade de schema com gold_clickbank: as 64 primeiras colunas batem 100% em nome e ordem (validado por script de comparação automatizada).
## 8. Histórico de Versões
| Versão | Data | Alterações Principais |
|---|---|---|
| 1.0 | Mai/2026 | Versão inicial. Mapeamento de campos da camada Gold derivada de gex_db_prod_silver.tb_buygoods_physical_new. Agrupamento por upsell_parent_receipt. Classificação funnel_type em 3 níveis (offer_name → product_codename → sales_type). Cálculo de total_refund líquido. Lógica is_house_traffic. Parametrização de data_inicio. |
| 1.1 | Mai/2026 | Reordenação das colunas para alinhar com gold_clickbank. Posições 1-64 IDÊNTICAS à gold_clickbank em nome e ordem. Campos inexistentes no BG (coupon_code, utm_*, src, vendor_name) marcados como NULL com cast(null as varchar). Novas colunas exclusivas do BG (purchase_group_id, account_id, total_collected_usd, iva, iva_usd, refund_fee/_usd, chargeback_fee/_usd, affiliate_id, subid 1-5) posicionadas nas posições 65-79. Total: 79 colunas. |
| 2.0 | Jun/2026 | Nova fonte: instituto_experience.tb_gex_buygoods_unified; tabela alvo: instituto_experience.dashboard_gold_buygoods. Agrupamento deixou de usar upsell_parent_receipt e passou a janela temporal de 240 min sobre (client_email, account_id), igual ao ClickBank; purchase_group_id = CONCAT(client_email, account_id, grupo). total_refund/_usd agora BRUTOS (sem dedução de iva/taxes). utm_* populados via MAX da silver (deixaram de ser NULL). client_country mapeado de código ISO para nome do país. product_name/offer_name/product_sku com fallback (COALESCE) herdando o main do grupo anterior. created_at_date/hour derivados de created_at_ts. Adicionada coluna datetime_platform (pos. 67). Removidas as colunas subid 1-5. Filtro de período direto na CTE base (sem CTE params). Engine MySQL 8/MariaDB. Total: 75 colunas (64 espelhadas + 11 exclusivas). |

## 9. Próximos Passos e Pontos de Atenção
• Quando o offer_name estiver 100% preenchido na Silver, a regra 1 do funnel_type passará a capturar todos os upsells/downsells via offer_name, e a regra 2 (codename) ficará latente. Não é necessário alterar a Gold.
• Avaliar a criação de uma view canônica que faz UNION ALL entre gold_clickbank e gold_buygoods, selecionando até a coluna 64 (paridade) ou tratando as exclusivas BG como NULL no lado CB.
• Considerar adicionar campos derivados em versões futuras: ticket_medio (total_price / quantity), uplift_funil (soma upsells/downsells), refund_rate (total_refund_bruto / total_collected), conforme demanda de visualizações.
• Avaliar inclusão do tratamento de chargeback_alert (USD 25 por alerta) quando a fonte de dados estiver disponível — atualmente esses casos caem como refund regular porque o sinal não vem nos webhooks da BuyGoods. Requer integração com fonte separada (Ethoca / relatório de alertas).
• Documentar no Data Dictionary que total_refund é BRUTO (soma direta dos refunds, sem dedução de iva/taxes). O impacto LÍQUIDO em P&L, se necessário, é derivável na camada de consumo como total_refund − iva (refund/cb) − taxes (refund/cb).
• Validar com o squad de tráfego o preenchimento dos campos utm_* vindos da silver unified (qualidade/cobertura), já que substituíram os antigos subid 1-5 como fonte de atribuição por campanha.
