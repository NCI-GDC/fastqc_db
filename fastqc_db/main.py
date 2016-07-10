#!/usr/bin/env python3

import argparse
import logging
import os
import sys

import sqlalchemy

from cdis_pipe_utils import pipe_util

import fastqc_db

def main():
    parser = argparse.ArgumentParser('FastQC to sqlite')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    # Required flags.
    parser.add_argument('--uuid',
                        required = True,
                        help = 'uuid string',
    )
    parser.add_argument('--fastqc_zip_path',
                        required=True
    )

    # setup required parameters
    args = parser.parse_args()
    uuid = args.uuid
    fastqc_zip_path = args.fastqc_zip_path

    fastqc_zip_name = os.path.basename(fastqc_zip_path)
    fastqc_zip_base, zip_ext = os.path.splitext(fastqc_zip_name)
    
    tool_name = 'fastqc_db'
    logger = pipe_util.setup_logging(tool_name, args, uuid)

    sqlite_name = fastqc_zip_base + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    fastqc_db.fastqc_db(uuid, fastqc_zip_path, engine, logger)
    return


if __name__ == '__main__':
    main()
