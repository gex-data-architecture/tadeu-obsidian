# -*- coding: utf-8 -*-
"""
gerar_datalake.py — Cataloga o Data Lake da AWS (Glue Data Catalog + ETL Jobs) e
gera a pasta `Data Lake/` no vault Obsidian. FONTE DA VERDADE = a própria AWS.

SOMENTE LEITURA na AWS: usa apenas glue.get_databases / get_tables / get_jobs.
Nunca cria/edita/dropa nada na AWS — só escreve markdown local no vault.
Re-rodável: regenera tudo e REMOVE notas órfãs (objeto que sumiu da AWS), virando
um espelho fiel do catálogo.

Uso:  python gerar_datalake.py
Requer: boto3, perfil AWS (padrão 'buygoods'), região us-east-1.
"""
import os
import re
import json
import boto3

VAULT  = r'C:\Users\tadeu\DataTeamDocs'
ROOT   = os.path.join(VAULT, 'Data Lake')
PROFILE = os.environ.get('AWS_PROFILE', 'buygoods')
REGION  = os.environ.get('AWS_REGION', 'us-east-1')

session = boto3.Session(profile_name=PROFILE, region_name=REGION)
glue = session.client('glue')
s3 = session.client('s3')
sfn = session.client('stepfunctions')  # orquestração (Step Functions)
events = session.client('events')      # encadeamento + agendamentos (EventBridge rules)
try:
    scheduler = session.client('scheduler')  # EventBridge Scheduler (serviço novo)
except Exception:
    scheduler = None

N_RUNS = 8  # quantas execuções recentes mostrar por job


def fetch_script(uri):
    """Baixa o script ETL do S3 (somente leitura). Devolve (texto, erro)."""
    if not uri or not uri.startswith('s3://'):
        return None, 'sem ScriptLocation'
    bucket, _, key = uri[len('s3://'):].partition('/')
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        return obj['Body'].read().decode('utf-8', errors='replace'), None
    except Exception as e:  # acesso negado / objeto sumiu — não derruba o resto
        return None, str(e)


def fetch_runs(name, n=N_RUNS):
    """Histórico recente de execuções via Glue get_job_runs (read-only)."""
    try:
        return glue.get_job_runs(JobName=name, MaxResults=n).get('JobRuns', [])
    except Exception:
        return []


def fmt_dt(dt):
    return dt.strftime('%Y-%m-%d %H:%M') if dt else '—'


def fmt_dur(sec):
    if not sec:
        return '—'
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    if h:
        return f'{h}h{m}m'
    if m:
        return f'{m}m{s}s'
    return f'{s}s'


def clean_err(msg):
    if not msg:
        return '—'
    msg = ' '.join(str(msg).split()).replace('|', '/')
    return (msg[:120] + '…') if len(msg) > 120 else msg


def short_arn(arn):
    return arn.split(':')[-1] if arn and ':' in arn else (arn or '')


def classify_state(st):
    """O que um estado do ASL invoca -> (kind, alvo). kind: job|crawler|sfn|lambda|sns|<Type>."""
    r = st.get('Resource', '') or ''
    p = st.get('Parameters', {}) or {}
    if 'glue:startJobRun' in r:
        return ('job', p.get('JobName') or short_arn(p.get('JobName.$', '')))
    if 'glue:startCrawler' in r:
        return ('crawler', p.get('Name') or p.get('Name.$', ''))
    if 'states:startExecution' in r:
        return ('sfn', short_arn(p.get('StateMachineArn', '') or p.get('StateMachineArn.$', '')))
    if 'lambda:invoke' in r or ':lambda:' in r:
        return ('lambda', short_arn(p.get('FunctionName', '') or p.get('FunctionName.$', '')))
    if ':sns:' in r:
        return ('sns', short_arn(p.get('TopicArn', '')))
    return (st.get('Type', ''), '')


# emojis/labels por tipo de passo, p/ a árvore de fluxo ficar legível
_STEP_ICON = {'job': '▶️ job', 'crawler': '🕷️ crawler', 'sfn': '⤵️ SFN',
              'lambda': 'ƛ lambda', 'sns': '🔔 sns'}


def walk_flow(states, start, indent=0, seen=None):
    """Percorre o ASL a partir de StartAt seguindo Next; desce em Parallel/Map.
    Devolve (linhas_markdown, refs) onde refs = {'job':set,'crawler':set,'sfn':set}."""
    lines, refs = [], {'job': set(), 'crawler': set(), 'sfn': set()}
    seen = seen if seen is not None else set()
    name = start
    pad = '  ' * indent
    while name and name not in seen and name in states:
        seen.add(name)
        st = states[name]
        typ = st.get('Type', '')
        kind, tgt = classify_state(st)
        if kind in _STEP_ICON:
            if kind in refs and tgt:
                refs[kind].add(tgt)
            link = f'[[{tgt}]]' if kind in ('job', 'crawler', 'sfn') else f'`{tgt}`'
            lines.append(f'{pad}- {_STEP_ICON[kind]} {link}')
        elif typ == 'Succeed':
            lines.append(f'{pad}- ✅ fim (sucesso)')
        elif typ == 'Fail':
            lines.append(f'{pad}- ❌ fim (falha)')
        elif typ in ('Parallel', 'Map'):
            lines.append(f'{pad}- ⑂ {typ.lower()}:')
        elif typ == 'Choice':
            lines.append(f'{pad}- ◇ escolha (`{name}`)')
        # desce em ramos paralelos / iteradores
        if typ == 'Parallel':
            for i, br in enumerate(st.get('Branches', []), 1):
                lines.append(f'{"  " * (indent + 1)}- ramo {i}:')
                sub_l, sub_r = walk_flow(br.get('States', {}), br.get('StartAt'), indent + 2, set())
                lines += sub_l
                for k in refs:
                    refs[k] |= sub_r[k]
        if typ == 'Map':
            ip = st.get('ItemProcessor') or st.get('Iterator') or {}
            if ip.get('States'):
                lines.append(f'{"  " * (indent + 1)}- para cada item:')
                sub_l, sub_r = walk_flow(ip['States'], ip.get('StartAt'), indent + 2, set())
                lines += sub_l
                for k in refs:
                    refs[k] |= sub_r[k]
        if typ in ('Succeed', 'Fail'):
            break
        name = st.get('Next')
    return lines, refs


def sfn_env(name):
    if name.endswith('-prod') or '-prod-' in name:
        return 'prod'
    if name.endswith('-develop') or '-develop-' in name:
        return 'develop'
    return ''


def target_kind(arn, input_str=None):
    """Classifica o ALVO de um agendamento (rule/scheduler) -> (kind, nome).
    Universal targets do Scheduler (`...:aws-sdk:glue:startJobRun`) trazem o nome real
    no `Input` JSON (JobName/Name/StateMachineArn), então tenta resolver por aí primeiro."""
    a = arn or ''
    try:
        inp = json.loads(input_str) if input_str else {}
    except Exception:
        inp = {}
    if 'glue:startJobRun' in a:
        return ('job', inp.get('JobName') or 'startJobRun')
    if 'glue:startCrawler' in a:
        return ('crawler', inp.get('Name') or 'startCrawler')
    if ':states:' in a or 'states:startExecution' in a or 'sfn:startExecution' in a:
        return ('sfn', short_arn(inp.get('StateMachineArn', '')) or short_arn(a))
    if ':lambda:' in a:
        return ('lambda', short_arn(a))
    if ':sns:' in a:
        return ('sns', short_arn(a))
    if ':sqs:' in a:
        return ('sqs', short_arn(a))
    if ':glue:' in a and ':job/' in a:
        return ('job', a.split(':job/')[-1])
    return (a.split(':')[2] if a.count(':') >= 2 else a, short_arn(a))


_DOW = {'1': 'dom', '2': 'seg', '3': 'ter', '4': 'qua', '5': 'qui', '6': 'sex', '7': 'sáb',
        'SUN': 'dom', 'MON': 'seg', 'TUE': 'ter', 'WED': 'qua', 'THU': 'qui',
        'FRI': 'sex', 'SAT': 'sáb', 'L': 'último dia'}


def humanize_schedule(expr):
    """cron(...)/rate(...) do EventBridge -> descrição legível em pt (horário em UTC)."""
    if not expr:
        return ''
    e = expr.strip()
    low = e.lower()
    if low.startswith('rate(') and e.endswith(')'):
        return f'a cada {e[5:-1].strip()}'
    if low.startswith('at(') and e.endswith(')'):
        return f'uma vez, em {e[3:-1].strip()} (UTC)'
    if low.startswith('cron(') and e.endswith(')'):
        f = e[5:-1].split()
        if len(f) != 6:
            return e
        mi, hr, dom, mon, dow, yr = f
        # frequência intra-dia
        if '/' in mi:
            step = mi.split('/')[-1]
            base = f' a partir do min {mi.split("/")[0]}' if mi.split('/')[0] not in ('0', '*') else ''
            freq = f'a cada {step} min{base}'
        elif '/' in hr:
            step = hr.split('/')[-1]
            mm = f'{int(mi):02d}' if mi.isdigit() else mi
            freq = f'a cada {step}h (no min {mm})'
        elif hr == '*':
            mm = f'{int(mi):02d}' if mi.isdigit() else mi
            freq = f'toda hora (no min {mm})'
        else:
            mm = f'{int(mi):02d}' if mi.isdigit() else mi
            try:  # ex.: hr "0,12" + min "30" -> "às 00:30 e 12:30"
                freq = 'às ' + ' e '.join(f'{int(h):02d}:{mm}' for h in hr.split(','))
            except ValueError:
                freq = f'às {hr}:{mm}'
        # recorrência por dia
        if dow not in ('*', '?'):
            dias = '/'.join(_DOW.get(d.upper(), d) for d in re.split(r'[,\-]', dow))
            quando = f'{dias}'
        elif dom not in ('*', '?'):
            quando = f'dia {dom}'
        else:
            quando = 'todo dia'
        return f'{quando} {freq} UTC'
    return e

# Argumentos "de infraestrutura" do Glue — escondidos pra deixar só o que é de negócio.
NOISE_ARGS = {
    '--job-language', '--TempDir', '--job-bookmark-option', '--enable-metrics',
    '--enable-observability-metrics', '--enable-continuous-cloudwatch-log',
    '--continuous-log-logGroup', '--enable-glue-datacatalog', '--enable-spark-ui',
    '--spark-event-logs-path', '--enable-job-insights', '--enable-auto-scaling',
}

WRITTEN = {}  # dir absoluto -> set de arquivos .md escritos (p/ limpar órfãos)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    WRITTEN.setdefault(os.path.dirname(path), set()).add(os.path.basename(path))


def parse_db(name):
    """gex_db_<env>_<layer> -> (env, layer). Ex.: gex_db_prod_silver -> ('prod','silver')."""
    m = re.match(r'gex_db_(develop|prod)_(bronze|silver|gold)$', name)
    return (m.group(1), m.group(2)) if m else ('', '')


def job_env(name):
    if name.endswith('-prod') or '-prod-' in name:
        return 'prod'
    if name.endswith('-develop') or '-develop-' in name:
        return 'develop'
    return ''


def job_flow(name):
    for pat in ('landing-to-bronze', 'bronze-to-silver', 'silver-to-gold', 'mysql-to-bronze'):
        if pat in name:
            return pat
    if 'to-mysql' in name or 'to_mysql' in name:
        return 'to-mysql'
    return ''


# ---------------------------------------------------------------- DATABASES + TABELAS
dbs = []
for page in glue.get_paginator('get_databases').paginate():
    dbs += [d['Name'] for d in page['DatabaseList']]

tables_by_db = {}
for db in dbs:
    env, layer = parse_db(db)
    tabs = []
    for page in glue.get_paginator('get_tables').paginate(DatabaseName=db):
        tabs += page['TableList']
    tables_by_db[db] = tabs
    for t in tabs:
        name = t['Name']
        sd = t.get('StorageDescriptor', {}) or {}
        cols = sd.get('Columns', []) or []
        parts = t.get('PartitionKeys', []) or []
        loc = sd.get('Location', '')
        fmt = (t.get('Parameters') or {}).get('classification', '')
        updated = t.get('UpdateTime', '')
        part_names = ', '.join(pk['Name'] for pk in parts) or '—'
        fm = [
            '---', 'tipo: tabela-datalake', f'database: {db}', f'ambiente: {env}',
            f'camada: {layer}', f'formato: {fmt}', f'colunas: {len(cols)}',
            f'tags: [datalake, {layer or "outro"}, {env or "outro"}]', '---',
        ]
        body = [
            f'# {name}', '', f'> `{db}` · camada **{layer or "?"}** · ambiente **{env or "?"}**', '',
            '## Propriedades', '',
            '| Propriedade | Valor |', '|---|---|',
            f'| Database | {db} |', f'| Camada | {layer} |', f'| Ambiente | {env} |',
            f'| Formato | {fmt} |', f'| Location (S3) | `{loc}` |',
            f'| Tipo | {t.get("TableType", "")} |', f'| Partições | {part_names} |',
            f'| Nº colunas | {len(cols)} |', f'| Atualizada em | {updated} |', '',
            '## Colunas', '', '| # | Coluna | Tipo |', '|---|---|---|',
        ]
        for i, c in enumerate(cols, 1):
            body.append(f'| {i} | {c["Name"]} | {c.get("Type", "")} |')
        if parts:
            body += ['', '## Chaves de partição', '']
            body += [f'- `{pk["Name"]}` ({pk.get("Type", "")})' for pk in parts]
        body += ['', '## Relacionados', '[[00-Data-Lake]]', '']
        write(os.path.join(ROOT, 'Tabelas', db, f'{name}.md'), '\n'.join(fm + [''] + body))

# ---------------------------------------------------------------- JOBS (ETL)
jobs = []
for page in glue.get_paginator('get_jobs').paginate():
    jobs += page['Jobs']

for j in jobs:
    name = j['Name']
    cmd = j.get('Command', {}) or {}
    args = j.get('DefaultArguments', {}) or {}
    env, flow = job_env(name), job_flow(name)
    biz = {k: v for k, v in args.items()
           if k not in NOISE_ARGS and not k.startswith('--enable') and not k.startswith('--continuous')}
    runs = fetch_runs(name)
    last = runs[0] if runs else {}
    fm = [
        '---', 'tipo: job-glue', f'ambiente: {env}', f'fluxo: {flow}',
        f'tipo_job: {cmd.get("Name", "")}', f'glue_version: {j.get("GlueVersion", "")}',
        f'ultima_execucao: {fmt_dt(last.get("StartedOn"))}',
        f'ultimo_estado: {last.get("JobRunState", "—")}',
        'tags: [datalake, glue-job]', '---',
    ]
    body = [
        f'# {name}', '', f'> Glue ETL · fluxo **{flow or "—"}** · ambiente **{env or "?"}**', '',
        '## Propriedades', '', '| Propriedade | Valor |', '|---|---|',
        f'| Tipo | {cmd.get("Name", "")} |',
        f'| Glue version | {j.get("GlueVersion", "")} |',
        f'| Worker | {j.get("WorkerType", "")} x{j.get("NumberOfWorkers", "")} |',
        f'| Timeout (min) | {j.get("Timeout", "")} |',
        f'| Max retries | {j.get("MaxRetries", "")} |',
        f'| Role | `{j.get("Role", "")}` |',
        f'| Script | `{cmd.get("ScriptLocation", "")}` |',
        f'| Criado | {j.get("CreatedOn", "")} |',
        f'| Modificado | {j.get("LastModifiedOn", "")} |', '',
    ]
    if biz:
        body += ['## Parâmetros de negócio', '', '| Argumento | Valor |', '|---|---|']
        body += [f'| `{k}` | {biz[k]} |' for k in sorted(biz)]
        body += ['']

    # --- Últimas execuções (Glue get_job_runs) ---
    body += ['## Últimas execuções', '']
    if runs:
        body += [f'> {N_RUNS} mais recentes (estado, duração e erro). Read-only via `get_job_runs`.', '',
                 '| Início | Estado | Duração | Erro |', '|---|---|--:|---|']
        for r in runs:
            body.append(f'| {fmt_dt(r.get("StartedOn"))} | {r.get("JobRunState", "")} | '
                        f'{fmt_dur(r.get("ExecutionTime"))} | {clean_err(r.get("ErrorMessage"))} |')
        body += ['']
    else:
        body += ['> Sem histórico de execuções (job nunca rodou ou sem acesso ao histórico).', '']

    # --- Script ETL embutido (baixado do S3, somente leitura) ---
    uri = cmd.get('ScriptLocation', '')
    code, err = fetch_script(uri)
    body += ['## Script', '', f'> Fonte: `{uri or "—"}` — baixado do S3 (read-only).', '']
    if code is not None:
        lang = 'python' if uri.endswith('.py') else ('scala' if uri.endswith('.scala') else '')
        # fence de 4 crases p/ não quebrar caso o script contenha ``` interno
        body += [f'````{lang}', code.rstrip('\n'), '````', '']
    else:
        body += [f'> ⚠️ Não foi possível ler o script: {err}', '']

    body += ['## Relacionados', '[[00-Data-Lake]]', '']
    write(os.path.join(ROOT, 'Jobs', f'{name}.md'), '\n'.join(fm + [''] + body))

# ---------------------------------------------------------------- CRAWLERS (Glue)
crawlers = []
cr_names = []
for page in glue.get_paginator('get_crawlers').paginate():
    cr_names += [c['Name'] for c in page['Crawlers']]
for i in range(0, len(cr_names), 100):  # batch_get_crawlers aceita até 100 por chamada
    crawlers += glue.batch_get_crawlers(CrawlerNames=cr_names[i:i + 100]).get('Crawlers', [])
crawlers.sort(key=lambda c: c['Name'])

for c in crawlers:
    name = c['Name']
    db = c.get('DatabaseName', '') or ''
    env, layer = parse_db(db)
    if not env:
        env = sfn_env(name)
    last = c.get('LastCrawl', {}) or {}
    s3t = [t['Path'] for t in (c.get('Targets', {}) or {}).get('S3Targets', [])]
    fm = [
        '---', 'tipo: crawler-glue', f'ambiente: {env}', f'camada: {layer}',
        f'database: {db}', f'ultimo_status: {last.get("Status", "—")}',
        'tags: [datalake, glue-crawler]', '---',
    ]
    body = [
        f'# {name}', '', f'> Glue Crawler · cataloga **{db or "?"}** ({layer or "?"} · {env or "?"})', '',
        '## Propriedades', '', '| Propriedade | Valor |', '|---|---|',
        f'| Database de destino | {("[[" + db + "/00-Indice|" + db + "]]") if db else "—"} |',
        f'| Camada / Ambiente | {layer or "—"} / {env or "—"} |',
        f'| Estado | {c.get("State", "")} |',
        f'| Último resultado | {last.get("Status", "—")} |',
        f'| Schedule | {(c.get("Schedule", {}) or {}).get("ScheduleExpression", "—") or "sob demanda (via Step Function)"} |',
        f'| Role | `{c.get("Role", "")}` |', '',
        '## Alvos S3 (o que ele varre)', '',
    ]
    body += ([f'- `{p}`' for p in s3t] or ['- —'])
    body += ['', '## Relacionados', '[[00-Data-Lake]] · [[00-Orquestracao]]', '']
    write(os.path.join(ROOT, 'Crawlers', f'{name}.md'), '\n'.join(fm + [''] + body))

# ---------------------------------------------------------------- STEP FUNCTIONS (orquestração)
def sfn_execs(arn, n=N_RUNS):
    try:
        return sfn.list_executions(stateMachineArn=arn, maxResults=n).get('executions', [])
    except Exception:
        return []

state_machines = []
for page in sfn.get_paginator('list_state_machines').paginate():
    state_machines += page['stateMachines']

sfn_info = {}  # nome -> infos (definição, fluxo, refs, execuções)
for m in state_machines:
    arn, nm = m['stateMachineArn'], m['name']
    d = sfn.describe_state_machine(stateMachineArn=arn)
    try:
        defn = json.loads(d['definition'])
    except Exception:
        defn = {'States': {}, 'StartAt': None}
    flow_lines, refs = walk_flow(defn.get('States', {}), defn.get('StartAt'))
    sfn_info[nm] = {
        'arn': arn, 'definition_raw': d.get('definition', ''),
        'role': d.get('roleArn', ''), 'created': d.get('creationDate'),
        'type': m.get('type', ''), 'flow': flow_lines, 'refs': refs,
        'execs': sfn_execs(arn),
    }

# ---- EventBridge: regras de encadeamento (job SUCCEEDED -> SFN), alertas (-> SNS) e AGENDAMENTOS (cron/rate)
chain, alerts, schedules = [], [], []
for page in events.get_paginator('list_rules').paginate():
    for r in page['Rules']:
        patt = r.get('EventPattern')
        sched_expr = r.get('ScheduleExpression')
        jobs_trig, states_cond = [], []
        if patt:
            try:
                pj = json.loads(patt)
            except Exception:
                pj = {}
            if pj.get('source') == ['aws.glue']:
                det = pj.get('detail', {}) or {}
                jobs_trig = det.get('jobName', []) or []
                states_cond = det.get('state', []) or []
        # só busca alvos se a regra interessa (encadeamento por glue OU agendamento)
        if not jobs_trig and not sched_expr:
            continue
        tg = events.list_targets_by_rule(Rule=r['Name']).get('Targets', [])
        enabled = r.get('State') == 'ENABLED'
        if sched_expr:
            tgts = [target_kind(t['Arn'], t.get('Input')) for t in tg]
            schedules.append({
                'name': r['Name'], 'source': 'rule', 'expr': sched_expr,
                'human': humanize_schedule(sched_expr), 'state': r.get('State', ''),
                'enabled': enabled, 'desc': r.get('Description', '') or '',
                'targets': tgts, 'group': '—',
            })
        if not jobs_trig:
            continue
        sfn_t = [short_arn(t['Arn']) for t in tg if ':states:' in t['Arn']]
        sns_t = [short_arn(t['Arn']) for t in tg if ':sns:' in t['Arn']]
        if sfn_t:
            chain.append({'name': r['Name'], 'jobs': set(jobs_trig), 'cond': states_cond,
                          'targets': set(sfn_t), 'enabled': enabled})
        if sns_t:
            alerts.append({'name': r['Name'], 'jobs': set(jobs_trig), 'cond': states_cond,
                           'sns': set(sns_t), 'enabled': enabled})

# ---- EventBridge Scheduler (serviço novo, separado das "rules"): list_schedules + get_schedule
if scheduler is not None:
    try:
        for page in scheduler.get_paginator('list_schedules').paginate():
            for s in page.get('Schedules', []):
                try:
                    det = scheduler.get_schedule(Name=s['Name'],
                                                 GroupName=s.get('GroupName', 'default'))
                except Exception:
                    det = {}
                expr = det.get('ScheduleExpression', '') or ''
                tgt = det.get('Target', {}) or {}
                tgt_arn = tgt.get('Arn', '')
                state = det.get('State', s.get('State', ''))
                schedules.append({
                    'name': s['Name'], 'source': 'scheduler', 'expr': expr,
                    'human': humanize_schedule(expr), 'state': state,
                    'enabled': state == 'ENABLED',
                    'desc': det.get('Description', '') or '',
                    'targets': [target_kind(tgt_arn, tgt.get('Input'))] if tgt_arn else [],
                    'group': s.get('GroupName', 'default'),
                    'timezone': det.get('ScheduleExpressionTimezone', 'UTC'),
                })
    except Exception as e:
        print('  EventBridge Scheduler indisponível (', e, ') — usando só as rules.')

def sfn_of_job(job):
    return [nm for nm, info in sfn_info.items() if job in info['refs']['job']]

# arestas de orquestração: (sfn_origem | None, job_gatilho, sfn_destino, habilitada)
edges = []
for c in chain:
    for job in c['jobs']:
        for dst in c['targets']:
            for src in (sfn_of_job(job) or [None]):
                edges.append((src, job, dst, c['enabled']))

# agendamentos que disparam diretamente uma SFN (alvo states:) -> p/ enriquecer a nota da SFN
sched_by_sfn = {}
for s in schedules:
    for kind, tgt in s['targets']:
        if kind == 'sfn':
            sched_by_sfn.setdefault(tgt, []).append(s)

def fmt_execs(execs):
    out = []
    for e in execs:
        sd = e.get('startDate')
        out.append(f'| {fmt_dt(sd)} | {e.get("status", "")} |')
    return out

# ---- 1 nota por Step Function
for nm in sorted(sfn_info):
    info = sfn_info[nm]
    env = sfn_env(nm)
    last = info['execs'][0] if info['execs'] else {}
    refs = info['refs']
    triggered_by = [(job, src) for (src, job, dst, en) in edges if dst == nm]
    downstream = [(job, dst) for (src, job, dst, en) in edges if src == nm]
    fm = [
        '---', 'tipo: step-function', f'ambiente: {env}', f'sfn_type: {info["type"]}',
        f'ultima_execucao: {fmt_dt(last.get("startDate"))}',
        f'ultimo_estado: {last.get("status", "—")}',
        'tags: [datalake, step-function, orquestracao]', '---',
    ]
    body = [
        f'# {nm}', '', f'> Step Function (orquestração) · ambiente **{env or "?"}** · tipo {info["type"]}', '',
        '## Propriedades', '', '| Propriedade | Valor |', '|---|---|',
        f'| Tipo | {info["type"]} |', f'| Role | `{info["role"]}` |',
        f'| Criada | {info["created"]} |', '',
        '## Fluxo (passo a passo do ASL)', '',
        '> Sequência dos estados a partir do `StartAt` (jobs ▶️, crawlers 🕷️, SFN ⤵️).', '',
    ]
    body += (info['flow'] or ['- (sem estados)'])
    body += ['', '## Encadeamento (EventBridge)', '']
    my_scheds = sched_by_sfn.get(nm, [])
    if my_scheds:
        body += ['**Agendada (EventBridge schedule):**']
        for s in my_scheds:
            tag = '' if s['enabled'] else ' _(desabilitada)_'
            tz = s.get('timezone', 'UTC')
            body += [f'- `{s["name"]}`{tag} — {s["human"]} · expressão `{s["expr"]}`'
                     + (f' ({tz})' if tz and tz != 'UTC' else '')
                     + (f' · {s["desc"]}' if s['desc'] else '')]
        body += ['']
    if triggered_by:
        body += ['**Disparada quando:**']
        body += [f'- job [[{job}]] = `SUCCEEDED` (via regra EventBridge)'
                 + (f' ⟶ origem provável: [[{src}]]' if src else '') for job, src in triggered_by]
        body += ['']
    elif not my_scheds:
        body += ['**Disparada quando:** gatilho externo (aplicação/webhook ou agendamento) — '
                 'não há regra de encadeamento nem agendamento apontando para ela.', '']
    if downstream:
        body += ['**Ao terminar, dispara:**']
        body += [f'- quando job [[{job}]] conclui `SUCCEEDED` ⟶ inicia [[{dst}]]' for job, dst in downstream]
        body += ['']
    body += ['## Dispara (alvos)', '',
             f'- **Jobs:** ' + (', '.join(f'[[{x}]]' for x in sorted(refs["job"])) or '—'),
             f'- **Crawlers:** ' + (', '.join(f'[[{x}]]' for x in sorted(refs["crawler"])) or '—'),
             f'- **SFN aninhadas:** ' + (', '.join(f'[[{x}]]' for x in sorted(refs["sfn"])) or '—'), '']
    body += ['## Últimas execuções', '']
    if info['execs']:
        body += [f'> {N_RUNS} mais recentes (read-only via `list_executions`).', '',
                 '| Início | Estado |', '|---|---|'] + fmt_execs(info['execs'])
        body += ['']
    else:
        body += ['> Sem execuções registradas.', '']
    body += ['## Definição (Amazon States Language)', '', '````json',
             json.dumps(json.loads(info['definition_raw']) if info['definition_raw'] else {},
                        indent=2, ensure_ascii=False), '````', '']
    body += ['## Relacionados', '[[00-Data-Lake]] · [[00-Orquestracao]]', '']
    write(os.path.join(ROOT, 'Orquestracao', f'{nm}.md'), '\n'.join(fm + [''] + body))

# ---- visão geral da orquestração: cadeias reconstruídas (árvore + mermaid)
dst_set = {dst for (_s, _j, dst, _e) in edges}
roots = sorted(nm for nm in sfn_info if nm not in dst_set)

def render_chain(nm, indent=0, seen=None):
    seen = seen if seen is not None else set()
    out = []
    pad = '  ' * indent
    out.append(f'{pad}- [[{nm}]]')
    if nm in seen:
        out.append(f'{pad}  - ↺ (já mostrado)')
        return out
    seen.add(nm)
    for job, dst in sorted([(j, d) for (s, j, d, e) in edges if s == nm]):
        out.append(f'{pad}  - ▶️ job [[{job}]] `SUCCEEDED` ⟶')
        out += render_chain(dst, indent + 2, seen)
    return out

ov = [
    '---', 'tipo: indice-orquestracao', 'gerado_por: skill/catalogo-datalake',
    'tags: [datalake, orquestracao, step-function]', '---',
    '# 🔗 Orquestração do Data Lake (Step Functions + EventBridge)', '',
    f'> **{len(sfn_info)} Step Functions**, **{len(crawlers)} crawlers** e **{len(schedules)} agendamentos**. '
    'As SFN rodam jobs/crawlers em sequência;',
    '> o encadeamento **entre** SFNs é por **regras EventBridge** (quando um job conclui `SUCCEEDED`, inicia a próxima SFN);',
    '> e as cadeias **começam** por **agendamentos** (cron/rate) — ver seção *Agendamentos*.',
    '> **Não editar à mão** — regerável pela skill `catalogo-datalake`.', '',
    '## Cadeias (a partir de cada gatilho externo)', '',
    '> Raiz = SFN sem regra de encadeamento apontando para ela (início por aplicação/webhook ou agenda).', '',
]
for r in roots:
    ov += render_chain(r)
    ov += ['']

# mermaid: só as arestas (visão de grafo)
ov += ['## Grafo (mermaid)', '', '```mermaid', 'flowchart TD']
def mid(s):
    return re.sub(r'\W', '_', s)
for nm in sfn_info:
    ov.append(f'  {mid(nm)}["{nm}"]')
for (src, job, dst, en) in sorted(set(edges)):
    if src:
        ov.append(f'  {mid(src)} -->|{job} ✓| {mid(dst)}')
    else:
        ov.append(f'  ext_{mid(dst)}(["job {job} ✓"]) --> {mid(dst)}')
ov += ['```', '']

if alerts:
    ov += ['## Alertas de falha (EventBridge → SNS)', '']
    for a in alerts:
        jlinks = ', '.join(f'[[{j}]]' for j in sorted(a['jobs']))
        sns = ', '.join(f'`{x}`' for x in sorted(a['sns']))
        cond = '/'.join(a['cond']) or 'FAILED'
        st = '' if a['enabled'] else ' _(desabilitada)_'
        ov += [f'- `{a["name"]}`{st}: job(s) {jlinks} = `{cond}` ⟶ {sns}']
    ov += ['']

# ---- Agendamentos (EventBridge rules com cron/rate + EventBridge Scheduler)
ov += ['## Agendamentos (EventBridge)', '']
if schedules:
    n_on = sum(1 for s in schedules if s['enabled'])
    ov += [f'> {len(schedules)} agendamento(s) — **{n_on} ativo(s)**, {len(schedules) - n_on} desabilitado(s). '
           'Horário em **UTC** salvo indicação de timezone. Estes são os gatilhos que iniciam as cadeias na hora marcada.', '',
           '| Status | Agendamento | Quando | Expressão | Dispara | Origem |',
           '|---|---|---|---|---|---|']
    for s in sorted(schedules, key=lambda x: (not x['enabled'], x['name'])):
        status = '🟢 ativo' if s['enabled'] else '⚪ off'
        alvos = ', '.join(
            (f'[[{tgt}]]' if kind in ('sfn', 'job', 'crawler') else f'`{kind}:{tgt}`')
            for kind, tgt in s['targets']) or '—'
        tz = s.get('timezone', 'UTC')
        quando = s['human'] + (f' ({tz})' if tz and tz != 'UTC' else '')
        origem = 'rule' if s['source'] == 'rule' else f'scheduler/{s.get("group", "default")}'
        ov.append(f'| {status} | `{s["name"]}` | {quando} | `{s["expr"]}` | {alvos} | {origem} |')
    ov += ['']
else:
    ov += ['> Nenhum agendamento (cron/rate) encontrado nas regras EventBridge nem no EventBridge Scheduler. '
           'As SFN parecem iniciar por aplicação/webhook ou só por encadeamento.', '']

ov += ['## Crawlers', '']
for c in crawlers:
    ov.append(f'- [[{c["Name"]}]] → `{c.get("DatabaseName", "")}` ({c.get("LastCrawl", {}).get("Status", "—")})')
ov += ['', '## Relacionados', '[[00-Data-Lake]]', '']
write(os.path.join(ROOT, 'Orquestracao', '00-Orquestracao.md'), '\n'.join(ov))

# ---------------------------------------------------------------- ÍNDICE
total_tabs = sum(len(v) for v in tables_by_db.values())
idx = [
    '---', 'tipo: indice-datalake', 'gerado_por: skill/catalogo-datalake',
    'tags: [datalake, indice]', '---',
    '# 🗄️ Data Lake — Catálogo (AWS Glue)', '',
    f'> Gerado da AWS Glue + Step Functions (conta 406933028738, `{REGION}`, perfil `{PROFILE}`). **Não editar à mão** — regerável.',
    f'> **{total_tabs} tabelas** em {len(dbs)} databases · **{len(jobs)} jobs** ETL · '
    f'**{len(state_machines)} Step Functions** · **{len(crawlers)} crawlers** · '
    f'**{len(schedules)} agendamentos**.',
    '> Arquitetura **medallion**: `landing → bronze → silver → gold → MySQL` (develop e prod).',
    '> Orquestração, cadeias e **agendamentos** (cron/rate): **[[00-Orquestracao]]**.', '',
    '## Databases (Glue Data Catalog)', '',
    '| Database | Ambiente | Camada | Tabelas |', '|---|---|---|---|',
]
for db in sorted(dbs):
    env, layer = parse_db(db)
    idx.append(f'| `{db}` | {env} | {layer} | {len(tables_by_db[db])} |')

idx += ['', '## Tabelas por database', '']
for db in sorted(dbs):
    if not tables_by_db[db]:
        continue
    idx.append(f'### `{db}`')
    for t in sorted(tables_by_db[db], key=lambda x: x['Name']):
        idx.append(f'- [[{db}/{t["Name"]}|{t["Name"]}]]')
    idx.append('')

idx += ['## Jobs ETL por fluxo', '']
order = ['mysql-to-bronze', 'landing-to-bronze', 'bronze-to-silver', 'silver-to-gold', 'to-mysql', '']
labels = {
    'mysql-to-bronze': 'MySQL → Bronze', 'landing-to-bronze': 'Landing → Bronze',
    'bronze-to-silver': 'Bronze → Silver', 'silver-to-gold': 'Silver → Gold',
    'to-mysql': 'Gold/Silver → MySQL', '': 'Outros',
}
for fl in order:
    grp = sorted([j['Name'] for j in jobs if job_flow(j['Name']) == fl])
    if not grp:
        continue
    idx.append(f'### {labels[fl]}')
    idx += [f'- [[{n}]]' for n in grp]
    idx.append('')

# Step Functions (orquestração) por ambiente
idx += ['## Step Functions (orquestração)', '',
        'Visão das cadeias e do grafo: **[[00-Orquestracao]]**.', '']
for amb in ('prod', 'develop', ''):
    grp = sorted(nm for nm in sfn_info if sfn_env(nm) == amb)
    if not grp:
        continue
    idx.append(f'### {amb or "outros"}')
    idx += [f'- [[{n}]]' for n in grp]
    idx.append('')

# Crawlers por database
idx += ['## Crawlers (Glue)', '']
cr_by_db = {}
for c in crawlers:
    cr_by_db.setdefault(c.get('DatabaseName', '') or '(sem db)', []).append(c['Name'])
for db in sorted(cr_by_db):
    idx.append(f'### `{db}`')
    idx += [f'- [[{n}]]' for n in sorted(cr_by_db[db])]
    idx.append('')

# Agendamentos (cron/rate) — resumo; detalhes/horários em 00-Orquestracao
idx += ['## Agendamentos (EventBridge)', '',
        'Horários (UTC), expressões e alvos: **[[00-Orquestracao]]**.', '']
if schedules:
    for s in sorted(schedules, key=lambda x: (not x['enabled'], x['name'])):
        status = '🟢' if s['enabled'] else '⚪'
        alvos = ', '.join(f'[[{tgt}]]' if kind in ('sfn', 'job', 'crawler') else tgt
                          for kind, tgt in s['targets']) or '—'
        idx.append(f'- {status} `{s["name"]}` — {s["human"]} → {alvos}')
else:
    idx.append('- _(nenhum agendamento cron/rate encontrado)_')
idx.append('')

idx += ['## Relacionados', '[[00-Indice]] · [[00-Orquestracao]] · skill `catalogo-datalake` · skill `limpeza-banco`', '']
write(os.path.join(ROOT, '00-Data-Lake.md'), '\n'.join(idx))

# ---------------------------------------------------------------- LIMPEZA DE ÓRFÃOS
# Pasta gerada = espelho da AWS. Remove .md que não foram escritos agora (objeto sumiu).
removidos = 0
for base, _dirs, files in os.walk(ROOT):
    keep = WRITTEN.get(base, set())
    for fn in files:
        if fn.endswith('.md') and fn not in keep:
            os.remove(os.path.join(base, fn))
            removidos += 1
            print(f'  órfã removida: {os.path.relpath(os.path.join(base, fn), ROOT)}')
# remove subpastas de Tabelas/ que ficaram vazias (database removido na AWS)
tdir = os.path.join(ROOT, 'Tabelas')
if os.path.isdir(tdir):
    for d in os.listdir(tdir):
        p = os.path.join(tdir, d)
        if os.path.isdir(p) and not os.listdir(p):
            os.rmdir(p)

print(f'Data Lake gerado: {total_tabs} tabelas em {len(dbs)} databases, {len(jobs)} jobs, '
      f'{len(state_machines)} step functions, {len(crawlers)} crawlers, {len(schedules)} agendamentos. '
      f'Órfãs removidas: {removidos}.')
print('Pasta:', ROOT)
