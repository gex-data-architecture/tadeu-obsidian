# -*- coding: utf-8 -*-
"""
organizar_eventos.py
Separa as notas de eventos do vault em Eventos/ENABLE e Eventos/DISABLE conforme
o STATUS real no MySQL (information_schema.EVENTS). ENABLE = só os eventos ativos.

FONTE DA VERDADE = o banco. SOMENTE LEITURA no MySQL — apenas move arquivos .md
locais, nunca toca no banco. Re-rodável: reflete o status atual a cada execução
(evento que vira DISABLED migra de ENABLE -> DISABLE sozinho na próxima rodada).

Uso:  python organizar_eventos.py [schema]      (default: instituto_experience)
Requer: pymysql + credenciais MySQL no .claude.json (servidor MCP `mysql`).
"""
import json
import os
import sys
import shutil

# Console do Windows (cp1252) quebra com emoji/acentos — força UTF-8.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import pymysql

VAULT = r'C:\Users\tadeu\DataTeamDocs'
SCHEMA = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('MYSQL_SCHEMA', 'instituto_experience')
EVENTS_DIR = os.path.join(VAULT, 'Banco de Dados', 'MySQL', SCHEMA, 'Eventos')
ENABLE = os.path.join(EVENTS_DIR, 'ENABLE')
DISABLE = os.path.join(EVENTS_DIR, 'DISABLE')

# ----------------------------------------------------------------- MySQL (read-only)
with open(r'C:\Users\tadeu\.claude.json', 'r', encoding='utf-8') as f:
    env = json.load(f)['mcpServers']['mysql']['env']
conn = pymysql.connect(
    host=env['MYSQL_HOST'], port=int(env['MYSQL_PORT']),
    user=env['MYSQL_USER'], password=env['MYSQL_PASS'],
    database=env['MYSQL_DB'], charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor, connect_timeout=30,
)
with conn.cursor() as cur:
    cur.execute(
        "SELECT EVENT_NAME, STATUS FROM information_schema.EVENTS WHERE EVENT_SCHEMA=%s",
        (SCHEMA,),
    )
    events = cur.fetchall()

if not os.path.isdir(EVENTS_DIR):
    sys.exit(f'Pasta de eventos não encontrada: {EVENTS_DIR}\n'
             f'(rode antes o gerador 3_gerar_vault.py para o schema "{SCHEMA}")')

os.makedirs(ENABLE, exist_ok=True)
os.makedirs(DISABLE, exist_ok=True)


def copies_of(name):
    """Todos os caminhos onde a nota do evento existe hoje (flat ou em subpasta)."""
    out = []
    for d in (EVENTS_DIR, ENABLE, DISABLE):
        p = os.path.join(d, f'{name}.md')
        if os.path.isfile(p):
            out.append(p)
    return out


moved = {'ENABLE': 0, 'DISABLE': 0}
missing = []
for e in events:
    name = e['EVENT_NAME']
    is_on = (e['STATUS'] or '').upper() == 'ENABLED'   # SLAVESIDE_DISABLED/DISABLED -> DISABLE
    bucket, label = (ENABLE, 'ENABLE') if is_on else (DISABLE, 'DISABLE')
    dst = os.path.join(bucket, f'{name}.md')
    paths = copies_of(name)
    if not paths:
        missing.append(name)
        continue
    if any(os.path.abspath(p) == os.path.abspath(dst) for p in paths):
        # já está no lugar certo — só limpa cópias duplicadas em outras pastas
        for p in paths:
            if os.path.abspath(p) != os.path.abspath(dst):
                os.remove(p)
    else:
        if os.path.exists(dst):
            os.remove(dst)
        shutil.move(paths[0], dst)
        moved[label] += 1
        for p in paths[1:]:
            if os.path.exists(p):
                os.remove(p)

# notas .md sem evento correspondente no banco (evento dropado) — só avisa
event_names = {e['EVENT_NAME'] for e in events}
orphans = []
for d in (EVENTS_DIR, ENABLE, DISABLE):
    for fn in os.listdir(d):
        if fn.endswith('.md') and fn[:-3] not in event_names:
            orphans.append(os.path.relpath(os.path.join(d, fn), EVENTS_DIR))

n_on = sum(1 for e in events if (e['STATUS'] or '').upper() == 'ENABLED')
print(f'Schema: {SCHEMA}')
print(f'Eventos no banco: {len(events)}  ({n_on} ENABLED / {len(events) - n_on} DISABLED)')
print(f'Movidos nesta rodada -> ENABLE: {moved["ENABLE"]} | DISABLE: {moved["DISABLE"]}')
if missing:
    print(f'AVISO sem nota no vault (rode o 3_gerar_vault.py): {", ".join(missing)}')
if orphans:
    print(f'AVISO nota .md sem evento no banco: {", ".join(orphans)}')
print('Pasta:', EVENTS_DIR)
