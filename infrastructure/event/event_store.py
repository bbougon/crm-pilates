from abc import abstractmethod
from datetime import datetime


class Event:

    def __init__(self) -> None:
        super().__init__()
        self.type = self.__class__.__name__
        self.timestamp = datetime.now()

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
    store = None


class EventSourced:

    def __init__(self, event) -> None:
        self.event = event

    def __call__(self, *args, **kwargs) -> Event:
        event = self.event(*args, **kwargs)
        StoreLocator.store.persist(event)
        return event
