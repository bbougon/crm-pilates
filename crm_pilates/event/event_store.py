from __future__ import annotations
import uuid
from abc import abstractmethod
from datetime import datetime
from typing import List
from uuid import UUID

import pytz

from crm_pilates.infrastructure.event_bus_provider import EventBusProvider

EVENT_VERSION = "2.1"


class Event:
    def __init__(self, root_id: UUID) -> None:
        super().__init__()
        self.id: UUID = uuid.uuid4()
        self.root_id: UUID = root_id
        self.type: str = self.__class__.__name__
        self.timestamp: datetime = datetime.now(tz=pytz.utc)
        self.payload: dict = self._to_payload()
        if self.payload:
            self.payload["version"] = EVENT_VERSION

    @abstractmethod
    def _to_payload(self) -> dict:
        ...


class EventStore:
    @abstractmethod
    def persist(self, event: Event):
        ...

    @abstractmethod
    def get_all(self) -> List[Event]:
        ...

    @abstractmethod
    def get_by_id(self, id: UUID) -> List[Event]:
        ...


class StoreLocator:
    store: EventStore = None


class EventSourced:
    def __init__(self, event) -> None:
        self.event = event

    def __call__(self, *args, **kwargs) -> Event:
        event: Event = self.event(*args, **kwargs)
        StoreLocator.store.persist(event)
        EventBusProvider.publish(event)
        return event
