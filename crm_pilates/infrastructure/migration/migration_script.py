from __future__ import annotations

import getopt
import logging
import time
from abc import abstractmethod
from decimal import getcontext, Decimal

logger = logging.getLogger("migration")


class MigrationScript:
    def __init__(self, name: str, argv) -> None:
        _, connection_url = getopt.getopt(argv, "", ["connection-url="])[0][0]
        self.connection_url = connection_url
        self.name = name

    def execute(self):
        start_time = time.time()
        self.run_script()
        getcontext().prec = 4
        logger.info(
            f"Migration script `{self.name}` run in {Decimal(time.time()) - Decimal(start_time)} seconds"
        )

    @abstractmethod
    def run_script(self):
        pass
