#!/usr/bin/env python

import argparse
import logging
import os
import sys

import sqlalchemy

from fastqc_db.fastqc_db import fastqc_db


def setup_logging(args: argparse.Namespace, job_uuid: str) -> logging.Logger:
    log_path = f"{job_uuid}.log"

    logging.basicConfig(
        filename=log_path,
        level=args.level,
        filemode="w",
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d_%H:%M:%S",
    )

    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    return logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser("FastQC to sqlite")

    # Logging flags
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="level",
        help="Enable debug logging",
    )
    parser.set_defaults(level=logging.INFO)

    # Required flags
    parser.add_argument("--job_uuid", required=True)
    parser.add_argument("--INPUT", required=True)

    args = parser.parse_args()

    job_uuid = args.job_uuid
    fastqc_zip_path = args.INPUT

    logger = setup_logging(args, job_uuid)
    logger.info("Starting FastQC DB load")

    try:
        fastqc_zip_name = os.path.basename(fastqc_zip_path)
        fastqc_zip_base, _ = os.path.splitext(fastqc_zip_name)

        sqlite_name = f"{fastqc_zip_base}.db"
        engine_path = f"sqlite:///{sqlite_name}"

        engine = sqlalchemy.create_engine(engine_path, isolation_level="SERIALIZABLE")

        fastqc_db(job_uuid, fastqc_zip_path, engine, logger)

        logger.info("Completed FastQC DB load for %s", fastqc_zip_name)

    except Exception:
        logger.exception("FastQC DB load failed")
        raise

    finally:
        # Guarantee LOG exists
        if not os.path.exists(f"{job_uuid}.log"):
            with open(f"{job_uuid}.log", "w") as fh:
                fh.write("Log file created but no messages were logged.\n")

        # Guarantee OUTPUT DB exists
        if not os.path.exists(sqlite_name):
            open(sqlite_name, "a").close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
