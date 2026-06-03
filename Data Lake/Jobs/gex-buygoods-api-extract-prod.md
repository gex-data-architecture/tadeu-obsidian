---
tipo: job-glue
ambiente: prod
fluxo: 
tipo_job: pythonshell
glue_version: 5.1
ultima_execucao: —
ultimo_estado: —
tags: [datalake, glue-job]
---

# gex-buygoods-api-extract-prod

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
| Script | `s3://gex-datalake-bronze-prod/scripts/buygoods_api/job_extract.py` |
| Criado | 2026-05-28 10:39:22.061000-03:00 |
| Modificado | 2026-05-28 10:39:22.061000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--date_from` | 2026-01-01 |
| `--date_to` | 2026-01-31 |
| `--env` | prod |
| `--extra-py-files` | s3://gex-datalake-bronze-prod/scripts/buygoods_api/buygoods_api_libs.zip |
| `--source_bucket` | gex-datalake-landing-prod |

## Últimas execuções

> Sem histórico de execuções (job nunca rodou ou sem acesso ao histórico).

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/buygoods_api/job_extract.py` — baixado do S3 (read-only).

````python
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import boto3

from awsglue.utils import getResolvedOptions

CURRENT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = CURRENT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.append(str(PACKAGE_ROOT))


def _add_extra_py_files_to_syspath() -> None:
    token = "--extra-py-files"
    if token not in sys.argv:
        return

    idx = sys.argv.index(token)
    if idx + 1 >= len(sys.argv):
        return

    s3_client = boto3.client("s3")
    for item in (part.strip() for part in sys.argv[idx + 1].split(",") if part.strip()):
        if item.startswith("s3://"):
            parsed = urlparse(item)
            bucket = parsed.netloc
            key = parsed.path.lstrip("/")
            local_path = f"/tmp/{Path(key).name}"
            s3_client.download_file(bucket, key, local_path)
            if local_path not in sys.path:
                sys.path.append(local_path)
            continue

        if item not in sys.path:
            sys.path.append(item)


_add_extra_py_files_to_syspath()

from src.api_client import BuyGoodsApiClient
from src.landing_writer import LandingWriter
from src.utils import get_execution_dt_proc, get_execution_run_id, get_monthly_windows, get_secret, load_config, log


REQUIRED_ARGS = [
    "JOB_NAME",
    "env",
    "source_bucket",
    "date_from",
    "date_to",
]


def main() -> None:
    args = getResolvedOptions(sys.argv, REQUIRED_ARGS)

    config = load_config(args["env"])
    run_id = get_execution_run_id()

    secret = get_secret(config.SECRET_NAME)
    accounts = secret.get("accounts")
    if not isinstance(accounts, list) or not accounts:
        raise ValueError(f"Secret {config.SECRET_NAME} missing non-empty accounts list")

    writer = LandingWriter(config=config, landing_bucket=args["source_bucket"])

    dt_proc = get_execution_dt_proc()
    windows = get_monthly_windows(args["date_from"], args["date_to"])

    processed_accounts = 0
    total_pages = 0
    total_records = 0

    log(
        "INFO",
        "extract_start",
        "BuyGoods extraction started",
        run_id=run_id,
        env=config.ENV,
        accounts=len(accounts),
        windows=len(windows),
        landing_bucket=args["source_bucket"],
        dt_proc=dt_proc,
    )

    for account in accounts:
        account_id = str(account.get("account_id", "")).strip()
        account_name = str(account.get("account_name", "")).strip()
        token = account.get("token")

        if not account_id or not account_name or not isinstance(token, str) or not token.strip():
            log(
                "WARN",
                "account_skip",
                "Skipping account with invalid credentials payload",
                run_id=run_id,
                account_id=account_id or "unknown",
                account_name=account_name or "unknown",
            )
            continue

        client = BuyGoodsApiClient(
            token=token,
            account_id=account_id,
            account_name=account_name,
            config=config,
        )

        log(
            "INFO",
            "account_start",
            "Processing account",
            run_id=run_id,
            account_id=account_id,
            account_name=account_name,
        )

        account_pages = 0
        account_records = 0

        for window_from, window_to in windows:
            log(
                "INFO",
                "window_start",
                "Processing date window",
                run_id=run_id,
                account_id=account_id,
                account_name=account_name,
                date_from=window_from,
                date_to=window_to,
            )

            page = 1
            while page <= config.MAX_PAGES_PER_WINDOW:
                if writer.page_exists(account_id, dt_proc, window_from, window_to, page):
                    log(
                        "INFO",
                        "page_skip",
                        "Landing page already exists",
                        run_id=run_id,
                        account_id=account_id,
                        page=page,
                        date_from=window_from,
                        date_to=window_to,
                    )
                    page += 1
                    continue

                response, metadata = client.fetch_page(window_from, window_to, page, run_id=run_id)
                records = client.get_records(response)

                if not records:
                    log(
                        "INFO",
                        "page_skip",
                        "Empty records, stopping window",
                        run_id=run_id,
                        account_id=account_id,
                        page=page,
                        date_from=window_from,
                        date_to=window_to,
                    )
                    break

                writer.write_page(
                    account_id=account_id,
                    account_name=account_name,
                    records=records,
                    dt_proc=dt_proc,
                    page=page,
                    date_from=window_from,
                    date_to=window_to,
                    run_id=run_id,
                    metadata=metadata,
                )

                account_pages += 1
                account_records += len(records)
                total_pages += 1
                total_records += len(records)

                has_next = client.has_next_page(response, records)
                time.sleep(config.RATE_LIMIT_SEC)
                if not has_next:
                    break

                page += 1

            if page > config.MAX_PAGES_PER_WINDOW:
                log(
                    "WARN",
                    "guardrail",
                    "Max pages reached, skipping window",
                    run_id=run_id,
                    account_id=account_id,
                    max_pages=config.MAX_PAGES_PER_WINDOW,
                    date_from=window_from,
                    date_to=window_to,
                )

        processed_accounts += 1
        log(
            "INFO",
            "account_done",
            "Finished account",
            run_id=run_id,
            account_id=account_id,
            account_name=account_name,
            pages=account_pages,
            records=account_records,
        )

    log(
        "INFO",
        "extract_done",
        "BuyGoods extraction finished",
        run_id=run_id,
        accounts=processed_accounts,
        windows=len(windows),
        pages=total_pages,
        records=total_records,
    )


if __name__ == "__main__":
    main()
````

## Relacionados
[[00-Data-Lake]]
