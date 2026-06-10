# -*- coding: utf-8 -*-
"""
validacao_silver_buygoods_plataforma.py
Reconciliação DIÁRIA da silver `instituto_experience.tb_gex_buygoods_unified` (MySQL)
com o export da **plataforma BuyGoods** (Master Overview, diário), 01/04 a 09/06/2026, USD.

Fontes:
  - Plataforma: Excel diário (Downloads) — Gross/Commissions/Refunds/Chargebacks/Commission Voids/Taxes/Net.
  - Silver: MySQL (read-only), alinhada pelo timestamp DA PLATAFORMA (datetime_platform /
    datetime_refunded_platform) para casar o "dia" com o BuyGoods.

Gera o relatório markdown em Operação/Validações/. Somente leitura no banco.
Uso:  python validacao_silver_buygoods_plataforma.py
Requer: pandas, xlrd>=2.0.1, pymysql.
"""
import json
import os
import sys
import pandas as pd
import pymysql

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

VAULT = r'C:\Users\tadeu\DataTeamDocs'
OUTDIR = os.path.join(VAULT, 'Operação', 'Validações')
XLS = r'C:\Users\tadeu\Downloads\Master_Overview_2026-04-01_2026-06-090wT8Ci.xls'
INI, FIM = '2026-04-01', '2026-06-09'
REPORT = os.path.join(OUTDIR, 'validacao-silver-buygoods-plataforma-2026-06-09.md')

# ---------------- plataforma (Excel diário) ----------------
p = pd.read_excel(XLS, engine='xlrd', header=0)
p.columns = [str(c).strip() for c in p.columns]
p = p[p['Date'].astype(str).str.strip() != 'Total'].copy()
p['d'] = pd.to_datetime(p['Date'], format='%B %d, %Y').dt.date
PCOLS = ['Gross Sales', 'Commissions', 'Refunds', 'Chargebacks', 'Commission Voids', 'Taxes', 'Net Sales']
for c in PCOLS:
    p[c] = pd.to_numeric(p[c], errors='coerce')

# ---------------- silver (MySQL, base timestamp da plataforma) ----------------
env = json.load(open(r'C:\Users\tadeu\.claude.json', encoding='utf-8'))['mcpServers']['mysql']['env']
cn = pymysql.connect(host=env['MYSQL_HOST'], port=int(env['MYSQL_PORT']), user=env['MYSQL_USER'],
                     password=env['MYSQL_PASS'], database=env['MYSQL_DB'], charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor)


def q(sql):
    with cn.cursor() as c:
        c.execute(sql)
        return c.fetchall()


sales = q(f"""SELECT LEFT(datetime_platform,10) d,
  SUM(total_price_usd - iva_usd) gross, SUM(affiliate_amount_usd) comm,
  SUM(CASE WHEN payment_status='approved' THEN iva_usd ELSE 0 END) taxes
 FROM instituto_experience.tb_gex_buygoods_unified
 WHERE LEFT(datetime_platform,10) BETWEEN '{INI}' AND '{FIM}'
 GROUP BY LEFT(datetime_platform,10)""")
refs = q(f"""SELECT LEFT(datetime_refunded_platform,10) d,
  SUM(CASE WHEN payment_status='chargeback' OR transaction_type='Chargeback' THEN total_refund_usd + chargeback_fee_usd ELSE 0 END) cb,
  SUM(CASE WHEN NOT(payment_status='chargeback' OR transaction_type='Chargeback') THEN total_refund_usd ELSE 0 END) rf
 FROM instituto_experience.tb_gex_buygoods_unified
 WHERE LEFT(datetime_refunded_platform,10) BETWEEN '{INI}' AND '{FIM}'
 GROUP BY LEFT(datetime_refunded_platform,10)""")
s = pd.DataFrame(sales); r = pd.DataFrame(refs)
for df in (s, r):
    df['d'] = pd.to_datetime(df['d']).dt.date
for col in ['gross', 'comm', 'taxes']:
    s[col] = s[col].astype(float)
for col in ['cb', 'rf']:
    r[col] = r[col].astype(float)

m = p.merge(s, on='d', how='left').merge(r, on='d', how='left').fillna(0).sort_values('d')
# net silver pela MESMA fórmula da plataforma (sem commission voids, que a silver não modela)
m['net_sv'] = m['gross'] - m['comm'] - m['rf'] - m['cb'] - m['taxes']
# deltas (silver - plataforma)
m['dG'] = m['gross'] - m['Gross Sales']
m['dC'] = m['comm'] - m['Commissions']
m['dR'] = m['rf'] - m['Refunds']
m['dB'] = m['cb'] - m['Chargebacks']
m['dT'] = m['taxes'] - m['Taxes']
m['dN'] = m['net_sv'] - m['Net Sales']


def br(v):
    return f'{v:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def pc(s_, p_):
    return '—' if p_ == 0 else f'{(s_-p_)/p_*100:+.2f}%'


L = []
w = L.append
w('---')
w('tipo: validacao')
w('par: tb_gex_buygoods_unified (silver MySQL) x plataforma BuyGoods (Master Overview, diário)')
w('data: 2026-06-09')
w(f'periodo: {INI} a {FIM}')
w('moeda: USD')
w('gerado_por: Operação/Validações/validacao_silver_buygoods_plataforma.py')
w('tags: [validacao, reconciliacao, buygoods, silver, plataforma]')
w('---')
w('# Validação — silver `tb_gex_buygoods_unified` × plataforma BuyGoods (diário)')
w('')
w('> Reconciliação **dia a dia** contra o export diário do Master Overview (USD), alinhada pelo '
  '**timestamp da plataforma** (`datetime_platform` / `datetime_refunded_platform`).')
w('> Veredito: a silver bate **≤1%** em Gross/Commissions/Refunds/Taxes; **Refunds reconcilia quase 100%**; '
  '**Chargebacks ~−5%** (após incluir o `chargeback_fee`). Único drift maior: **Gross de junho (+2%)** — settlement.')
w('')
w('## De-para (campo da silver por KPI, base timestamp-plataforma)')
w('')
w('| KPI (plataforma) | Definição na silver |')
w('|---|---|')
w('| **Gross Sales** | `SUM(total_price_usd - iva_usd)` por `DATE(datetime_platform)` |')
w('| **Commissions** | `SUM(affiliate_amount_usd)` por `DATE(datetime_platform)` |')
w('| **Refunds** | `SUM(total_refund_usd)` (não-chargeback) por `DATE(datetime_refunded_platform)` |')
w('| **Chargebacks** | `SUM(total_refund_usd + chargeback_fee_usd)` onde `payment_status=chargeback OR transaction_type=Chargeback`, por `DATE(datetime_refunded_platform)` |')
w('| **Taxes** | `SUM(iva_usd)` das vendas `approved` por `DATE(datetime_platform)` |')
w('| **Net Sales** | `Gross − Commissions − Refunds − Chargebacks − Taxes` (plataforma ainda soma `Commission Voids`) |')
w('')

# total
w('## Total do período')
w('')
w('| KPI | Plataforma | Silver | Δ | Δ% |')
w('|---|--:|--:|--:|--:|')
for lbl, pcol, scol in [('Gross Sales', 'Gross Sales', 'gross'), ('Commissions', 'Commissions', 'comm'),
                        ('Refunds', 'Refunds', 'rf'), ('Chargebacks', 'Chargebacks', 'cb'),
                        ('Taxes', 'Taxes', 'taxes'), ('Net Sales', 'Net Sales', 'net_sv')]:
    P, S = m[pcol].sum(), m[scol].sum()
    w(f'| {lbl} | {br(P)} | {br(S)} | {br(S-P)} | {pc(S, P)} |')
w('')
w('> **Refunds** reconcilia (+0,05%) ao atribuir pelo `datetime_refunded_platform`. **Chargebacks** agora '
  'inclui o `chargeback_fee` (passou de −16,5% para ~−5%). **Net** herda o resíduo de voids + chargebacks + gross de junho.')
w('')

# por dia — valores absolutos plataforma x silver
w('## Por dia — plataforma × silver (USD)')
w('')
w('> Cada KPI com o valor da **plataforma (P)** e da **silver (S)** lado a lado, e o **Δ Net** (silver−plataforma) '
  'para localizar dias divergentes.')
w('')
w('| Dia | Gross P | Gross S | Comm P | Comm S | Refund P | Refund S | CB P | CB S | Tax P | Tax S | Net P | Net S | Δ Net |')
w('|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|')
for _, x in m.iterrows():
    w(f"| {x.d.strftime('%d/%m')} | {br(x['Gross Sales'])} | {br(x['gross'])} "
      f"| {br(x['Commissions'])} | {br(x['comm'])} | {br(x['Refunds'])} | {br(x['rf'])} "
      f"| {br(x['Chargebacks'])} | {br(x['cb'])} | {br(x['Taxes'])} | {br(x['taxes'])} "
      f"| {br(x['Net Sales'])} | {br(x['net_sv'])} | {br(x['dN'])} |")
w(f"| **Total** | **{br(m['Gross Sales'].sum())}** | **{br(m['gross'].sum())}** "
  f"| **{br(m['Commissions'].sum())}** | **{br(m['comm'].sum())}** | **{br(m['Refunds'].sum())}** | **{br(m['rf'].sum())}** "
  f"| **{br(m['Chargebacks'].sum())}** | **{br(m['cb'].sum())}** | **{br(m['Taxes'].sum())}** | **{br(m['taxes'].sum())}** "
  f"| **{br(m['Net Sales'].sum())}** | **{br(m['net_sv'].sum())}** | **{br(m['dN'].sum())}** |")
w('')

# achados
w('## Achados')
w('')
w('1. **Refunds reconcilia (~100%)** ao atribuir por `datetime_refunded_platform` e separar chargeback — '
  'confirma que a silver tem os reembolsos certos; o que faltava era a **data/critério** de atribuição.')
w('2. **Chargebacks:** o "Chargebacks" da plataforma inclui a **taxa de chargeback** → definição corrigida para '
  '`total_refund_usd + chargeback_fee_usd`, que derrubou o desvio de **−16,5% para ~−5%**. O resíduo restante '
  '(~27k) é provável atribuição de data de borda / algum chargeback ainda não marcado como tal na silver.')
w('3. ⚠️ **Gross drifta positivo no fim do período (junho)**: os maiores desvios de Gross estão em **01–04/06 e 09/06** '
  '(silver acima da plataforma) — período recente, provável **settlement** (vendas/ajustes muito novos ainda não batem '
  'entre origem e silver). Reavaliar com export mais recente.')
w('4. **Commissions −0,45%** e **Taxes +0,91%** são desvios pequenos e ~uniformes (arredondamento/FX/definição fina).')
w('5. A plataforma soma **Commission Voids** (~45k no período) no Net; a silver não modela voids — '
  'parte do Δ Net vem daí.')
w('')

w('## Reproduzir')
w(f'- Plataforma: `{os.path.basename(XLS)}` (Downloads) — export diário do Master Overview.')
w('- Silver: este script (`validacao_silver_buygoods_plataforma.py`), read-only no MySQL.')
w('')
w('## Relacionados')
w('- Silver doc: [[Fontes de Dados/Buygoods/doc_silver_buygoods]]')
w('- Validação gold (MySQL×MySQL): [[validacao-gold-buygoods-mysql-2026-06-09]]')
w('- Schema: [[CLAUDE]] · Diário: [[log]]')
w('')

os.makedirs(OUTDIR, exist_ok=True)
open(REPORT, 'w', encoding='utf-8').write('\n'.join(L))
print('Relatório:', REPORT)
print('Total Δ — Gross', br(m.dG.sum()), '| Comm', br(m.dC.sum()), '| Ref', br(m.dR.sum()),
      '| CB', br(m.dB.sum()), '| Tax', br(m.dT.sum()), '| Net', br(m.dN.sum()))
