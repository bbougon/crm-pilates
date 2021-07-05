import functools


class Event:
    pass


def eventsourced(event: Event) -> Event:

    @functools.wraps(event)
    def wrapper_eventsourced(*args, **kwargs):
        pass

    return event
