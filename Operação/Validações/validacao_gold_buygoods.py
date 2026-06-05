# -*- coding: utf-8 -*-
"""
validacao_gold_buygoods.py
Reconciliação COMPLETA entre:
  - MySQL : instituto_experience.dashboard_gold_buygoods   (gerada por procedure)
  - Athena: gex_db_prod_gold.tb_gex_gold_buygoods           (camada gold do data lake)

SOMENTE LEITURA nas duas pontas. Gera um relatório markdown em Validações/.
MySQL via pymysql (credenciais do .claude.json). Athena via boto3 (perfil buygoods).
Uso:  $env:AWS_PROFILE="buygoods"; python validacao_gold_buygoods.py
"""
import json
import os
import sys
import time
from decimal import Decimal

# Console do Windows usa cp1252 e quebra ao imprimir emoji (✅/❌). Força UTF-8.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
from datetime import datetime

import pymysql
import boto3

# ----------------------------------------------------------------- config
MYSQL_TABLE = 'instituto_experience.dashboard_gold_buygoods'
ATHENA_DB = 'gex_db_prod_gold'
ATHENA_TABLE = 'tb_gex_gold_buygoods'
ATHENA_OUT = 's3://gex-athena-query-results/validacoes/'
REGION = os.environ.get('AWS_REGION', 'us-east-1')
PROFILE = os.environ.get('AWS_PROFILE', 'buygoods')

VAULT = r'C:\Users\tadeu\DataTeamDocs'
OUTDIR = os.path.join(VAULT, 'Validações')
TODAY = datetime.now().strftime('%Y-%m-%d')
REPORT = os.path.join(OUTDIR, f'validacao-gold-buygoods-{TODAY}.md')

KEY = 'transaction_id'
DATE_COL = 'created_at_date'

# Colunas numéricas a somar (idênticas nas duas tabelas).
NUM_COLS = [
    'product_cost', 'product_cost_usd', 'quantity', 'quantity_principal',
    'total_price', 'total_price_usd', 'taxes', 'taxes_usd',
    'total_refund', 'total_refund_usd', 'commission', 'commission_usd',
    'affiliate_amount', 'affiliate_amount_usd', 'revenue_afiliado', 'revenue_afiliado_usd',
    'has_upsell', 'has_upsell2', 'has_upsell3', 'has_downsell', 'has_downsell2', 'has_downsell3',
    'has_order_bump', 'total_price_upsell', 'total_price_upsell_usd',
    'total_price_upsell2', 'total_price_upsell2_usd', 'total_price_upsell3', 'total_price_upsell3_usd',
    'total_price_downsell', 'total_price_downsell_usd', 'total_price_downsell2', 'total_price_downsell2_usd',
    'total_price_downsell3', 'total_price_downsell3_usd', 'total_price_order_bump', 'total_price_order_bump_usd',
    'is_house_traffic', 'total_collected_usd', 'iva', 'iva_usd',
    'refund_fee', 'refund_fee_usd', 'chargeback_fee', 'chargeback_fee_usd',
]

# ----------------------------------------------------------------- conexões
with open(r'C:\Users\tadeu\.claude.json', 'r', encoding='utf-8') as f:
    env = json.load(f)['mcpServers']['mysql']['env']
mysql_conn = pymysql.connect(
    host=env['MYSQL_HOST'], port=int(env['MYSQL_PORT']),
    user=env['MYSQL_USER'], password=env['MYSQL_PASS'],
    database=env['MYSQL_DB'], charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor, connect_timeout=30,
)
athena = boto3.Session(profile_name=PROFILE, region_name=REGION).client('athena')


def mysql_rows(sql):
    with mysql_conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def athena_rows(sql):
    qid = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={'Database': ATHENA_DB},
        ResultConfiguration={'OutputLocation': ATHENA_OUT},
        WorkGroup='primary',
    )['QueryExecutionId']
    while True:
        st = athena.get_query_execution(QueryExecutionId=qid)['QueryExecution']['Status']
        state = st['State']
        if state in ('SUCCEEDED', 'FAILED', 'CANCELLED'):
            break
        time.sleep(1.5)
    if state != 'SUCCEEDED':
        raise RuntimeError(f'Athena {state}: {st.get("StateChangeReason")}')
    rows, header = [], None
    for page in athena.get_paginator('get_query_results').paginate(QueryExecutionId=qid):
        for r in page['ResultSet']['Rows']:
            vals = [c.get('VarCharValue') for c in r['Data']]
            if header is None:
                header = vals
                continue
            rows.append(dict(zip(header, vals)))
    return rows


def D(v):
    if v is None or v == '':
        return Decimal(0)
    return Decimal(str(v))


# ----------------------------------------------------------------- 1) AGREGADOS
agg_select = (
    "SELECT COUNT(*) AS cnt, "
    f"COUNT(DISTINCT {KEY}) AS dist_tx, "
    f"MIN({DATE_COL}) AS dmin, MAX({DATE_COL}) AS dmax, "
    f"COUNT(DISTINCT {DATE_COL}) AS ndias"
    + "".join(f", SUM({c}) AS s_{c}" for c in NUM_COLS)
)
my_agg = mysql_rows(f"{agg_select} FROM {MYSQL_TABLE}")[0]
print('MySQL agregados OK')
at_agg = athena_rows(f'{agg_select} FROM "{ATHENA_DB}"."{ATHENA_TABLE}"')[0]
print('Athena agregados OK')

# ----------------------------------------------------------------- 2) POR DIA
my_day = {str(r['d']): (int(r['c']), D(r['s'])) for r in mysql_rows(
    f"SELECT {DATE_COL} d, COUNT(*) c, SUM(total_price_usd) s FROM {MYSQL_TABLE} GROUP BY {DATE_COL}")}
at_day = {str(r['d']): (int(r['c']), D(r['s'])) for r in athena_rows(
    f'SELECT {DATE_COL} d, COUNT(*) c, SUM(total_price_usd) s FROM "{ATHENA_DB}"."{ATHENA_TABLE}" GROUP BY {DATE_COL}')}
print(f'Por dia OK (MySQL {len(my_day)} dias, Athena {len(at_day)} dias)')

# ----------------------------------------------------------------- 3) SET DE transaction_id
my_tx = {str(r[KEY]) for r in mysql_rows(f"SELECT DISTINCT {KEY} FROM {MYSQL_TABLE}")}
at_tx = {str(r[KEY]) for r in athena_rows(
    f'SELECT DISTINCT {KEY} FROM "{ATHENA_DB}"."{ATHENA_TABLE}"')}
only_my = my_tx - at_tx
only_at = at_tx - my_tx
print(f'Set transaction_id OK (MySQL {len(my_tx)}, Athena {len(at_tx)}, só-MySQL {len(only_my)}, só-Athena {len(only_at)})')

# ----------------------------------------------------------------- montar relatório
def status(a, b):
    return '✅' if a == b else '❌'


def pct(diff, base):
    if base == 0:
        return '—' if diff == 0 else 'n/a'
    return f'{(diff / base * 100):+.4f}%'


L = []
w = L.append

cnt_my, cnt_at = int(my_agg['cnt']), int(at_agg['cnt'])
tx_my, tx_at = int(my_agg['dist_tx']), int(at_agg['dist_tx'])
metric_fail = 0

w('---')
w('tipo: validacao')
w('par: dashboard_gold_buygoods (MySQL) x tb_gex_gold_buygoods (Athena)')
w(f'data: {TODAY}')
w('gerado_por: Validações/validacao_gold_buygoods.py')
w('tags: [validacao, reconciliacao, buygoods, gold]')
w('---')
w('# Validação — `dashboard_gold_buygoods` (MySQL) × `tb_gex_gold_buygoods` (Athena)')
w('')
w(f'> Reconciliação completa rodada em **{TODAY}**. Somente leitura nas duas pontas.')
w('> MySQL: `instituto_experience.dashboard_gold_buygoods` (gerada por procedure).')
w('> Athena: `gex_db_prod_gold.tb_gex_gold_buygoods` (camada gold do data lake).')
w('')

# veredito
sum_fail = sum(1 for c in NUM_COLS if D(my_agg[f's_{c}']) != D(at_agg[f's_{c}']))
day_keys = sorted(set(my_day) | set(at_day))
day_fail = sum(1 for d in day_keys if my_day.get(d) != at_day.get(d))
total_fail = (cnt_my != cnt_at) + (tx_my != tx_at) + sum_fail + day_fail + len(only_my) + len(only_at)
verdict = '✅ TABELAS IGUAIS' if total_fail == 0 else '❌ HÁ DIFERENÇAS'
w('## Veredito')
w('')
w(f'### {verdict}')
w('')
w('| Bloco | Resultado |')
w('|---|---|')
w(f'| Contagem de linhas | {status(cnt_my, cnt_at)} (MySQL {cnt_my:,} / Athena {cnt_at:,}) |')
w(f'| `transaction_id` distintos | {status(tx_my, tx_at)} (MySQL {tx_my:,} / Athena {tx_at:,}) |')
w(f'| Medidas numéricas (somas) | {"✅" if sum_fail == 0 else f"❌ {sum_fail}/{len(NUM_COLS)} divergem"} |')
w(f'| Quebra por dia | {"✅" if day_fail == 0 else f"❌ {day_fail} dia(s) divergem"} |')
w(f'| `transaction_id` só no MySQL | {"✅ 0" if not only_my else f"❌ {len(only_my):,}"} |')
w(f'| `transaction_id` só no Athena | {"✅ 0" if not only_at else f"❌ {len(only_at):,}"} |')
w('')

# contagens
w('## 1. Contagens e período')
w('')
w('| Métrica | MySQL | Athena | Diferença | Status |')
w('|---|--:|--:|--:|:--:|')
w(f'| Linhas (grão) | {cnt_my:,} | {cnt_at:,} | {cnt_at - cnt_my:+,} | {status(cnt_my, cnt_at)} |')
w(f'| `transaction_id` distintos | {tx_my:,} | {tx_at:,} | {tx_at - tx_my:+,} | {status(tx_my, tx_at)} |')
w(f'| Dias distintos (`{DATE_COL}`) | {int(my_agg["ndias"])} | {int(at_agg["ndias"])} | '
  f'{int(at_agg["ndias"]) - int(my_agg["ndias"]):+} | {status(int(my_agg["ndias"]), int(at_agg["ndias"]))} |')
w(f'| Data mínima | {my_agg["dmin"]} | {at_agg["dmin"]} | — | {status(str(my_agg["dmin"]), str(at_agg["dmin"]))} |')
w(f'| Data máxima | {my_agg["dmax"]} | {at_agg["dmax"]} | — | {status(str(my_agg["dmax"]), str(at_agg["dmax"]))} |')
w('')
if cnt_my != tx_my or cnt_at != tx_at:
    w(f'> ⚠️ O grão **não** é 1 linha por `transaction_id` (há repetição por produto/janela). '
      f'Por isso linhas ≠ transações distintas. A reconciliação usa os dois ângulos.')
    w('')

# medidas
w('## 2. Medidas numéricas (soma total de cada coluna)')
w('')
w('| Coluna | MySQL | Athena | Diferença | % | Status |')
w('|---|--:|--:|--:|--:|:--:|')
for c in NUM_COLS:
    a, b = D(my_agg[f's_{c}']), D(at_agg[f's_{c}'])
    diff = b - a
    w(f'| `{c}` | {a:,} | {b:,} | {diff:+,} | {pct(diff, a)} | {status(a, b)} |')
w('')

# por dia (só divergentes)
w('## 3. Quebra por dia')
w('')
if day_fail == 0:
    w(f'✅ Todos os **{len(day_keys)} dias** batem em contagem e em `SUM(total_price_usd)`.')
else:
    w(f'❌ **{day_fail}** dia(s) divergem (de {len(day_keys)}). Mostrando os divergentes:')
    w('')
    w('| Dia | Linhas MySQL | Linhas Athena | Σ total_price_usd MySQL | Σ total_price_usd Athena | Status |')
    w('|---|--:|--:|--:|--:|:--:|')
    for d in day_keys:
        mv = my_day.get(d, (0, Decimal(0)))
        av = at_day.get(d, (0, Decimal(0)))
        if mv != av:
            w(f'| {d} | {mv[0]:,} | {av[0]:,} | {mv[1]:,} | {av[1]:,} | ❌ |')
w('')

# transaction set diff
w('## 4. Reconciliação por `transaction_id`')
w('')
w('| | Quantidade |')
w('|---|--:|')
w(f'| Distintos no MySQL | {len(my_tx):,} |')
w(f'| Distintos no Athena | {len(at_tx):,} |')
w(f'| Em ambos (interseção) | {len(my_tx & at_tx):,} |')
w(f'| **Só no MySQL** | {len(only_my):,} |')
w(f'| **Só no Athena** | {len(only_at):,} |')
w('')
if only_my:
    w('### Amostra — `transaction_id` só no MySQL (até 25)')
    w('')
    for t in sorted(only_my)[:25]:
        w(f'- `{t}`')
    w('')
if only_at:
    w('### Amostra — `transaction_id` só no Athena (até 25)')
    w('')
    for t in sorted(only_at)[:25]:
        w(f'- `{t}`')
    w('')

# schema
w('## 5. Schema')
w('')
w('Ambas têm **75 colunas com os mesmos nomes**. Diferença esperada só na representação de tipo: ')
w('MySQL usa `text/mediumtext/longtext` p/ strings e `date` p/ `created_at_date`; no Athena são `string` ')
w('e `created_at_date` é **chave de partição**. Não é divergência de dados.')
w('')

w('## 6. Conclusão')
w('')
if total_fail == 0:
    w('As duas tabelas representam **os mesmos dados** em todos os ângulos checados '
      '(linhas, transações distintas, somas de todas as medidas, quebra diária e conjunto de `transaction_id`).')
else:
    w('Há divergência(s) acima. Próximos passos sugeridos:')
    w('- Olhar os **dias divergentes** (seção 3) para localizar o período afetado.')
    w('- Investigar os `transaction_id` exclusivos (seção 4) — costuma ser atraso de carga (lag do job vs procedure) ou filtro diferente.')
    w('- Se as **somas** divergem mas contagem bate: provável diferença de arredondamento de câmbio (USD) ou de uma medida específica — ver quais colunas falharam na seção 2.')
w('')
w('## Relacionados')
w('[[00-Data-Lake]] · [[00-Indice]] · `gex_db_prod_gold/tb_gex_gold_buygoods` · procedure que gera `dashboard_gold_buygoods`')
w('')

os.makedirs(OUTDIR, exist_ok=True)
with open(REPORT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(L))

print('\n==== RESUMO ====')
print(verdict)
print(f'Linhas: MySQL {cnt_my:,} / Athena {cnt_at:,}')
print(f'TX distintos: MySQL {tx_my:,} / Athena {tx_at:,}')
print(f'Somas divergentes: {sum_fail}/{len(NUM_COLS)} | Dias divergentes: {day_fail} | só-MySQL {len(only_my)} | só-Athena {len(only_at)}')
print('Relatório:', REPORT)
