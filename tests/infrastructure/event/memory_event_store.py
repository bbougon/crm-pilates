from event.event_store import EventStore, Event


class MemoryEventStore(EventStore):

    def __init__(self):
        self.events = []

    def persist(self, event: Event):
        self.events.append(event)

    def get_all(self):
        return self.events