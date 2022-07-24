from __future__ import annotations
from abc import abstractmethod
from typing import List


class EventBus:

    def __init__(self) -> None:
        super().__init__()
        self.subscribers: List[EventSubscriber] = []

    def publish(self, event: any):
        for subscriber in self.subscribers:
            if subscriber.event == event.__class__.__name__:
                subscriber.consume(event)

    def subscribe(self, event_subscriber: EventSubscriber):
        self.subscribers.append(event_subscriber)


class EventSubscriber:

    def __init__(self, event: str) -> None:
        super().__init__()
        self.event = event

    def subscribe(self, event_bus: EventBus):
        event_bus.subscribe(self)

    @abstractmethod
    def consume(self, event: any):
        pass
