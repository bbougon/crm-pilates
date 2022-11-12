import logging
import os
from uuid import UUID

import psycopg

from crm_pilates import settings
from crm_pilates.infrastructure.event.sqlite.sqlite_event_store import (
    MultipleJsonEncoders,
    UUIDEncoder,
    EnumEncoder,
    DateTimeEncoder,
)

logger = logging.getLogger("migration")


class Migration:
    def __init__(self, connection_url: str) -> None:
        super().__init__()
        self.connection_url = connection_url
        self.encoders = MultipleJsonEncoders(UUIDEncoder, EnumEncoder, DateTimeEncoder)

    def migrate(self):
        yield from self.run_scripts()

    def run_scripts(self):
        migration_scripts = []
        for (dirpath, _, files) in os.walk(settings.MIGRATION_SCRIPTS):
            migration_scripts.extend(
                [
                    os.path.join(dirpath, file)
                    for file in files
                    if file.split("/")[-1].startswith("script_0")
                    and file.split("/")[-1].endswith(".py")
                ]
            )
        migration_scripts.sort()
        for script in migration_scripts:
            logger.info(f"Run script {script}")
            yield os.system(f"python {script} --connection-url={self.connection_url}")

    def get_event(self, id: UUID):
        with psycopg.connect(self.connection_url) as connection:
            row = connection.execute(
                "SELECT * FROM event WHERE id = %(event_id)s", {"event_id": str(id)}
            ).fetchone()
            return row
