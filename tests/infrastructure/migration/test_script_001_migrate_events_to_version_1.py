from datetime import datetime
from uuid import uuid4

from crm_pilates.infrastructure.migration.migration import Migration
from crm_pilates.infrastructure.migration.script_001_migrate_events_to_version_1 import (
    MigrateEventsToVersion1Script,
)
from tests.infrastructure.migration.test_migration import set_event, PILATES_TEST


def test_should_update_version(clean_database, connection_url_arg):
    id = uuid4()
    root_id = uuid4()
    date = datetime.now()
    set_event(id, root_id, "Custom", date, {"event": "my event"})

    MigrateEventsToVersion1Script(connection_url_arg).execute()

    event = Migration(
        "postgresql://crm-pilates-test:example@localhost:5433/crm-pilates-test"
    ).get_event(id)
    assert event[0] == id
    assert event[1] == root_id
    assert event[2] == "Custom"
    assert event[3] == date
    assert event[4] == {"version": "1", "event": "my event"}


def test_should_not_update_version_if_already_set(clean_database, connection_url_arg):
    id = uuid4()
    root_id = uuid4()
    date = datetime.now()
    set_event(id, root_id, "Custom", date, {"event": "my event", "version": "2"})

    MigrateEventsToVersion1Script(connection_url_arg).execute()

    event = Migration(PILATES_TEST).get_event(id)
    assert event[0] == id
    assert event[1] == root_id
    assert event[2] == "Custom"
    assert event[3] == date
    assert event[4] == {"version": "2", "event": "my event"}


def test_should_update_created_classroom_with_subject(
    clean_database, connection_url_arg
):
    id = uuid4()
    second_id = uuid4()
    third_id = uuid4()
    root_id = uuid4()
    date = datetime.now()
    custom_id = uuid4()
    set_event(custom_id, root_id, "Custom", date, {"event": "my event", "version": "1"})
    set_event(
        id,
        root_id,
        "ClassroomCreated",
        date,
        {
            "id": "1",
            "name": "Machine Trio",
            "duration": {"duration": 60, "time_unit": "MINUTE"},
            "position": 3,
            "schedule": {
                "stop": "2022-01-25T15:15:01+00:00",
                "start": "2021-11-10T14:15:00+00:00",
            },
            "attendees": [],
        },
    )
    set_event(
        second_id,
        root_id,
        "ConfirmedSessionEvent",
        date,
        {
            "id": "2",
            "name": "Cours Duo",
            "position": 2,
            "schedule": {
                "stop": "2021-11-03T14:00:00+00:00",
                "start": "2021-11-03T13:00:00+00:00",
            },
            "attendees": [],
            "classroom_id": "1",
        },
    )
    set_event(
        third_id,
        root_id,
        "ClassroomCreated",
        date,
        {
            "id": "3",
            "name": "Cours Machines",
            "duration": {"duration": 60, "time_unit": "MINUTE"},
            "position": 2,
            "schedule": {
                "stop": "2022-01-25T15:15:01+00:00",
                "start": "2021-11-10T14:15:00+00:00",
            },
            "attendees": [],
        },
    )

    MigrateEventsToVersion1Script(connection_url_arg).execute()

    custom_event = Migration(PILATES_TEST).get_event(custom_id)
    event = Migration(PILATES_TEST).get_event(id)
    second_event = Migration(PILATES_TEST).get_event(second_id)
    third_event = Migration(PILATES_TEST).get_event(third_id)
    assert custom_event[4] == {"version": "1", "event": "my event"}
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
        "schedule": {
            "stop": "2022-01-25T15:15:01+00:00",
            "start": "2021-11-10T14:15:00+00:00",
        },
        "attendees": [],
    }
    assert second_event[4] == {
        "version": "1",
        "subject": "MAT",
        "id": "2",
        "name": "Cours Duo",
        "position": 2,
        "schedule": {
            "stop": "2021-11-03T14:00:00+00:00",
            "start": "2021-11-03T13:00:00+00:00",
        },
        "attendees": [],
        "classroom_id": "1",
    }
    assert third_event[4] == {
        "version": "1",
        "subject": "MACHINE_DUO",
        "id": "3",
        "name": "Cours Machines",
        "duration": {"duration": 60, "time_unit": "MINUTE"},
        "position": 2,
        "schedule": {
            "stop": "2022-01-25T15:15:01+00:00",
            "start": "2021-11-10T14:15:00+00:00",
        },
        "attendees": [],
    }
