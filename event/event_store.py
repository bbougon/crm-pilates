import uuid
from abc import abstractmethod
from datetime import datetime
from typing import List
from uuid import UUID


class Event:

    def __init__(self, root_id: UUID) -> None:
        super().__init__()
        self.id: UUID = uuid.uuid4()
        self.root_id: UUID = root_id
        self.type: str = self.__class__.__name__
        self.timestamp: datetime = datetime.now()
        self.payload = None

    @abstractmethod
    def _to_payload(self):
        ...


class EventStore:

    @abstractmethod
    def persist(self, event: Event):
        ...

    @abstractmethod
    def get_all(self) -> List[Event]:
        ...


class StoreLocator:
    store: EventStore = None


class EventSourced:

    def __init__(self, event) -> None:
        self.event = event

    def __call__(self, *args, **kwargs) -> Event:
        event = self.event(*args, **kwargs)
        StoreLocator.store.persist(event)
        return event
