from typing import List
from uuid import UUID

from crm_pilates.event.event_store import EventStore, Event


class MemoryEventStore(EventStore):

    def get_by_id(self, id: UUID) -> List[Event]:
        pass

    def __init__(self):
        self.events = []

    def persist(self, event: Event):
        self.events.append(event)

    def get_all(self):
        return self.events
