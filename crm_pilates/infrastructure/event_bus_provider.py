from __future__ import annotations

from crm_pilates.event.event_bus import EventBus


class EventBusProvider:
    event_bus: EventBus

    @classmethod
    def publish(cls, event: any):
        cls.event_bus.publish(event)


EventBusProvider.event_bus = EventBus()
