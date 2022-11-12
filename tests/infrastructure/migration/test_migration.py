import json
from datetime import datetime
from functools import partial
from uuid import UUID

import psycopg
from psycopg.types.json import Jsonb

from crm_pilates import settings
from crm_pilates.infrastructure.event.sqlite.sqlite_event_store import (
    MultipleJsonEncoders,
    UUIDEncoder,
    EnumEncoder,
    DateTimeEncoder,
)
from crm_pilates.infrastructure.migration.migration import Migration

PILATES_TEST = settings.DATABASE_URL


def set_event(id: UUID, root_id: UUID, event_type: str, date: datetime, event: dict):
    uuid_dumps = partial(
        json.dumps, cls=MultipleJsonEncoders(UUIDEncoder, EnumEncoder, DateTimeEncoder)
    )
    with psycopg.connect(PILATES_TEST) as connection:
        connection.execute(
            "INSERT INTO event VALUES (%(id)s, %(root_id)s, %(type)s, %(timestamp_)s, %(payload)s)",
            {
                "id": id,
                "root_id": root_id,
                "type": event_type,
                "timestamp_": date.isoformat(),
                "payload": Jsonb(event, dumps=uuid_dumps),
            },
        )


def test_should_execute_all_files_in_path(clean_database, mocker):
    mocker.patch(
        "os.walk",
        return_value=[
            (
                "tests/infrastructure/migration/files/",
                iter([]),
                iter(
                    [
                        "script_002_test.py",
                        "script_001_test.py",
                    ]
                ),
            )
        ],
    )

    [migration for migration in Migration(PILATES_TEST).migrate()]

    with psycopg.connect(PILATES_TEST) as connection:
        rows = connection.execute("SELECT * FROM event").fetchall()

        assert len(rows) == 2
        assert rows[0][2] == "type_1"
        assert rows[1][2] == "type_2"
