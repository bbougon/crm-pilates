import datetime
import uuid
from uuid import UUID

import pytz
from immobilus import immobilus

from event.event_store import Event, EventSourced, StoreLocator


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
def test_should_persist_event_in_store(postgres_event_store):
    root_id = uuid.uuid4()
    event_emitted: Event = CustomEventEmitted(root_id)

    persisted_event: Event = StoreLocator.store.get_by_id(event_emitted.id)

    assert_event(persisted_event, root_id)


@immobilus("2021-05-20 10:05:17.245")
def test_should_retrieve_all_events_in_store(postgres_event_store):
    first_event_root_id = uuid.uuid4()
    CustomEventEmitted(first_event_root_id)
    second_event_root_id = uuid.uuid4()
    CustomEventEmitted(second_event_root_id)

    persisted_events: [Event] = StoreLocator.store.get_all()

    assert len(persisted_events) == 2
    assert_event(persisted_events[0], first_event_root_id)
    assert_event(persisted_events[1], second_event_root_id)


def assert_event(event: Event, root_id: UUID):
    assert isinstance(event.id, UUID)
    assert event.root_id == root_id
    assert event.type == "CustomEventEmitted"
    assert event.timestamp == datetime.datetime(2021, 5, 20, 10, 5, 17, 245000, tzinfo=pytz.utc)
    assert event.payload == {"id": str(root_id), "name": "custom_event"}
