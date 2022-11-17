from datetime import datetime
from uuid import uuid4

from crm_pilates.infrastructure.migration.migration import Migration
from crm_pilates.infrastructure.migration.script_004_migrate_encrypt_sensitive_data import (
    MigrateEncryptSensitiveData,
)
from tests.infrastructure.migration.test_migration import PILATES_TEST, set_event


def test_should_encrypt_sensitive_data(clean_database, connection_url_arg):
    id = uuid4()
    root_id = uuid4()
    date = datetime.now()
    custom_id = uuid4()
    set_event(custom_id, root_id, "Custom", date, {"event": "my event", "version": "2"})
    set_event(
        id,
        root_id,
        "ClientCreated",
        date,
        {
            "id": "1",
            "firstname": "bertrand",
            "lastname": "martin",
            "credits": [
                {
                    "value": 10,
                    "subject": "MAT",
                }
            ],
        },
    )

    MigrateEncryptSensitiveData(connection_url_arg).execute()

    custom_event = Migration(PILATES_TEST).get_event(custom_id)
    event = Migration(PILATES_TEST).get_event(id)
    assert custom_event[4] == {"version": "2.1", "event": "my event"}
    assert event[0] == id
    assert event[1] == root_id
    assert event[2] == "ClientCreated"
    assert event[4] == {
        "id": "1",
        "version": "2.1",
        "firstname": "encrypted_bertrand",
        "lastname": "encrypted_martin",
        "credits": [
            {
                "value": 10,
                "subject": "MAT",
            }
        ],
    }
