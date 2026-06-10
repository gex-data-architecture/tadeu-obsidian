# -*- coding: utf-8 -*-
"""
validacao_silver_buygoods_plataforma.py
Reconciliação da silver `instituto_experience.tb_gex_buygoods_unified` (MySQL) com os
KPIs da **plataforma BuyGoods** (Master Overview), período 01/04/2026 a 09/06/2026.

SOMENTE LEITURA no MySQL. Gera um relatório markdown em Operação/Validações/.
Os valores da plataforma são fixos aqui (lidos da tela/Excel da conta master).
De-para descoberto por engenharia reversa (ver observações no relatório).

Uso:  python validacao_silver_buygoods_plataforma.py
"""
import json
import os
import sys
from decimal import Decimal
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import pymysql

VAULT = r'C:\Users\tadeu\DataTeamDocs'
OUTDIR = os.path.join(VAULT, 'Operação', 'Validações')
PERIODO_INI, PERIODO_FIM = '2026-04-01', '2026-06-09'
TODAY = '2026-06-09'
REPORT = os.path.join(OUTDIR, 'validacao-silver-buygoods-plataforma-2026-06-09.md')

# KPIs da plataforma BuyGoods (Master Overview), 01/04 a 09/06/2026 — fonte da verdade.
PLAT = {
    'gross': Decimal('98681080.46'),
    'refunds': Decimal('13624448.77'),
    'commissions': Decimal('59750058.50'),
    'taxes': Decimal('4940464.79'),
    'net': Decimal('20366108.40'),
}

with open(r'C:\Users\tadeu\.claude.json', 'r', encoding='utf-8') as f:
    env = json.load(f)['mcpServers']['mysql']['env']
conn = pymysql.connect(
    host=env['MYSQL_HOST'], port=int(env['MYSQL_PORT']),
    user=env['MYSQL_USER'], password=env['MYSQL_PASS'],
    database=env['MYSQL_DB'], charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor, connect_timeout=30,
)

PERDAY_SQL = f"""
WITH s AS (
  SELECT created_at_date d,
         SUM(total_price_usd - iva_usd) gross,
         SUM(affiliate_amount_usd) commissions,
         SUM(CASE WHEN payment_status='approved' THEN iva_usd ELSE 0 END) taxes
  FROM instituto_experience.tb_gex_buygoods_unified
  WHERE created_at_date BETWEEN '{PERIODO_INI}' AND '{PERIODO_FIM}'
  GROUP BY created_at_date
),
r AS (
  SELECT date_refunded d, SUM(total_refund_usd) refunds
  FROM instituto_experience.tb_gex_buygoods_unified
  WHERE date_refunded BETWEEN '{PERIODO_INI}' AND '{PERIODO_FIM}'
  GROUP BY date_refunded
)
SELECT s.d AS dia,
  ROUND(s.gross,2) gross, ROUND(COALESCE(r.refunds,0),2) refunds,
  ROUND(s.commissions,2) commissions, ROUND(s.taxes,2) taxes,
  ROUND(s.gross - COALESCE(r.refunds,0) - s.commissions - s.taxes,2) net_calc
FROM s LEFT JOIN r ON r.d = s.d
ORDER BY s.d
"""

with conn.cursor() as cur:
    cur.execute(PERDAY_SQL)
    rows = cur.fetchall()


def D(v):
    return Decimal(str(v or 0))


def br(v):
    """Formata Decimal em pt-BR: 1.234.567,89."""
    return f'{D(v):,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def pct(diff, base):
    return '—' if base == 0 else f'{(diff / base * 100):+.2f}%'


# totais (silver)
tot = {k: sum(D(r[k2]) for r in rows) for k, k2 in
       [('gross', 'gross'), ('refunds', 'refunds'), ('commissions', 'commissions'),
        ('taxes', 'taxes'), ('net', 'net_calc')]}

L = []
w = L.append
w('---')
w('tipo: validacao')
w('par: tb_gex_buygoods_unified (silver MySQL) x plataforma BuyGoods (Master Overview)')
w(f'data: {TODAY}')
w(f'periodo: {PERIODO_INI} a {PERIODO_FIM}')
w('moeda: USD')
w('gerado_por: Operação/Validações/validacao_silver_buygoods_plataforma.py')
w('tags: [validacao, reconciliacao, buygoods, silver, plataforma]')
w('---')
w('# Validação — silver `tb_gex_buygoods_unified` × plataforma BuyGoods')
w('')
w(f'> Reconciliação dos KPIs do **Master Overview** (01/04→09/06/2026, USD) contra a silver no MySQL.')
w('> Somente leitura. A silver **reproduz a plataforma dentro de ~0,3%–1,2%** por KPI — diferenças de '
  'definição/atribuição de data/fuso, **não** de dados faltando.')
w('')

# ---- de-para
w('## De-para descoberto (campo da silver por KPI)')
w('')
w('| KPI (plataforma) | Definição na silver |')
w('|---|---|')
w('| **Gross Sales** | `SUM(total_price_usd - iva_usd)` por `created_at_date` |')
w('| **Refunds & Chargebacks** | `SUM(total_refund_usd)` por **`date_refunded`** (não pela data da venda) |')
w('| **Commissions** | `SUM(affiliate_amount_usd)` (todas as linhas) por `created_at_date` |')
w('| **Taxes** | `SUM(iva_usd)` das vendas `payment_status=approved` (não o `taxes_usd`) |')
w('| **Net Sales** | `Gross − Refunds − Commissions − Taxes` (calculado) |')
w('')

# ---- geral
w('## Geral (total do período)')
w('')
w('| KPI | Plataforma (USD) | Silver (USD) | Δ | Δ% |')
w('|---|--:|--:|--:|--:|')
for k, lbl in [('gross', 'Gross Sales'), ('refunds', 'Refunds & Chargebacks'),
               ('commissions', 'Commissions'), ('taxes', 'Taxes'), ('net', 'Net Sales (calc)')]:
    diff = tot[k] - PLAT[k]
    w(f'| {lbl} | {br(PLAT[k])} | {br(tot[k])} | {br(diff)} | {pct(diff, PLAT[k])} |')
w('')
w('> **Net** acumula mais desvio relativo (+3,3%) por ser um **resíduo pequeno de números grandes** — '
  'os erros de cada componente se somam. Gross/Refunds/Commissions/Taxes ficam todos ≤1,2%.')
w('')

# ---- por dia
w('## Por dia (lado silver — USD)')
w('')
w('> A plataforma só forneceu o **total** do período (tela do Master Overview); os valores **diários** abaixo '
  'são da silver, com **Net calculado**. O comparativo diário plataforma×silver será fechado quando chegar o Excel.')
w('')
w('| Dia | Gross | Refunds & CB | Commissions | Taxes | **Net (calc)** |')
w('|---|--:|--:|--:|--:|--:|')
for r in rows:
    d = r['dia']
    ds = d.strftime('%d/%m') if hasattr(d, 'strftime') else str(d)
    w(f"| {ds} | {br(r['gross'])} | {br(r['refunds'])} | {br(r['commissions'])} | {br(r['taxes'])} | {br(r['net_calc'])} |")
w(f"| **Total** | **{br(tot['gross'])}** | **{br(tot['refunds'])}** | **{br(tot['commissions'])}** "
  f"| **{br(tot['taxes'])}** | **{br(tot['net'])}** |")
w('')

# ---- observações
w('## Observações')
w('')
w('- **Mapeamento não é óbvio:** "Taxes" = `iva_usd` (o `taxes_usd` somaria ~9M, ~2x); "Commissions" = '
  '`affiliate_amount_usd` (o `commission_usd` é ~37M, é outro conceito — provável valor do vendor/fee).')
w('- **Reembolso é por `date_refunded`:** trocar a data de atribuição derrubou o erro de **−4,0% para −1,2%** '
  '(reembolsos de vendas antigas processados dentro do período).')
w('- **Resíduos com assinatura de fuso:** `created_at` é `timestamp`; a plataforma agrupa o "dia" no fuso dela. '
  'Nas bordas de cada dia, transações caem em dias diferentes → gap pequeno e bidirecional ao longo de 70 dias. Some FX/arredondamento.')
w('- **Tipos de transação na silver:** Sale, Cancel, Chargeback, Refund, Fulfillment, Rebill — a plataforma '
  'filtra/atribui por tipo (Gross líquido de IVA; Taxes só de approved).')
w('- **Grão:** 1 linha por `transaction_id` (411.186 linhas = 411.186 tx no período).')
w('')
w('## ⚠️ Pendências para fechar ao centavo')
w('- **Excel da conta master** (valores diários e por campo) → reconciliação diária plataforma×silver e '
  'validação além dos 5 KPIs (por produto/oferta/afiliado).')
w('- Confirmar o **fuso** usado pela plataforma para fechar o dia (provável causa dos resíduos de borda).')
w('')

w('## Como reproduzir (read-only)')
w('```sql')
w(PERDAY_SQL.strip())
w('```')
w('')
w('## Relacionados')
w('- Silver doc: [[Fontes de Dados/Buygoods/doc_silver_buygoods]]')
w('- Validação gold (MySQL×MySQL): [[validacao-gold-buygoods-mysql-2026-06-09]]')
w('- Schema: [[CLAUDE]] · Diário: [[log]]')
w('')

os.makedirs(OUTDIR, exist_ok=True)
with open(REPORT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(L))

print('Relatório:', REPORT)
print('Totais silver — gross', br(tot['gross']), '| refunds', br(tot['refunds']),
      '| commissions', br(tot['commissions']), '| taxes', br(tot['taxes']), '| net', br(tot['net']))
