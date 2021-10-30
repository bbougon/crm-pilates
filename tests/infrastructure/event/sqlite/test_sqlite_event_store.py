import datetime
import uuid
from uuid import UUID

import pytz
from immobilus import immobilus

from event.event_store import Event, EventSourced
from infrastructure.event.sqlite.sqlite_event_store import SQLiteEventStore


@EventSourced
class CustomEventEmitted(Event):

    def __init__(self, root_id: UUID) -> None:
        self.name = "custom_event"
        super().__init__(root_id)

    def _to_payload(self):
        return {
            "id": self.root_id,
            "name": self.name
        }


@immobilus("2021-05-20 10:05:17.245")
def test_persist_event_in_store(database):
    root_id = uuid.uuid4()
    event_emitted: Event = CustomEventEmitted(root_id)
    SQLiteEventStore(database).persist(event_emitted)

    persisted_event: Event = SQLiteEventStore(database.realpath()).get_by_id(event_emitted.id)

    assert persisted_event
    assert isinstance(persisted_event.id, UUID)
    assert persisted_event.root_id == root_id
    assert persisted_event.type == "CustomEventEmitted"
    assert persisted_event.timestamp == datetime.datetime(2021, 5, 20, 10, 5, 17, 245000, tzinfo=pytz.utc)
    assert persisted_event.payload == {"id": root_id.hex, "name": "custom_event"}
