# -*- coding: utf-8 -*-
"""
validar_plataforma.py  (skill: validar-plataforma-buygoods)
Reconcilia a silver `instituto_experience.tb_gex_buygoods_unified` (TODA a plataforma)
com o export diário do **Master Overview** do BuyGoods (Excel). Gera TOTAL + POR DIA.

Alinhamento: a silver é lida pelo **timestamp da plataforma** (datetime_platform /
datetime_refunded_platform); a data do Master Overview casa direto (sem shift).

De-para (KPI plataforma -> silver):
  Gross Sales = total_price_usd - iva_usd        (por DATE(datetime_platform))
  Commissions = affiliate_amount_usd             (por DATE(datetime_platform))
  Taxes       = iva_usd dos approved             (por DATE(datetime_platform))
  Refunds     = total_refund_usd (não-chargeback)(por DATE(datetime_refunded_platform))
  Chargebacks = total_refund_usd + chargeback_fee_usd (chargeback, mesma data)
  Net Sales   = Gross - Commissions - Refunds - Chargebacks - Taxes
                (a plataforma ainda soma Commission Voids, que a silver não modela)

SOMENTE LEITURA no MySQL. Período derivado do próprio Excel.
Uso:  python validar_plataforma.py [caminho_do_excel]
      (default: o Master_Overview_*.xls* mais recente em Downloads)
Requer: pandas, xlrd>=2.0.1 (.xls) / openpyxl (.xlsx), pymysql.
"""
import json, os, sys, glob
import pandas as pd
import pymysql
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

VAULT = r'C:\Users\tadeu\DataTeamDocs'
OUTDIR = os.path.join(VAULT, 'Operação', 'Validações')


def find_default():
    c = glob.glob(os.path.join(os.path.expanduser('~'), 'Downloads', 'Master_Overview_*.xls*'))
    return max(c, key=os.path.getmtime) if c else None


XLS = sys.argv[1] if len(sys.argv) > 1 else find_default()
if not XLS or not os.path.isfile(XLS):
    sys.exit('Excel do Master Overview não encontrado — passe o caminho como argumento.')

eng = 'xlrd' if XLS.lower().endswith('.xls') else 'openpyxl'
p = pd.read_excel(XLS, engine=eng, header=0)
p.columns = [str(c).strip() for c in p.columns]
p = p[p['Date'].astype(str).str.strip() != 'Total'].copy()
p['d'] = pd.to_datetime(p['Date'], format='%B %d, %Y', errors='coerce')
if p['d'].isna().any():
    p.loc[p['d'].isna(), 'd'] = pd.to_datetime(p.loc[p['d'].isna(), 'Date'], errors='coerce')
p['d'] = p['d'].dt.date
PCOLS = ['Gross Sales', 'Commissions', 'Refunds', 'Chargebacks', 'Commission Voids', 'Taxes', 'Net Sales']
for c in PCOLS:
    p[c] = pd.to_numeric(p[c], errors='coerce').fillna(0)
INI, FIM = min(p['d']).isoformat(), max(p['d']).isoformat()
REPORT = os.path.join(OUTDIR, f'validacao-plataforma-buygoods-{FIM}.md')

env = json.load(open(r'C:\Users\tadeu\.claude.json', encoding='utf-8'))['mcpServers']['mysql']['env']
cn = pymysql.connect(host=env['MYSQL_HOST'], port=int(env['MYSQL_PORT']), user=env['MYSQL_USER'],
                     password=env['MYSQL_PASS'], database=env['MYSQL_DB'], charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor)


def q(sql):
    with cn.cursor() as c:
        c.execute(sql); return c.fetchall()


sales = q(f"""SELECT LEFT(datetime_platform,10) d,
  SUM(total_price_usd - iva_usd) gross, SUM(affiliate_amount_usd) comm,
  SUM(CASE WHEN payment_status='approved' THEN iva_usd ELSE 0 END) taxes
 FROM instituto_experience.tb_gex_buygoods_unified
 WHERE LEFT(datetime_platform,10) BETWEEN '{INI}' AND '{FIM}' GROUP BY LEFT(datetime_platform,10)""")
refs = q(f"""SELECT LEFT(datetime_refunded_platform,10) d,
  SUM(CASE WHEN cbk THEN total_refund_usd + chargeback_fee_usd ELSE 0 END) cb,
  SUM(CASE WHEN NOT cbk THEN total_refund_usd ELSE 0 END) rf
 FROM (SELECT *, (payment_status='chargeback' OR transaction_type='Chargeback') cbk
       FROM instituto_experience.tb_gex_buygoods_unified) t
 WHERE LEFT(datetime_refunded_platform,10) BETWEEN '{INI}' AND '{FIM}' GROUP BY LEFT(datetime_refunded_platform,10)""")
s = pd.DataFrame(sales); r = pd.DataFrame(refs)
for df in (s, r):
    df['d'] = pd.to_datetime(df['d']).dt.date
for col in ['gross', 'comm', 'taxes']:
    s[col] = s[col].astype(float)
for col in ['cb', 'rf']:
    r[col] = r[col].astype(float)

m = p.merge(s, on='d', how='left').merge(r, on='d', how='left').fillna(0).sort_values('d')
m['net_sv'] = m['gross'] - m['comm'] - m['rf'] - m['cb'] - m['taxes']
m['dN'] = m['net_sv'] - m['Net Sales']
m['mes'] = pd.to_datetime(m['d']).dt.strftime('%Y-%m')


def br(v):
    return f'{v:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def pc(s_, p_):
    return '—' if abs(p_) < 0.005 else f'{(s_-p_)/p_*100:+.2f}%'


PAIRS = [('Gross Sales', 'Gross Sales', 'gross'), ('Commissions', 'Commissions', 'comm'),
         ('Refunds', 'Refunds', 'rf'), ('Chargebacks', 'Chargebacks', 'cb'),
         ('Taxes', 'Taxes', 'taxes'), ('Net Sales', 'Net Sales', 'net_sv')]
L = []; w = L.append
w('---'); w('tipo: validacao')
w('par: tb_gex_buygoods_unified (silver) x plataforma BuyGoods (Master Overview, diário)')
w(f'data: {FIM}'); w(f'periodo: {INI} a {FIM}'); w('moeda: USD')
w('gerado_por: skill/validar-plataforma-buygoods')
w('tags: [validacao, reconciliacao, buygoods, silver, plataforma]'); w('---')
w('# Validação — silver `tb_gex_buygoods_unified` × plataforma BuyGoods (diário)')
w('')
w(f'> Master Overview **{INI} → {FIM}** (USD). Silver alinhada pelo **timestamp da plataforma**. Somente leitura.')
w('')
w('## De-para (KPI plataforma → silver)')
w('')
w('| KPI | Definição na silver |')
w('|---|---|')
w('| Gross Sales | `SUM(total_price_usd - iva_usd)` por `DATE(datetime_platform)` |')
w('| Commissions | `SUM(affiliate_amount_usd)` por `DATE(datetime_platform)` |')
w('| Refunds | `SUM(total_refund_usd)` (não-chargeback) por `DATE(datetime_refunded_platform)` |')
w('| Chargebacks | `SUM(total_refund_usd + chargeback_fee_usd)` (chargeback), mesma data |')
w('| Taxes | `SUM(iva_usd)` das vendas `approved` por `DATE(datetime_platform)` |')
w('| Net Sales | `Gross − Commissions − Refunds − Chargebacks − Taxes` (plataforma soma Commission Voids) |')
w('')
# total
w('## Total do período')
w(''); w('| KPI | Plataforma | Silver | Δ | Δ% |'); w('|---|--:|--:|--:|--:|')
for lbl, pcol, scol in PAIRS:
    P, S = m[pcol].sum(), m[scol].sum()
    w(f'| {lbl} | {br(P)} | {br(S)} | {br(S-P)} | {pc(S, P)} |')
w('')
# por mês (locador)
w('## Por mês (localizar a diferença)')
w(''); w('| Mês | Δ Gross% | Δ Comm% | Δ Refunds% | Δ Chargeback% | Δ Net |'); w('|---|--:|--:|--:|--:|--:|')
gm = m.groupby('mes').agg(Gp=('Gross Sales', 'sum'), Gs=('gross', 'sum'), Cp=('Commissions', 'sum'),
                          Cs=('comm', 'sum'), Rp=('Refunds', 'sum'), Rs=('rf', 'sum'),
                          Bp=('Chargebacks', 'sum'), Bs=('cb', 'sum'), dN=('dN', 'sum'))
for mes, x in gm.iterrows():
    w(f'| {mes} | {pc(x.Gs,x.Gp)} | {pc(x.Cs,x.Cp)} | {pc(x.Rs,x.Rp)} | {pc(x.Bs,x.Bp)} | {br(x.dN)} |')
w('')
# por dia
w('## Por dia — plataforma × silver (USD)')
w(''); w('> Cada KPI com plataforma (P) e silver (S) lado a lado + Δ Net.'); w('')
w('| Dia | Gross P | Gross S | Comm P | Comm S | Refund P | Refund S | CB P | CB S | Tax P | Tax S | Net P | Net S | Δ Net |')
w('|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|')
for _, x in m.iterrows():
    w(f"| {x.d.strftime('%d/%m')} | {br(x['Gross Sales'])} | {br(x['gross'])} | {br(x['Commissions'])} | {br(x['comm'])} "
      f"| {br(x['Refunds'])} | {br(x['rf'])} | {br(x['Chargebacks'])} | {br(x['cb'])} | {br(x['Taxes'])} | {br(x['taxes'])} "
      f"| {br(x['Net Sales'])} | {br(x['net_sv'])} | {br(x['dN'])} |")
w(f"| **Total** | **{br(m['Gross Sales'].sum())}** | **{br(m['gross'].sum())}** | **{br(m['Commissions'].sum())}** | **{br(m['comm'].sum())}** "
  f"| **{br(m['Refunds'].sum())}** | **{br(m['rf'].sum())}** | **{br(m['Chargebacks'].sum())}** | **{br(m['cb'].sum())}** "
  f"| **{br(m['Taxes'].sum())}** | **{br(m['taxes'].sum())}** | **{br(m['Net Sales'].sum())}** | **{br(m['net_sv'].sum())}** | **{br(m['dN'].sum())}** |")
w('')
# achados (auto)
worst = m.reindex(m['dN'].abs().sort_values(ascending=False).index).head(5)
w('## Achados (auto)')
w('')
w('- **Maiores desvios de Net (dia):** ' + ' · '.join(f"{x.d.strftime('%d/%m')} ({br(x.dN)})" for _, x in worst.iterrows()))
w('- **Chargebacks** incluem a `chargeback_fee` (`total_refund_usd + chargeback_fee_usd`).')
w('- **Commission Voids** não é modelado na silver → parte do Δ Net vem daí.')
w('- Desvios pequenos e ~uniformes = arredondamento/FX/definição fina; desvios concentrados num período '
  'recente = provável **settlement** (reavaliar com export mais novo); quebra com data fixa = investigar **ingestão**.')
w('')
w('## Reproduzir')
w(f'- Plataforma: `{os.path.basename(XLS)}`.')
w('- Skill `validar-plataforma-buygoods` (`scripts/validar_plataforma.py`), read-only no MySQL.')
w('')
w('## Relacionados')
w('- Conta específica: skill `validar-conta-buygoods`')
w('- Silver doc: [[Fontes de Dados/Buygoods/doc_silver_buygoods]] · [[CLAUDE]] · [[log]]')
w('')

os.makedirs(OUTDIR, exist_ok=True)
open(REPORT, 'w', encoding='utf-8').write('\n'.join(L))
print('Relatório:', REPORT)
for lbl, pcol, scol in PAIRS:
    print(f'  {lbl:12} Δ {br(m[scol].sum()-m[pcol].sum()):>14} ({pc(m[scol].sum(), m[pcol].sum())})')
