#!/usr/bin/env python3

import argparse
import logging
import sys

from cdis_pipe_utils import pipe_util

import fastqc_db

def main():
    parser = argparse.ArgumentParser('FastQC tool')

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
    parser.add_argument('-d', '--fastqc_data_path',
                        required=True
    )
    parser.add_argument('-s', '--fastqc_summary_path',
                        Required=True
    )

    # setup required parameters
    args = parser.parse_args()
    uuid = args.uuid
    fastqc_data_path = args.fastqc_data_path
    fastqc_summary_path = args.fastqc_summary_path
    
    logger = pipe_util.setup_logging(tool_name, args, uuid)
    engine = pipe_util.setup_db(uuid)

    fastqc_db.fastqc_db_data(uuid, fastqc_data_path, engine, logger)
    fastqc_db.fastqc_db_summary(uuid, fastqc_summary_path, engine, logger)
    return


if __name__ == '__main__':
    main()
