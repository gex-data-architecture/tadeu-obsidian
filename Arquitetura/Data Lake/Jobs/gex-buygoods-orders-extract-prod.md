---
tipo: job-glue
ambiente: prod
fluxo: 
tipo_job: pythonshell
glue_version: 5.1
ultima_execucao: 2026-06-12 02:00
ultimo_estado: SUCCEEDED
tags: [datalake, glue-job]
---

# gex-buygoods-orders-extract-prod

> Glue ETL · fluxo **—** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | pythonshell |
| Glue version | 5.1 |
| Worker |  x |
| Timeout (min) | 480 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/buygoods_orders_extract.py` |
| Criado | 2026-06-01 13:14:31.844000-03:00 |
| Modificado | 2026-06-01 13:14:31.844000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--ACCOUNTS_KEY` | buygoods_orders/config/buygoods_accounts.csv |
| `--BRONZE_PREFIX` | buygoods_orders/raw |
| `--BUCKET` | gex-datalake-bronze-prod |
| `--CONTROL_PREFIX` | buygoods_orders/control/checkpoints |
| `--MAX_WORKERS` | 10 |
| `--PAGE_SIZE` | 100 |
| `--SLEEP` | 2.0 |
| `--START_DATE` | 2026-04-01 |

## Últimas execuções

> 8 mais recentes (estado, duração e erro). Read-only via `get_job_runs`.

| Início | Estado | Duração | Erro |
|---|---|--:|---|
| 2026-06-12 02:00 | SUCCEEDED | 1h48m | — |
| 2026-06-11 08:07 | SUCCEEDED | 2h11m | — |
| 2026-06-10 17:15 | STOPPED | 1h22m | — |
| 2026-06-10 17:12 | STOPPED | — | — |
| 2026-06-01 15:00 | STOPPED | 12m16s | — |
| 2026-06-01 13:35 | FAILED | 48m47s | Command failed with exit code 1 |

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/buygoods_orders_extract.py` — baixado do S3 (read-only).

````python
# -*- coding: utf-8 -*-
"""
BuyGoods -> Bronze (Glue Python Shell job)
==========================================
Varre TODAS as contas (lidas de um CSV no S3) em paralelo (um worker por conta,
respeitando o rate limit por token), pagina dia a dia, e grava os orders CRUS
(todos os campos como string) em parquet particionado no S3:

    s3://<BUCKET>/<BRONZE_PREFIX>/acct_id=<id>/year_month=<YYYY-MM>/orders_<YYYY-MM-DD>.parquet

Retomável: cada dia concluido vai pra um checkpoint JSON no S3; reexecucoes pulam
o que ja foi gravado.

Argumentos (todos opcionais, passados como --CHAVE valor):
    --BUCKET            (default: api-buygoods-teste-tadeu)
    --ACCOUNTS_KEY      (default: config/buygoods_accounts.csv)
    --BRONZE_PREFIX     (default: bronze/buygoods/orders)
    --CONTROL_PREFIX    (default: control/buygoods/checkpoints)
    --START_DATE        (default: 2026-04-01)         YYYY-MM-DD
    --END_DATE          (default: hoje em UTC)         YYYY-MM-DD
    --MAX_WORKERS       (default: 10)   contas em paralelo
    --SLEEP             (default: 2.0)  seg entre requests (por conta)
    --PAGE_SIZE         (default: 100)
    --ACCOUNT_IDS       (default: vazio = todas)  ex: "12340,12501" para testar
    --FORCE             (default: 0)  1 = ignora checkpoint e reprocessa tudo
    --LOOKBACK_DAYS     (default: 0)  >0 ativa modo INCREMENTAL: re-extrai os
                        ultimos N dias de CRIACAO (START=hoje-N, END=hoje),
                        forca re-pull e NAO sobrescreve o checkpoint historico.
                        Usado nos agendamentos para capturar reembolsos/
                        chargebacks que mudam o estado de pedidos recentes.

                        Valores usados na orquestracao:
                          LOOKBACK_DAYS=1   -> a cada 2h: janela D-0 + D-1
                                               (ontem -> hoje = 2 dias). Pega
                                               vendas novas rapido; rapido/barato.
                          LOOKBACK_DAYS=30  -> 1x por dia na madrugada: janela
                                               D-30. Pega reembolsos/chargebacks
                                               tardios em pedidos antigos (~98,8%
                                               dos reembolsos acontecem ate 30d).
"""
import sys, os, io, json, time, random, threading
from datetime import date, datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ----------------------------------------------------------------------
# Args
# ----------------------------------------------------------------------
def get_args(argv):
    defaults = {
        "BUCKET": "api-buygoods-teste-tadeu",
        "ACCOUNTS_KEY": "config/buygoods_accounts.csv",
        "BRONZE_PREFIX": "bronze/buygoods/orders",
        "CONTROL_PREFIX": "control/buygoods/checkpoints",
        "START_DATE": "2026-04-01",
        "END_DATE": datetime.now(timezone.utc).date().isoformat(),
        "MAX_WORKERS": "10",
        "SLEEP": "2.0",
        "PAGE_SIZE": "100",
        "ACCOUNT_IDS": "",
        "FORCE": "0",
        "LOOKBACK_DAYS": "0",
    }
    out = dict(defaults)
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok.startswith("--"):
            key = tok[2:]
            val = argv[i + 1] if i + 1 < len(argv) else ""
            out[key] = val
            i += 2
        else:
            i += 1
    return out

ARGS = get_args(sys.argv[1:])

BUCKET         = ARGS["BUCKET"]
ACCOUNTS_KEY   = ARGS["ACCOUNTS_KEY"]
BRONZE_PREFIX  = ARGS["BRONZE_PREFIX"].strip("/")
CONTROL_PREFIX = ARGS["CONTROL_PREFIX"].strip("/")
START_DATE     = date.fromisoformat(ARGS["START_DATE"])
END_DATE       = date.fromisoformat(ARGS["END_DATE"])
MAX_WORKERS    = int(ARGS["MAX_WORKERS"])
SLEEP          = float(ARGS["SLEEP"])
PAGE_SIZE      = int(ARGS["PAGE_SIZE"])
ACCOUNT_IDS    = [x.strip() for x in ARGS["ACCOUNT_IDS"].split(",") if x.strip()]
FORCE          = ARGS["FORCE"] == "1"
LOOKBACK_DAYS  = int(ARGS.get("LOOKBACK_DAYS", "0") or "0")

# Modo incremental (a cada 2h): re-extrai janela movel de dias de CRIACAO.
# Como o pedido BuyGoods e mutavel (reembolso/chargeback no mesmo registro),
# precisamos reconsultar o dia de criacao para capturar updates.
INCREMENTAL = LOOKBACK_DAYS > 0
if INCREMENTAL:
    _today = datetime.now(timezone.utc).date()
    START_DATE = _today - timedelta(days=LOOKBACK_DAYS)
    END_DATE   = _today

BASE_URL    = "https://admin3.buygoods.com/public/v2/orders.php"
# Backoff de 429: a API nao manda Retry-After. Backoff exponencial comecando
# curto (5s) -> 10 -> 20 -> 40 -> teto 60s. O inicio curto economiza nos
# throttles leves; o teto de 60s e necessario porque a janela de rate-limit da
# API leva ~60s pra resetar (cap menor faz a pagina esgotar as retries e falhar).
# MAX_RETRIES alto (~10 min de paciencia por pagina) garante zero perda de pagina.
BASE_429_WAIT = 5
MAX_429_WAIT  = 60
MAX_RETRIES = 12
REQUEST_TIMEOUT = 30

s3 = boto3.client("s3")
_print_lock = threading.Lock()

def log(msg):
    with _print_lock:
        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}", flush=True)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def daterange(d1, d2):
    for nd in range((d2 - d1).days + 1):
        yield d1 + timedelta(days=nd)

def extract_records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "orders", "results", "items", "rows"):
            if key in payload and isinstance(payload[key], list):
                return payload[key]
        list_values = [v for v in payload.values() if isinstance(v, list)]
        if len(list_values) == 1:
            return list_values[0]
    return []

def fetch_page(session, account_id, day_str, offset):
    params = {"account_id": account_id, "start_date": day_str,
              "end_date": day_str, "limit": PAGE_SIZE, "offset": offset}
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
            if r.status_code == 429:
                ra = r.headers.get("Retry-After")
                if ra and ra.isdigit():
                    wait = float(ra)
                else:
                    base = min(BASE_429_WAIT * (2 ** (attempt - 1)), MAX_429_WAIT)
                    # JITTER (equal jitter): metade fixa + metade aleatoria.
                    # Sem isso, todos os workers (mesmo IP) re-tentavam no MESMO
                    # segundo apos um 429 -> novo pico -> 429 de novo ("thundering
                    # herd"), fazendo paginas azaradas esgotarem as 12 tentativas.
                    # O jitter espalha os retries e quebra a sincronia.
                    wait = base * 0.5 + random.uniform(0, base * 0.5)
                log(f"  [429] acc={account_id} {day_str} off={offset} tent {attempt} -> {wait:.0f}s")
                time.sleep(wait)
                continue
            if r.status_code >= 500:
                wait = min(2 ** attempt, 60)
                log(f"  [{r.status_code}] acc={account_id} {day_str} tent {attempt} -> {wait:.0f}s")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            wait = min(2 ** attempt, 60)
            log(f"  [EXC] acc={account_id} {day_str} tent {attempt}: {str(e)[:80]} -> {wait:.0f}s")
            time.sleep(wait)
    raise RuntimeError(f"Falha apos {MAX_RETRIES} tentativas (acc={account_id}, day={day_str}, off={offset})")

def fetch_day(session, account_id, day_str):
    registros, offset = [], 0
    while True:
        payload = fetch_page(session, account_id, day_str, offset)
        recs = extract_records(payload)
        registros.extend(recs)
        time.sleep(SLEEP)
        if len(recs) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return registros

def records_to_parquet_bytes(records, account_id, day_str):
    df = pd.DataFrame(records)
    # tudo string (bronze cru); estruturas viram JSON string
    for col in df.columns:
        df[col] = df[col].apply(
            lambda v: v if (v is None or isinstance(v, str)) else json.dumps(v, ensure_ascii=False)
        )
    df = df.astype("string")
    df["_extract_account_id"] = account_id
    df["_extract_date"] = day_str
    df["_extracted_at"] = datetime.now(timezone.utc).isoformat()
    table = pa.Table.from_pandas(df, preserve_index=False)
    # forca todas as colunas como string no schema parquet
    table = table.cast(pa.schema([(f.name, pa.string()) for f in table.schema]))
    buf = io.BytesIO()
    pq.write_table(table, buf, compression="snappy")
    buf.seek(0)
    return buf.getvalue()

# ----------------------------------------------------------------------
# Checkpoint (por conta)
# ----------------------------------------------------------------------
def ckpt_key(account_id):
    return f"{CONTROL_PREFIX}/{account_id}.json"

def load_ckpt(account_id):
    # incremental sempre re-extrai a janela (estado dos pedidos muda)
    if FORCE or INCREMENTAL:
        return set()
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=ckpt_key(account_id))
        data = json.loads(obj["Body"].read())
        return set(data.get("done_days", []))
    except s3.exceptions.NoSuchKey:
        return set()
    except Exception:
        return set()

def save_ckpt(account_id, done_days):
    body = json.dumps({"account_id": account_id,
                       "done_days": sorted(done_days),
                       "updated_at": datetime.now(timezone.utc).isoformat()})
    s3.put_object(Bucket=BUCKET, Key=ckpt_key(account_id),
                  Body=body.encode("utf-8"), ContentType="application/json")

# ----------------------------------------------------------------------
# Worker por conta
# ----------------------------------------------------------------------
def process_account(acc):
    account_id   = str(acc["account_id"]).strip()
    account_name = str(acc.get("account_name", ""))
    token        = str(acc["token"]).strip()

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    })

    done = load_ckpt(account_id)
    total_orders, days_done_now = 0, 0
    log(f"START acc={account_id} ({account_name}) | ja feitos: {len(done)} dias")

    for d in daterange(START_DATE, END_DATE):
        day_str = d.isoformat()
        if day_str in done:
            continue
        registros = fetch_day(session, account_id, day_str)
        if registros:
            ym = day_str[:7]  # YYYY-MM
            key = f"{BRONZE_PREFIX}/acct_id={account_id}/year_month={ym}/orders_{day_str}.parquet"
            data = records_to_parquet_bytes(registros, account_id, day_str)
            s3.put_object(Bucket=BUCKET, Key=key, Body=data)
            total_orders += len(registros)
        # marca dia (com ou sem dados) e persiste checkpoint
        done.add(day_str)
        days_done_now += 1
        # no incremental NAO sobrescreve o checkpoint historico (so re-pull da janela)
        if not INCREMENTAL:
            save_ckpt(account_id, done)

    log(f"DONE  acc={account_id} ({account_name}) | +{days_done_now} dias | {total_orders} orders nesta run")
    return {"account_id": account_id, "account_name": account_name,
            "orders": total_orders, "days_processed": days_done_now}

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    log(f"Config: bucket={BUCKET} periodo={START_DATE}..{END_DATE} "
        f"workers={MAX_WORKERS} sleep={SLEEP}s force={FORCE} "
        f"incremental={INCREMENTAL} lookback_days={LOOKBACK_DAYS}")
    obj = s3.get_object(Bucket=BUCKET, Key=ACCOUNTS_KEY)
    accounts = pd.read_csv(io.BytesIO(obj["Body"].read()), dtype=str).to_dict("records")
    if ACCOUNT_IDS:
        accounts = [a for a in accounts if str(a["account_id"]).strip() in ACCOUNT_IDS]
    log(f"Contas a processar: {len(accounts)}")

    results, errors = [], []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(process_account, a): a for a in accounts}
        for fut in as_completed(futs):
            a = futs[fut]
            try:
                results.append(fut.result())
            except Exception as e:
                errors.append({"account_id": a.get("account_id"), "error": str(e)})
                log(f"ERRO acc={a.get('account_id')}: {str(e)[:200]}")

    # 2a PASSADA (sequencial): re-tenta as contas que falharam na passada
    # paralela. Sem a contencao dos N workers dividindo o mesmo IP, o 429
    # transitorio quase sempre se resolve. Idempotente: no incremental reextrai
    # a janela e regrava as mesmas chaves no S3; no full, o checkpoint por dia
    # faz pular o que ja foi gravado. So o que sobrar daqui e erro real.
    if errors:
        failed_ids = {str(e["account_id"]).strip() for e in errors}
        retry_accounts = [a for a in accounts if str(a.get("account_id")).strip() in failed_ids]
        log("=" * 60)
        log(f"[RETRY] {len(retry_accounts)} conta(s) falharam na 1a passada; "
            f"aguardando 60s p/ resetar a janela de rate-limit e re-tentando "
            f"SEQUENCIALMENTE...")
        time.sleep(60)
        errors = []
        for a in retry_accounts:
            try:
                results.append(process_account(a))
            except Exception as e:
                errors.append({"account_id": a.get("account_id"), "error": str(e)})
                log(f"ERRO (2a passada) acc={a.get('account_id')}: {str(e)[:200]}")

    total_orders = sum(r["orders"] for r in results)
    log("=" * 60)
    log(f"FIM. contas_ok={len(results)} erros={len(errors)} total_orders_run={total_orders}")
    if errors:
        log(f"CONTAS COM ERRO (apos 2a passada): {json.dumps(errors)[:1000]}")
        # so falha o job se a conta falhou ATE na 2a passada sequencial -> a o
        # problema e real (token invalido, API fora, etc.) e o alerta procede.
        raise SystemExit(f"{len(errors)} conta(s) falharam mesmo apos retry")

if __name__ == "__main__":
    main()
````

## Relacionados
[[00-Data-Lake]]
