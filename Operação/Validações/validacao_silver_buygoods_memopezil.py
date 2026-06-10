# -*- coding: utf-8 -*-
"""
validacao_silver_buygoods_memopezil.py
Validação COMPLETA (campo a campo) da silver `tb_gex_buygoods_unified` para a conta
**Memopezil (account_id=12340)** contra o extrato diário da plataforma BuyGoods (Excel).

Regras de alinhamento (confirmadas no de-para):
  - O Excel rotula cada dia com a data **D**, mas os valores são do dia **D-1**.
  - A silver é agrupada pelo **timestamp da plataforma** (datetime_platform / datetime_refunded_platform).
  => Excel(D)  ==  silver(D-1) na base de timestamp-plataforma.

De-para campo Excel -> silver:
  Sales=total_collected_usd ; Sale Taxes=iva_usd ; Fees=taxes_usd ; Commissions=affiliate_amount_usd
  Refunds=total_refund_usd(não-cbk) ; Chargebacks=total_refund_usd+chargeback_fee_usd(cbk)
  Fee Voids=taxes_usd(refunded) ; Sale Tax Refunds=iva_usd(refunded)
  Commission Voids ~ affiliate_amount_usd(refunded)  [a silver NÃO rastreia void real -> diverge]
  Amount/Balance/JV%/Alerts/Shipping = settlement/meta, sem equivalente transacional na silver.

Somente leitura no MySQL. Gera markdown em Operação/Validações/.
"""
import json, os, sys
import pandas as pd
import pymysql
from datetime import timedelta
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

VAULT = r'C:\Users\tadeu\DataTeamDocs'
OUTDIR = os.path.join(VAULT, 'Operação', 'Validações')
XLS = r'C:\Users\tadeu\Downloads\Transactions_06-10-2026_450_12340.xlsx'
ACC = '12340'
INI, FIM = '2026-04-01', '2026-06-09'          # janela da SILVER (Excel é D+1)
REPORT = os.path.join(OUTDIR, 'validacao-silver-buygoods-memopezil-12340.md')

# ---------- plataforma (Excel diário; D mostra dados de D-1) ----------
e = pd.read_excel(XLS, engine='openpyxl', header=0)
e.columns = [str(c).strip() for c in e.columns]
e['d'] = pd.to_datetime(e['Date']).dt.normalize()
ECOLS = ['Sales', 'Commissions', 'Refunds', 'Chargebacks', 'Commissions Voids', 'Fee Voids',
         'Fees', 'Sale Tax Refunds', 'Sale Taxes', 'Shipping/Handling', 'Amount']
for c in ECOLS:
    e[c] = pd.to_numeric(e[c], errors='coerce').fillna(0)
e = e.groupby('d', as_index=False)[ECOLS].sum()
e['sd'] = (e['d'] - timedelta(days=1)).dt.date     # silver day = Excel - 1

# ---------- silver (MySQL) ----------
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
refd = q(f"""SELECT LEFT(datetime_refunded_platform,10) d,
  SUM(CASE WHEN NOT cbk THEN total_refund_usd ELSE 0 END) refunds,
  SUM(CASE WHEN cbk THEN total_refund_usd+chargeback_fee_usd ELSE 0 END) chargebacks,
  SUM(CASE WHEN NOT cbk THEN affiliate_amount_usd ELSE 0 END) commission_voids,
  SUM(CASE WHEN NOT cbk THEN taxes_usd ELSE 0 END) fee_voids,
  SUM(CASE WHEN NOT cbk THEN iva_usd ELSE 0 END) sale_tax_refunds
 FROM (SELECT *, (payment_status='chargeback' OR transaction_type='Chargeback') cbk
       FROM instituto_experience.tb_gex_buygoods_unified WHERE account_id='{ACC}') t
 WHERE LEFT(datetime_refunded_platform,10) BETWEEN '{INI}' AND '{FIM}'
 GROUP BY LEFT(datetime_refunded_platform,10)""")
s = pd.DataFrame(sale); r = pd.DataFrame(refd)
for df in (s, r):
    df['d'] = pd.to_datetime(df['d']).dt.date
for c in ['sales', 'sale_taxes', 'fees', 'commissions']:
    s[c] = s[c].astype(float)
for c in ['refunds', 'chargebacks', 'commission_voids', 'fee_voids', 'sale_tax_refunds']:
    r[c] = r[c].astype(float)

m = e.merge(s, left_on='sd', right_on='d', how='left', suffixes=('', '_s')) \
     .merge(r, left_on='sd', right_on='d', how='left', suffixes=('', '_r')).fillna(0)

# pares (rótulo, coluna Excel, coluna silver)
PAIRS = [('Sales', 'Sales', 'sales'), ('Commissions', 'Commissions', 'commissions'),
         ('Sale Taxes', 'Sale Taxes', 'sale_taxes'), ('Fees', 'Fees', 'fees'),
         ('Refunds', 'Refunds', 'refunds'), ('Chargebacks', 'Chargebacks', 'chargebacks'),
         ('Fee Voids', 'Fee Voids', 'fee_voids'), ('Sale Tax Refunds', 'Sale Tax Refunds', 'sale_tax_refunds'),
         ('Commission Voids', 'Commissions Voids', 'commission_voids')]


def br(v):
    return f'{v:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def pcl(s_, p_):
    return '—' if abs(p_) < 0.005 else f'{(s_-p_)/p_*100:+.2f}%'


L = []; w = L.append
w('---')
w('tipo: validacao')
w('par: tb_gex_buygoods_unified (silver) x extrato BuyGoods — conta Memopezil (account_id=12340)')
w('data: 2026-06-10')
w(f'periodo_silver: {INI} a {FIM}')
w('moeda: USD')
w('gerado_por: Operação/Validações/validacao_silver_buygoods_memopezil.py')
w('tags: [validacao, reconciliacao, buygoods, silver, conta, memopezil]')
w('---')
w('# Validação campo a campo — Memopezil (account_id=12340)')
w('')
w('> Silver `tb_gex_buygoods_unified` × extrato diário da plataforma (Excel). Alinhamento: **Excel(D) = silver(D−1)** '
  'na base de **timestamp da plataforma**. Somente leitura.')
w('')
w('## De-para (campo Excel → silver)')
w('')
w('| Campo Excel | Campo silver | Status |')
w('|---|---|---|')
w('| Sales | `total_collected_usd` | ✅ reconcilia (~−0,7%) |')
w('| Commissions | `affiliate_amount_usd` | ✅ reconcilia (~−0,6%) |')
w('| Sale Taxes | `iva_usd` | ✅ reconcilia (~−0,6%) |')
w('| Fees | `taxes_usd` | ✅ reconcilia (~−0,7%) |')
w('| Refunds | `total_refund_usd` (não-chargeback) | ⚠️ −12,6% — **quebra a partir de 26/05** (ver "Refunds por dia") |')
w('| Chargebacks | `total_refund_usd + chargeback_fee_usd` (chargeback) | ⚠️ −7,7% (mesma quebra) |')
w('| Sale Tax Refunds | `iva_usd` dos refunded | ⚠️ −7% (acompanha o refund/lag) |')
w('| Fee Voids | — | ❌ **não derivável** — a BuyGoods raramente estorna a fee (mantém a taxa) |')
w('| Commission Voids | — | ❌ **não derivável** — afiliado mantém a comissão; void é exceção |')
w('| Amount / Balance | — | ⛔ settlement (inclui allowances/holds) — não-transacional |')
w('| JV Percentage / Alerts / Shipping/Handling / Product Notes | — | ⛔ meta / sem dado financeiro na silver |')
w('')

# total
w('## Total do período (campo a campo)')
w('')
w('| Campo | Plataforma (Excel) | Silver | Δ | Δ% |')
w('|---|--:|--:|--:|--:|')
tots = {}
for lbl, ec, sc in PAIRS:
    P, S = m[ec].sum(), m[sc].sum()
    tots[lbl] = (P, S)
    w(f'| {lbl} | {br(P)} | {br(S)} | {br(S-P)} | {pcl(S, P)} |')
w('')
w('> ✅ **Sale-side reconcilia** (Sales/Commissions/Sale Taxes/Fees ~−0,65% uniforme). ⚠️ **Refunds/Chargebacks** '
  'divergem por uma **quebra na captura de estornos a partir de 26/05** (ver seção "Refunds por dia"). ❌ **Voids** (Commission/Fee) '
  'não são deriváveis: dependem da política de void da BuyGoods (comissão/fee em geral **não** são estornadas), '
  'enquanto a silver só tem o valor original — por isso somar "afiliado/fee dos estornados" superestima o void.')
w('')

# por dia — deltas
w('## Por dia — Δ silver − plataforma (USD)')
w('')
w('> Diferença por campo e por dia (rotulado pela data do **Excel**; silver = D−1). Use para localizar divergências.')
w('')
hdr = '| Dia | ' + ' | '.join(lbl for lbl, _, _ in PAIRS) + ' |'
w(hdr)
w('|---' * (len(PAIRS) + 1) + '|')
for _, x in m.sort_values('d').iterrows():
    cells = ' | '.join(br(x[sc] - x[ec]) for _, ec, sc in PAIRS)
    w(f"| {x['d'].strftime('%d/%m')} | {cells} |")
tline = ' | '.join(f"**{br(tots[lbl][1]-tots[lbl][0])}**" for lbl, _, _ in PAIRS)
w(f'| **Total** | {tline} |')
w('')

# refunds por dia (foco da investigação de lag)
w('## Refunds por dia — plataforma × silver (USD)')
w('')
w('> Refunds atribuídos por `datetime_refunded_platform` (Excel D = silver D−1). **Reconcilia até 25/05 e '
  'despenca a partir de 26/05** — não é lag recente uniforme, é uma quebra com data.')
w('')
w('| Dia (Excel) | Plataforma | Silver | Δ | Δ% |')
w('|---|--:|--:|--:|--:|')
for _, x in m.sort_values('d').iterrows():
    P, S = x['Refunds'], x['refunds']
    if P == 0 and S == 0:
        continue
    w(f"| {x['d'].strftime('%d/%m')} | {br(P)} | {br(S)} | {br(S-P)} | {pcl(S,P)} |")
w(f"| **Total** | **{br(m['Refunds'].sum())}** | **{br(m['refunds'].sum())}** "
  f"| **{br(m['refunds'].sum()-m['Refunds'].sum())}** | **{pcl(m['refunds'].sum(), m['Refunds'].sum())}** |")
w('')

w('## Observações')
w('')
w('1. **Alinhamento crítico:** o Excel rotula o dia **D** com dados de **D−1**; e a silver precisa ser lida pelo '
  '`datetime_platform`/`datetime_refunded_platform` (o `created_at_date` está +1h e desalinha dias movimentados).')
w('2. **Nomes "trocados" na silver:** o que a plataforma chama de **Commissions** (afiliado) é o '
  '`affiliate_amount_usd`; o **Amount** (líquido do vendor) é o `commission_usd`; e **Fees** (taxa BuyGoods) é o `taxes_usd`.')
w('3. **Refunds: quebra com data (26/05), não lag uniforme.** A análise por dia mostra reconciliação **<1%/dia '
  'até 25/05** e um **despencar a partir de 26/05** (fundo em 27–29/05: silver pega ~18% dos refunds; ex.: 28/05 '
  '132k vs 22k), com recuperação parcial (~−10%) em junho. Como o pior NÃO é o período mais recente, **não é lag '
  'de ingestão** — é uma **degradação datada** na captura de estornos. ⚠️ Coincide com 26/05 (incidente Meta Ads) — '
  'possível causa comum na infra de ingestão, a confirmar.')
w('4. **Voids não são deriváveis da silver:** Commission Voids e Fee Voids dependem da **política da BuyGoods** '
  '(em geral comissão e fee NÃO são estornadas no refund). A plataforma reporta voids ~0; a silver só tem o '
  'valor original, então qualquer fórmula "imposto/fee/afiliado dos estornados" superestima.')
w('5. **Amount/Balance** não são comparáveis: incluem **allowances/holds** (reservas) lançados pela BuyGoods, '
  'que não existem na base transacional.')
w('')
w('## Reproduzir')
w(f'- Plataforma: `{os.path.basename(XLS)}` (Downloads).')
w('- Silver: este script (`validacao_silver_buygoods_memopezil.py`), read-only no MySQL.')
w('')
w('## Relacionados')
w('- Validação agregada (plataforma): [[validacao-silver-buygoods-plataforma-2026-06-09]]')
w('- Silver doc: [[Fontes de Dados/Buygoods/doc_silver_buygoods]] · [[CLAUDE]] · [[log]]')
w('')

os.makedirs(OUTDIR, exist_ok=True)
open(REPORT, 'w', encoding='utf-8').write('\n'.join(L))
print('Relatório:', REPORT)
for lbl, _, _ in PAIRS:
    P, S = tots[lbl]
    print(f'  {lbl:18} plat {br(P):>15} | silver {br(S):>15} | Δ {br(S-P):>12} ({pcl(S,P)})')
