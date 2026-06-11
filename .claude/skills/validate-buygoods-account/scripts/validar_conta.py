# -*- coding: utf-8 -*-
"""
validar_conta.py  (skill: validar-conta-buygoods)
Validação CAMPO A CAMPO da silver `tb_gex_buygoods_unified` para UMA conta
(account_id) contra o extrato diário "Transactions" do BuyGoods (Excel). Total + por dia.

Alinhamento (extrato Transactions): o Excel rotula o dia **D** com dados de **D-1**;
a silver é lida pelo **timestamp da plataforma** => Excel(D) == silver(D-1).

De-para (campo Excel -> silver):
  Sales=total_collected_usd ; Sale Taxes=iva_usd ; Fees=taxes_usd ; Commissions=affiliate_amount_usd
  Refunds=total_refund_usd(não-cbk) ; Chargebacks=total_refund_usd+chargeback_fee_usd(cbk)
  Sale Tax Refunds=iva_usd(refunded) ; Fee Voids / Commission Voids = NÃO deriváveis (política de void)
  Amount/Balance/JV%/Alerts/Shipping = settlement/meta, sem equivalente transacional.

SOMENTE LEITURA no MySQL. Período derivado do Excel (silver = Excel - 1 dia).
Uso:  python validar_conta.py [caminho_do_excel] [account_id]
      (defaults: Transactions_*.xlsx mais recente em Downloads; account_id do nome do arquivo)
Requer: pandas, openpyxl, pymysql.
"""
import json, os, sys, glob
import pandas as pd
import pymysql
from datetime import timedelta
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

VAULT = r'C:\Users\tadeu\DataTeamDocs'
OUTDIR = os.path.join(VAULT, 'Operação', 'Validações')


def find_default():
    c = glob.glob(os.path.join(os.path.expanduser('~'), 'Downloads', 'Transactions_*.xls*'))
    return max(c, key=os.path.getmtime) if c else None


XLS = sys.argv[1] if len(sys.argv) > 1 else find_default()
if not XLS or not os.path.isfile(XLS):
    sys.exit('Excel "Transactions" não encontrado — passe o caminho como argumento.')
ACC = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(os.path.basename(XLS))[0].split('_')[-1]

eng = 'xlrd' if XLS.lower().endswith('.xls') else 'openpyxl'
# alguns exports têm linhas de preâmbulo (Transactions/Criteria/Date Range) antes do cabeçalho real:
# detecta a linha que contém a coluna 'Date'.
_raw = pd.read_excel(XLS, engine=eng, header=None)
_hdr = next((i for i in range(min(15, len(_raw)))
             if 'Date' in [str(v).strip() for v in _raw.iloc[i].tolist()]), None)
if _hdr is None:
    sys.exit('Cabeçalho não encontrado (nenhuma linha com a coluna "Date").')
e = pd.read_excel(XLS, engine=eng, header=_hdr)
e.columns = [str(c).strip() for c in e.columns]
e['d'] = pd.to_datetime(e['Date']).dt.normalize()
ECOLS = ['Sales', 'Commissions', 'Refunds', 'Chargebacks', 'Commissions Voids', 'Fee Voids',
         'Fees', 'Sale Tax Refunds', 'Sale Taxes', 'Shipping/Handling', 'Amount']
for c in ECOLS:
    e[c] = pd.to_numeric(e[c], errors='coerce').fillna(0)
e = e.groupby('d', as_index=False)[ECOLS].sum()
e['sd'] = (e['d'] - timedelta(days=1)).dt.date
INI = min(e['sd']).isoformat(); FIM = max(e['sd']).isoformat()
REPORT = os.path.join(OUTDIR, f'validacao-conta-buygoods-{ACC}.md')

env = json.load(open(r'C:\Users\tadeu\.claude.json', encoding='utf-8'))['mcpServers']['mysql']['env']
cn = pymysql.connect(host=env['MYSQL_HOST'], port=int(env['MYSQL_PORT']), user=env['MYSQL_USER'],
                     password=env['MYSQL_PASS'], database=env['MYSQL_DB'], charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor)


def q(sql):
    with cn.cursor() as c:
        c.execute(sql); return c.fetchall()


sale = q(f"""SELECT LEFT(datetime_platform,10) d,
  SUM(total_collected_usd) sales, SUM(iva_usd) sale_taxes, SUM(taxes_usd) fees,
  SUM(affiliate_amount_usd) commissions
 FROM instituto_experience.tb_gex_buygoods_unified
 WHERE account_id='{ACC}' AND LEFT(datetime_platform,10) BETWEEN '{INI}' AND '{FIM}'
 GROUP BY LEFT(datetime_platform,10)""")
# Fee Voids e Sale Tax Refunds: PROPORCIONAL ao que foi estornado (refund parcial só devolve parte
# da fee/imposto). frac = total_refund_usd / total_collected_usd. O valor "cheio" superestima parciais.
refd = q(f"""SELECT LEFT(datetime_refunded_platform,10) d,
  SUM(CASE WHEN NOT cbk THEN total_refund_usd ELSE 0 END) refunds,
  SUM(CASE WHEN cbk THEN total_refund_usd+chargeback_fee_usd ELSE 0 END) chargebacks,
  SUM(CASE WHEN NOT cbk THEN taxes_usd*(total_refund_usd/NULLIF(total_collected_usd,0)) ELSE 0 END) fee_voids,
  SUM(CASE WHEN NOT cbk THEN iva_usd*(total_refund_usd/NULLIF(total_collected_usd,0)) ELSE 0 END) sale_tax_refunds
 FROM (SELECT *, (payment_status='chargeback' OR transaction_type='Chargeback') cbk
       FROM instituto_experience.tb_gex_buygoods_unified WHERE account_id='{ACC}') t
 WHERE LEFT(datetime_refunded_platform,10) BETWEEN '{INI}' AND '{FIM}'
 GROUP BY LEFT(datetime_refunded_platform,10)""")
s = pd.DataFrame(sale); r = pd.DataFrame(refd)
for df in (s, r):
    df['d'] = pd.to_datetime(df['d']).dt.date
for c in ['sales', 'sale_taxes', 'fees', 'commissions']:
    s[c] = s[c].astype(float)
for c in ['refunds', 'chargebacks', 'fee_voids', 'sale_tax_refunds']:
    r[c] = r[c].astype(float)

m = e.merge(s, left_on='sd', right_on='d', how='left', suffixes=('', '_s')) \
     .merge(r, left_on='sd', right_on='d', how='left', suffixes=('', '_r')).fillna(0)

PAIRS = [('Sales', 'Sales', 'sales'), ('Commissions', 'Commissions', 'commissions'),
         ('Sale Taxes', 'Sale Taxes', 'sale_taxes'), ('Fees', 'Fees', 'fees'),
         ('Refunds', 'Refunds', 'refunds'), ('Chargebacks', 'Chargebacks', 'chargebacks'),
         ('Fee Voids', 'Fee Voids', 'fee_voids'), ('Sale Tax Refunds', 'Sale Tax Refunds', 'sale_tax_refunds')]


def br(v):
    return f'{v:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def pcl(s_, p_):
    return '—' if abs(p_) < 0.005 else f'{(s_-p_)/p_*100:+.2f}%'


tots = {lbl: (m[ec].sum(), m[sc].sum()) for lbl, ec, sc in PAIRS}

# auto-detecta "quebra" nos refunds: primeiro dia (com P relevante) a partir do qual Δ% < -20%
mb = m.sort_values('d')
brk = None
for _, x in mb.iterrows():
    if x['Refunds'] > 100 and x['refunds'] < x['Refunds'] * 0.8:
        brk = x['d']; break

L = []; w = L.append
w('---'); w('tipo: validacao')
w(f'par: tb_gex_buygoods_unified (silver) x extrato BuyGoods — conta account_id={ACC}')
w(f'data: {FIM}'); w(f'periodo_silver: {INI} a {FIM}'); w('moeda: USD')
w('gerado_por: skill/validar-conta-buygoods')
w(f'tags: [validacao, reconciliacao, buygoods, silver, conta, "account/{ACC}"]'); w('---')
w(f'# Validação campo a campo — conta `{ACC}`')
w('')
w('> Silver `tb_gex_buygoods_unified` × extrato diário "Transactions" da plataforma. '
  'Alinhamento: **Excel(D) = silver(D−1)** na base de **timestamp da plataforma**. Somente leitura.')
w('')
w('## De-para (campo Excel → silver)')
w(''); w('| Campo Excel | Campo silver | Δ% / Status |'); w('|---|---|---|')
DEPARA = [('Sales', 'total_collected_usd', 'Sales'), ('Commissions', 'affiliate_amount_usd', 'Commissions'),
          ('Sale Taxes', 'iva_usd', 'Sale Taxes'), ('Fees', 'taxes_usd', 'Fees'),
          ('Refunds', 'total_refund_usd (não-cbk)', 'Refunds'),
          ('Chargebacks', 'total_refund_usd + chargeback_fee_usd (cbk)', 'Chargebacks'),
          ('Fee Voids', 'taxes_usd × (total_refund/total_collected)', 'Fee Voids'),
          ('Sale Tax Refunds', 'iva_usd × (total_refund/total_collected)', 'Sale Tax Refunds')]
for ec, sv, key in DEPARA:
    P, S = tots[key]
    w(f'| {ec} | `{sv}` | {pcl(S, P)} |')
w('| Commission Voids | — | ❌ não derivável — afiliado mantém a comissão (estorno é exceção) |')
w('| Amount / Balance | — | ⛔ settlement (allowances/holds) |')
w('| JV% / Alerts / Shipping / Product Notes | — | ⛔ meta / sem dado financeiro |')
w('')
# total
w('## Total do período (campo a campo)')
w(''); w('| Campo | Plataforma | Silver | Δ | Δ% |'); w('|---|--:|--:|--:|--:|')
for lbl, ec, sc in PAIRS:
    P, S = tots[lbl]
    w(f'| {lbl} | {br(P)} | {br(S)} | {br(S-P)} | {pcl(S, P)} |')
w('')
# por dia (deltas)
w('## Por dia — Δ silver − plataforma (USD)')
w(''); w('> Diferença por campo e por dia (rótulo = data do Excel; silver = D−1).'); w('')
w('| Dia | ' + ' | '.join(lbl for lbl, _, _ in PAIRS) + ' |')
w('|---' * (len(PAIRS) + 1) + '|')
for _, x in mb.iterrows():
    w(f"| {x['d'].strftime('%d/%m')} | " + ' | '.join(br(x[sc] - x[ec]) for _, ec, sc in PAIRS) + ' |')
w('| **Total** | ' + ' | '.join(f"**{br(tots[lbl][1]-tots[lbl][0])}**" for lbl, _, _ in PAIRS) + ' |')
w('')
# refunds por dia
w('## Refunds por dia — plataforma × silver (USD)')
w(''); w('> Refunds por `datetime_refunded_platform`. Use para localizar quebras com data.'); w('')
w('| Dia | Plataforma | Silver | Δ | Δ% |'); w('|---|--:|--:|--:|--:|')
for _, x in mb.iterrows():
    if x['Refunds'] == 0 and x['refunds'] == 0:
        continue
    w(f"| {x['d'].strftime('%d/%m')} | {br(x['Refunds'])} | {br(x['refunds'])} | {br(x['refunds']-x['Refunds'])} | {pcl(x['refunds'], x['Refunds'])} |")
P, S = tots['Refunds']
w(f"| **Total** | **{br(P)}** | **{br(S)}** | **{br(S-P)}** | **{pcl(S,P)}** |")
w('')
# observações
w('## Observações')
w('')
w('1. **Alinhamento:** Excel(D) = dados de D−1; silver lida por `datetime_platform`/`datetime_refunded_platform` '
  '(o `created_at_date` está +1h e desalinha dias movimentados).')
w('2. **Nomes "trocados" na silver:** Commissions (afiliado) = `affiliate_amount_usd`; Amount (líquido do vendor) '
  '= `commission_usd`; Fees (taxa BuyGoods) = `taxes_usd`.')
if brk:
    w(f'3. **Refunds: quebra com data** — divergência forte (>20%) a partir de **{brk.strftime("%d/%m")}** '
      '(ver "Refunds por dia"). Se o pior NÃO é o período mais recente, não é lag → investigar **ingestão de estornos** '
      'a partir dessa data.')
else:
    w('3. **Refunds** reconciliam sem quebra de data relevante no período.')
w('4. **Fee Voids e Sale Tax Refunds são proporcionais:** a BuyGoods estorna fee e imposto, mas em refund '
  'parcial só a parte estornada (`× total_refund/total_collected`) — somar o valor cheio superestima. '
  '**Commission Voids** é a exceção: o afiliado MANTÉM a comissão (estorno é raríssimo), então não é derivável.')
w('5. **Amount/Balance** = settlement (incluem allowances/holds), fora da base transacional.')
w('')
w('## Reproduzir')
w(f'- Plataforma: `{os.path.basename(XLS)}` (account_id={ACC}).')
w('- Skill `validar-conta-buygoods` (`scripts/validar_conta.py`), read-only no MySQL.')
w('')
w('## Relacionados')
w('- Validação agregada: skill `validar-plataforma-buygoods`')
w('- Silver doc: [[Fontes de Dados/Buygoods/doc_silver_buygoods]] · [[CLAUDE]] · [[log]]')
w('')

os.makedirs(OUTDIR, exist_ok=True)
open(REPORT, 'w', encoding='utf-8').write('\n'.join(L))
print('Relatório:', REPORT, '| conta:', ACC, '| quebra refunds:', brk)
for lbl, ec, sc in PAIRS:
    P, S = tots[lbl]
    print(f'  {lbl:18} Δ {br(S-P):>14} ({pcl(S,P)})')
