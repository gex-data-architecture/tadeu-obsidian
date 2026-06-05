---
tipo: job-glue
ambiente: prod
fluxo: 
tipo_job: glueetl
glue_version: 4.0
ultima_execucao: —
ultimo_estado: —
tags: [datalake, glue-job]
---

# gex-buygoods-api-convert-prod

> Glue ETL · fluxo **—** · ambiente **prod**

## Propriedades

| Propriedade | Valor |
|---|---|
| Tipo | glueetl |
| Glue version | 4.0 |
| Worker | G.1X x2 |
| Timeout (min) | 2880 |
| Max retries | 0 |
| Role | `arn:aws:iam::406933028738:role/gex-glue-role-prod` |
| Script | `s3://gex-datalake-bronze-prod/scripts/buygoods_api/job_convert.py` |
| Criado | 2026-05-28 10:39:21.942000-03:00 |
| Modificado | 2026-05-28 10:39:21.942000-03:00 |

## Parâmetros de negócio

| Argumento | Valor |
|---|---|
| `--env` | prod |
| `--extra-py-files` | s3://gex-datalake-bronze-prod/scripts/buygoods_api/buygoods_api_libs.zip |
| `--source_bucket` | gex-datalake-landing-prod |
| `--target_bucket` | gex-datalake-bronze-prod |

## Últimas execuções

> Sem histórico de execuções (job nunca rodou ou sem acesso ao histórico).

## Script

> Fonte: `s3://gex-datalake-bronze-prod/scripts/buygoods_api/job_convert.py` — baixado do S3 (read-only).

````python
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import boto3

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

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

from src.bronze_converter import BronzeConverter
from src.utils import get_execution_run_id, load_config, log


def get_optional_arg(name: str) -> Optional[str]:
    token = f"--{name}"
    if token not in sys.argv:
        return None
    idx = sys.argv.index(token)
    if idx + 1 >= len(sys.argv):
        return None
    return sys.argv[idx + 1]


def main() -> None:
    required = ["JOB_NAME", "env", "source_bucket", "target_bucket"]
    args = getResolvedOptions(sys.argv, required)

    run_id = get_execution_run_id()
    config = load_config(args["env"])
    dt_proc = get_optional_arg("dt_proc")

    sc = SparkContext.getOrCreate()
    glue_context = GlueContext(sc)
    spark = glue_context.spark_session

    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    converter = BronzeConverter(
        spark=spark,
        config=config,
        landing_bucket=args["source_bucket"],
        bronze_bucket=args["target_bucket"],
    )

    log(
        "INFO",
        "convert_start",
        "BuyGoods convert started",
        run_id=run_id,
        env=config.ENV,
        dt_proc=dt_proc or "all",
        source_bucket=args["source_bucket"],
        target_bucket=args["target_bucket"],
    )

    df = converter.read_landing(run_id=run_id, dt_proc=dt_proc)

    # Fase exploratoria: sem deduplicacao ate validar contrato real da API.
    df = converter.add_dt_proc(df)
    converter.write_bronze(df, run_id=run_id)

    job.commit()
    log("INFO", "convert_done", "BuyGoods convert finished", run_id=run_id)


if __name__ == "__main__":
    main()
````

## Relacionados
[[00-Data-Lake]]
