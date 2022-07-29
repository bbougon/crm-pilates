import json
from datetime import datetime
from functools import partial
from uuid import UUID, uuid4

import psycopg
from psycopg.types.json import Jsonb

from crm_pilates import settings
from crm_pilates.infrastructure.event.sqlite.sqlite_event_store import MultipleJsonEncoders, UUIDEncoder, EnumEncoder, \
    DateTimeEncoder
from crm_pilates.infrastructure.migration.migration import Migration

PILATES_TEST = settings.DATABASE_URL


def set_event(id: UUID, root_id: UUID, event_type: str, date: datetime, event: dict):
    uuid_dumps = partial(json.dumps, cls=MultipleJsonEncoders(UUIDEncoder, EnumEncoder, DateTimeEncoder))
    with psycopg.connect(PILATES_TEST) as connection:
        connection.execute("INSERT INTO event VALUES (%(id)s, %(root_id)s, %(type)s, %(timestamp_)s, %(payload)s)", {
            "id": id,
            "root_id": root_id,
            "type": event_type,
            "timestamp_": date.isoformat(),
            "payload": Jsonb(event, dumps=uuid_dumps)
        })


def test_should_update_version(clean_database):
    id = uuid4()
    root_id = uuid4()
    date = datetime.now()
    set_event(id, root_id, "Custom", date, {"event": "my event"})

    Migration(PILATES_TEST).migrate()

    event = Migration("postgresql://crm-pilates-test:example@localhost:5433/crm-pilates-test").get_event(id)
    assert event[0] == id
    assert event[1] == root_id
    assert event[2] == "Custom"
    assert event[3] == date
    assert event[4] == {
        "version": "1",
        "event": "my event"
    }


def test_should_not_update_version_if_already_set(clean_database):
    id = uuid4()
    root_id = uuid4()
    date = datetime.now()
    set_event(id, root_id, "Custom", date, {"event": "my event", "version": "2"})

    Migration(PILATES_TEST).migrate()

    event = Migration(PILATES_TEST).get_event(id)
    assert event[0] == id
    assert event[1] == root_id
    assert event[2] == "Custom"
    assert event[3] == date
    assert event[4] == {
        "version": "2",
        "event": "my event"
    }


def test_should_update_created_classroom_with_subject(clean_database):
    id = uuid4()
    second_id = uuid4()
    third_id = uuid4()
    root_id = uuid4()
    date = datetime.now()
    custom_id = uuid4()
    set_event(custom_id, root_id, "Custom", date, {"event": "my event", "version": "1"})
    set_event(id, root_id, "ClassroomCreated", date, {
        "id": "1",
        "name": "Machine Trio",
        "duration": {"duration": 60, "time_unit": "MINUTE"},
        "position": 3,
        "schedule": {"stop": "2022-01-25T15:15:01+00:00", "start": "2021-11-10T14:15:00+00:00"},
        "attendees": []
    })
    set_event(second_id, root_id, "ConfirmedSessionEvent", date, {
        "id": "2",
        "name": "Cours Duo",
        "position": 2,
        "schedule": {"stop": "2021-11-03T14:00:00+00:00", "start": "2021-11-03T13:00:00+00:00"},
        "attendees": [],
        "classroom_id": "1"
    })
    set_event(third_id, root_id, "ClassroomCreated", date, {
        "id": "3",
        "name": "Cours Machines",
        "duration": {"duration": 60, "time_unit": "MINUTE"},
        "position": 2,
        "schedule": {"stop": "2022-01-25T15:15:01+00:00", "start": "2021-11-10T14:15:00+00:00"},
        "attendees": []
    })

    Migration(PILATES_TEST).migrate()

    custom_event = Migration(PILATES_TEST).get_event(custom_id)
    event = Migration(PILATES_TEST).get_event(id)
    second_event = Migration(PILATES_TEST).get_event(second_id)
    third_event = Migration(PILATES_TEST).get_event(third_id)
    assert custom_event[4] == {
        "version": "1",
        "event": "my event"
    }
    assert event[0] == id
    assert event[1] == root_id
    assert event[2] == "ClassroomCreated"
    assert event[3] == date
    assert event[4] == {
        "version": "1",
        "subject": "MACHINE_TRIO",
        "id": "1",
        "name": "Machine Trio",
        "duration": {"duration": 60, "time_unit": "MINUTE"},
        "position": 3,
        "schedule": {"stop": "2022-01-25T15:15:01+00:00", "start": "2021-11-10T14:15:00+00:00"},
        "attendees": []
    }
    assert second_event[4] == {
        "version": "1",
        "subject": "MAT",
        "id": "2",
        "name": "Cours Duo",
        "position": 2,
        "schedule": {"stop": "2021-11-03T14:00:00+00:00", "start": "2021-11-03T13:00:00+00:00"},
        "attendees": [],
        "classroom_id": "1"
    }
    assert third_event[4] == {
        "version": "1",
        "subject": "MACHINE_DUO",
        "id": "3",
        "name": "Cours Machines",
        "duration": {"duration": 60, "time_unit": "MINUTE"},
        "position": 2,
        "schedule": {"stop": "2022-01-25T15:15:01+00:00", "start": "2021-11-10T14:15:00+00:00"},
        "attendees": []
    }


def test_should_create_table_user(drop_tables):
    Migration(PILATES_TEST).migrate()

    with psycopg.connect(PILATES_TEST) as connection:
        result = connection.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'public' AND table_type LIKE 'BASE TABLE' AND TABLE_NAME = 'users';")
        assert result is not None
