from abc import abstractmethod
from enum import Enum

from crm_pilates.event.event_store import Event


class Command:
    pass


class Status(Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    NONE = "NONE"


class CommandHandler:
    @abstractmethod
    def execute(self, command: Command) -> Event:
        pass
