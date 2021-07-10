from abc import abstractmethod

from infrastructure.event.event_store import Event


class Command:
    pass


class CommandHandler:

    @abstractmethod
    def execute(self, command: Command) -> Event:
        ...
