import functools


class Event:
    pass


def eventsourced(event: Event):

    @functools.wraps(event)
    def wrapper_eventsourced(*args, **kwargs):
        pass
    return wrapper_eventsourced