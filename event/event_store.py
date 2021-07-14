import uuid
from abc import abstractmethod
from datetime import datetime
from uuid import UUID


class Event:

    def __init__(self, root_id: UUID) -> None:
        super().__init__()
        self.id: UUID = uuid.uuid4()
        self.root_id: UUID = root_id
        self.type: str = self.__class__.__name__
        self.timestamp: datetime = datetime.now()

    @property
    def payload(self):
        return self._to_payload()

    @abstractmethod
    def _to_payload(self):
        ...


class EventStore:

    @abstractmethod
    def persist(self, event: Event):
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