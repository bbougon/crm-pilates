import json
import sys
import uuid
from datetime import datetime
from functools import partial

import psycopg
from psycopg.types.json import Jsonb

from crm_pilates.infrastructure.event.sqlite.sqlite_event_store import (
    MultipleJsonEncoders,
    UUIDEncoder,
    EnumEncoder,
    DateTimeEncoder,
)
from crm_pilates.infrastructure.migration.migration_script import MigrationScript


class FirstMigrationScriptForTest(MigrationScript):
    def __init__(self, argument) -> None:
        super().__init__(self.__class__.__name__, argument)

    def run_script(self):
        uuid_dumps = partial(
            json.dumps,
            cls=MultipleJsonEncoders(UUIDEncoder, EnumEncoder, DateTimeEncoder),
        )
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(
                "INSERT INTO event VALUES (%(id)s, %(root_id)s, %(type)s, %(timestamp_)s, %(payload)s)",
                {
                    "id": uuid.uuid4(),
                    "root_id": uuid.uuid4(),
                    "type": "type_1",
                    "timestamp_": datetime.now().isoformat(),
                    "payload": Jsonb({"event": 1}, dumps=uuid_dumps),
                },
            )
            connection.commit()


if __name__ == "__main__":
    FirstMigrationScriptForTest(sys.argv[1:]).execute()
