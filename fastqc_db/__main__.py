#!/usr/bin/env python
"""
Python Project Template Entrypoint Script
"""

import datetime
import logging
import sys

import click

from .main import main

try:
    from fastqc_db import __version__
except Exception:
    __version__ = "0.0.0"

log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s:%(lineno)s %(levelname)s | %(message)s",
)

if __name__ == "__main__":
    """CLI Entrypoint"""

    status_code = 0
    try:
        status_code = sys.exit(main())
    except Exception as e:
        log.exception(e)
        sys.exit(1)
    sys.exit(status_code)


# __END__
