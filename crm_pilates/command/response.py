from crm_pilates.event.event_store import Event


class Response:

    def __init__(self, event: Event) -> None:
        super().__init__()
        self.__event = event

    @property
    def event(self) -> Event:
        return self.__event
