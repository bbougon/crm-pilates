from datetime import datetime
from uuid import uuid4

from crm_pilates.infrastructure.migration.migration import Migration
from crm_pilates.infrastructure.migration.script_003_migrate_classroom_to_scheduled import (
    MigrateClassroomToScheduledScript,
)
from tests.infrastructure.migration.test_migration import PILATES_TEST, set_event


def test_should_update_classroom_created_event_type_to_classroom_scheduled(
    clean_database,
):
    id = uuid4()
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

    MigrateClassroomToScheduledScript(PILATES_TEST).execute()

    custom_event = Migration(PILATES_TEST).get_event(custom_id)
    event = Migration(PILATES_TEST).get_event(id)
    assert custom_event[4] == {"version": "2", "event": "my event"}
    assert event[0] == id
    assert event[1] == root_id
    assert event[2] == "ClassroomScheduled"
    assert event[4]["version"] == "2"
