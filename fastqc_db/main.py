#!/usr/bin/env python3

import argparse
import logging
import os

import sqlalchemy

from fastqc_db import fastqc_db


def setup_logging(job_uuid: str, level: int) -> logging.Logger:
    logging.basicConfig(
        filename=f"{job_uuid}.log",
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    return logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser("FastQC to sqlite")

    parser.add_argument("--job_uuid", required=True)
    parser.add_argument("--INPUT", required=True)
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )

    args = parser.parse_args()

    logger = setup_logging(args.job_uuid, logging.DEBUG if args.debug else logging.INFO)

    fastqc_zip_name = os.path.basename(args.INPUT)
    fastqc_zip_base, _ = os.path.splitext(fastqc_zip_name)

    engine = sqlalchemy.create_engine(
        f"sqlite:///{fastqc_zip_base}.db",
        isolation_level="SERIALIZABLE",
    )

    fastqc_db(args.job_uuid, args.INPUT, engine, logger)
    return 0


if __name__ == "__main__":
    main()
