import logging
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List, TextIO

import pandas as pd
import sqlalchemy


def clean_headers(headers: List[str]) -> List[str]:
    return [str(h).strip().replace(" ", "_") for h in headers]


def get_total_deduplicated_percentage(
    fastqc_data_open: TextIO, logger: logging.Logger
) -> List[str]:
    for line in fastqc_data_open:
        if line.startswith("#Total Deduplicated Percentage"):
            return line.strip("\n").lstrip("#").split("\t")
    logger.error("Total Deduplicated Percentage not found")
    sys.exit(1)


def fastqc_detail_to_df(
    job_uuid: str,
    fastq_name: str,
    fastqc_data_path: str,
    data_key: str,
    engine: sqlalchemy.engine.Engine,
    logger: logging.Logger,
) -> pd.DataFrame:
    rows = []
    headers = None
    in_module = False

    with open(fastqc_data_path) as f:
        for line in f:
            line = line.rstrip("\n")

            if line.startswith(data_key):
                in_module = True
                continue

            if in_module and line.startswith(">>END_MODULE"):
                break

            if in_module and line.startswith("#"):
                headers = clean_headers(line.lstrip("#").split("\t"))
                continue

            if in_module and headers:
                rows.append([job_uuid, fastq_name] + line.split("\t"))

    if not rows or not headers:
        logger.info("No data for module %s", data_key)
        return pd.DataFrame()

    return pd.DataFrame(
        rows,
        columns=["job_uuid", "fastq"] + headers,
    )


def fastqc_summary_to_dict(
    data_dict: Dict[str, Any],
    fastqc_summary_path: str,
    engine: sqlalchemy.engine.Engine,
    logger: logging.Logger,
) -> Dict[str, Any]:
    with open(fastqc_summary_path) as f:
        for line in f:
            status, module, *_ = line.strip().split("\t")
            data_dict[module] = status

    if "Per tile sequence quality" not in data_dict:
        data_dict["Per tile sequence quality"] = None

    return data_dict


def get_fastq_name(fastqc_data_path: str, logger: logging.Logger) -> str:
    with open(fastqc_data_path) as f:
        for line in f:
            if line.startswith("Filename\t"):
                return line.split("\t")[1].strip()

    logger.error("Filename not found in fastqc_data.txt")
    sys.exit(1)


def fastqc_db(
    job_uuid: str,
    fastqc_zip_path: str,
    engine: sqlalchemy.engine.Engine,
    logger: logging.Logger,
) -> None:
    fastqc_zip_name = os.path.basename(fastqc_zip_path)
    step_dir = os.getcwd()
    fastqc_zip_base, _ = os.path.splitext(fastqc_zip_name)

    logger.info("Processing FastQC zip: %s", fastqc_zip_path)

    subprocess.check_output(["unzip", "-q", fastqc_zip_path, "-d", step_dir])

    fastqc_data_path = os.path.join(step_dir, fastqc_zip_base, "fastqc_data.txt")
    fastqc_summary_path = os.path.join(step_dir, fastqc_zip_base, "summary.txt")

    fastq_name = get_fastq_name(fastqc_data_path, logger)

    summary_dict = {
        "job_uuid": job_uuid,
        "fastq": fastq_name,
    }

    summary_dict = fastqc_summary_to_dict(
        summary_dict, fastqc_summary_path, engine, logger
    )

    pd.DataFrame([summary_dict]).to_sql(
        "fastqc_summary",
        engine,
        if_exists="append",
        index=False,
    )

    data_key_list = [
        ">>Basic Statistics",
        ">>Per base sequence quality",
        ">>Per tile sequence quality",
        ">>Per sequence quality scores",
        ">>Per base sequence content",
        ">>Per sequence GC content",
        ">>Per base N content",
        ">>Sequence Length Distribution",
        ">>Sequence Duplication Levels",
        ">>Overrepresented sequences",
        ">>Adapter Content",
        ">>Kmer Content",
    ]

    for data_key in data_key_list:
        df = fastqc_detail_to_df(
            job_uuid, fastq_name, fastqc_data_path, data_key, engine, logger
        )

        if df.empty:
            continue

        table_name = "fastqc_data_" + "_".join(
            data_key.lstrip(">>").strip().lower().split()
        )

        df.to_sql(
            table_name,
            engine,
            if_exists="append",
            index=False,
        )

    shutil.rmtree(os.path.join(step_dir, fastqc_zip_base))
    logger.info("Completed FastQC DB load for %s", fastq_name)
