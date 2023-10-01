import logging
import os
from datetime import datetime
from uuid import UUID

import psycopg
from psycopg.rows import namedtuple_row

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
        scripts = [script.script_path for script in self.get_already_played_scripts()]
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
        migration_scripts = list(
            filter(lambda script: script not in scripts, migration_scripts)
        )
        migration_scripts.sort()
        yield from self.run_scripts(migration_scripts)

    def run_scripts(self, migration_scripts):
        for script in migration_scripts:
            logger.info(f"Run script {script}")
            yield os.system(f"python {script} --connection-url={self.connection_url}")
            yield self.update_migration(script, datetime.now())

    def get_event(self, id: UUID):
        with psycopg.connect(self.connection_url) as connection:
            row = connection.execute(
                "SELECT * FROM event WHERE id = %(event_id)s", {"event_id": str(id)}
            ).fetchone()
            return row

    def get_already_played_scripts(self):
        with psycopg.connect(
            self.connection_url, row_factory=namedtuple_row
        ) as connection:
            rows = connection.execute("SELECT script_path FROM migration").fetchall()
            return rows

    def update_migration(self, script: str, script_execution_date: datetime):
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(
                "INSERT INTO migration (timestamp_, script_path) VALUES (%(date_)s, %(script_path)s)",
                {"date_": script_execution_date, "script_path": script},
            )
