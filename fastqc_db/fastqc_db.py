import logging
import os
import shutil
import subprocess
import sys
from typing import Any, Optional, TextIO

import pandas as pd
import sqlalchemy


# def get_total_deduplicated_percentage(fastqc_data_open, logger):
def get_total_deduplicated_percentage(
    fastqc_data_open: TextIO, logger: logging.Logger
) -> list[str]:
    for line in fastqc_data_open:
        if line.startswith("#Total Deduplicated Percentage"):
            line_split = list()
            line_split = line.strip("\n").lstrip("#").split("\t")
            return line_split
    logger.debug("get_total_deduplicated_percentage() failed")
    sys.exit(1)


# def fastqc_detail_to_df(
#    job_uuid, fastq_name, fastqc_data_path, data_key, engine, logger
# ):
def fastqc_detail_to_df(
    job_uuid: str,
    fastq_name: str,
    fastqc_data_path: str,
    data_key: str,
    engine: sqlalchemy.engine.Engine,
    logger: logging.Logger,
) -> pd.DataFrame:
    logger.info("detail step: %s" % data_key)
    logger.info("fastqc_data_path: %s" % fastqc_data_path)
    process_data = False
    process_header = False
    have_data = False
    df = pd.DataFrame()
    with open(fastqc_data_path, "r") as fastqc_data_open:
        for line in fastqc_data_open:
            # logger.info('line=%s' % line)
            if line.startswith("##FastQC"):
                # logger.info('\tcase 1')
                continue
            elif process_data and line.startswith("#"):
                # logger.info('\tcase 5')
                process_header = True
                header_list = line.strip("#").strip().split("\t")
                logger.info("fastqc_detail_to_df() header_list: %s" % header_list)
            elif (
                process_data and not process_header and line.startswith(">>END_MODULE")
            ):
                # logger.info('\tcase 2')
                break
            elif line.startswith(data_key):
                # logger.info('\tcase 3')
                logger.info("fastqc_detail_to_df() found data_key: %s" % data_key)
                process_data = True
            elif process_data and line.startswith(">>END_MODULE"):
                # logger.info('\tcase 4')
                logger.info("fastqc_detail_to_df() >>END_MODULE")
                if data_key == ">>Basic Statistics":
                    value_list = get_total_deduplicated_percentage(
                        fastqc_data_open, logger
                    )
                    row_df = pd.DataFrame(
                        [[job_uuid, fastq_name] + value_list],
                        columns=["job_uuid", "fastq"] + header_list,
                    )
                    # row_df = pd.DataFrame([job_uuid, fastq_name] + value_list)
                    # row_df_t = row_df.T
                    # row_df_t.columns = ["job_uuid", "fastq"]
                    # logger.info('9 row_df_t=%s' % row_df_t)
                    if df is not None:
                        df = pd.concat([df, row_df], ignore_index=True)
                break
            elif process_data and process_header:
                # logger.info('\tcase 6')
                logger.info("fastqc_detail_to_df() columns=%s" % header_list)
                df = pd.DataFrame(columns=["job_uuid", "fastq"] + header_list)
                process_header = False
                have_data = True
                # logger.info('2 df=%s' % df)
                line_split = line.strip("\n").split("\t")
                logger.info("process_header line_split=%s" % line_split)
                row_df = pd.DataFrame(
                    [[job_uuid, fastq_name] + line_split],
                    columns=[["job_uuid", "fastq"] + header_list],
                )
                # row_df
                # row_df = pd.DataFrame([job_uuid, fastq_name] + line_split)
                # row_df_t = row_df.T
                # row_df_t.columns = ["job_uuid", "fastq"] + header_list # type: ignore
                logger.info("1 row_df_t=%s" % row_df)
                df = pd.concat([df, row_df], ignore_index=True)
                # logger.info('3 df=%s' % df)
            elif process_data and not process_header:
                # logger.info('\tcase 7')
                line_split = line.strip("\n").split("\t")
                logger.info("not process_header line_split=%s" % line_split)
                row_df = pd.DataFrame(
                    [[job_uuid, fastq_name] + line_split],
                    columns=[["job_uuid", "fastq"] + header_list],
                )
                # row_df = pd.DataFrame([job_uuid, fastq_name] + line_split)
                # row_df_t = row_df.T
                # row_df_t.columns = ["job_uuid", "fastq"] + header_list # type: ignore
                logger.info("not process_header line_split=%s" % line_split)
                logger.info("2 row_df_t=%s" % row_df)
                df = pd.concat([df, row_df], ignore_index=True)
                # logger.info('4 df=%s' % df)
            elif not process_data and not process_header:
                # logger.info('\tcase 8')
                continue
            else:
                # logger.info('\tcase 9')
                logger.debug("fastqc_detail_to_df(): should not be here")
                sys.exit(1)
    if have_data:
        logger.info("complete df=%s" % df)
        return df
    else:
        logger.info("no df")
        return pd.DataFrame()
    logger.debug("fastqc_detail_to_df(): should not reach end of function")
    sys.exit(1)


# def fastqc_summary_to_dict(data_dict, fastqc_summary_path, engine, logger):
def fastqc_summary_to_dict(
    data_dict: dict[str, Any],
    fastqc_summary_path: str,
    engine: sqlalchemy.engine.Engine,
    logger: logging.Logger,
) -> dict[str, Any]:
    logger.info("fastqc_summary_path=%s" % fastqc_summary_path)
    with open(fastqc_summary_path, "r") as fastqc_summary_open:
        for line in fastqc_summary_open:
            line_split = line.split("\t")
            line_key = line_split[1].strip()
            line_value = line_split[0].strip()
            data_dict[line_key] = line_value
    if "Per tile sequence quality" not in data_dict:
        data_dict["Per tile sequence quality"] = None
    return data_dict


# def get_fastq_name(fastqc_data_path, logger):
def get_fastq_name(fastqc_data_path: str, logger: logging.Logger) -> str:
    with open(fastqc_data_path) as data_open:
        for line in data_open:
            if line.startswith("Filename\t"):
                line_split = line.split("\t")
                fastq_name = line_split[1].strip()
                return fastq_name
    logger.debug("unable to find fastq_name in %s" % fastqc_data_path)
    sys.exit(1)
    return


# def fastqc_db(job_uuid, fastqc_zip_path, engine, logger):
def fastqc_db(
    job_uuid: str,
    fastqc_zip_path: str,
    engine: sqlalchemy.engine.Engine,
    logger: logging.Logger,
) -> None:
    fastqc_zip_name = os.path.basename(fastqc_zip_path)
    step_dir = os.getcwd()
    fastqc_zip_base, fastqc_zip_ext = os.path.splitext(fastqc_zip_name)
    logger.info("writing `fastqc db`: %s" % fastqc_zip_path)

    # extract fastqc report
    cmd = ["unzip", fastqc_zip_path, "-d", step_dir]
    output = subprocess.check_output(cmd)  # noqa: F841

    fastqc_data_path = os.path.join(step_dir, fastqc_zip_base, "fastqc_data.txt")
    fastqc_summary_path = os.path.join(step_dir, fastqc_zip_base, "summary.txt")

    fastq_name = get_fastq_name(fastqc_data_path, logger)

    summary_dict = dict()
    summary_dict["job_uuid"] = [
        job_uuid
    ]  # need one non-scalar value in df to avoid index
    summary_dict["fastq"] = fastq_name  # type: ignore
    summary_dict = fastqc_summary_to_dict(
        summary_dict, fastqc_summary_path, engine, logger
    )
    df = pd.DataFrame(summary_dict)
    table_name = "fastqc_summary"
    df.to_sql(table_name, engine, if_exists="append")
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
        if df is None:
            continue
        table_name = "fastqc_data_" + "_".join(data_key.lstrip(">>").strip().split(" "))
        logger.info("fastqc_to_db() table_name=%s" % table_name)
        df.to_sql(table_name, engine, if_exists="append")

    shutil.rmtree(os.path.join(step_dir, fastqc_zip_base))
    logger.info("completed writing `fastqc db`: %s" % fastq_name)
    return
