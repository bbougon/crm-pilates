from abc import abstractmethod

from event.event_store import Event


class Command:
    pass


class CommandHandler:

    @abstractmethod
    def execute(self, command: Command) -> Event:
        pass
