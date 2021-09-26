from abc import abstractmethod
from typing import Tuple

from command.command_bus import CommandBus
from command.command_handler import Command, Status
from event.event_store import Event


class Saga(Command):
    pass


class SagaHandler:

    def __init__(self, command_bus: CommandBus) -> None:
        super().__init__()
        self._command_bus = command_bus

    @abstractmethod
    def execute(self, saga: Saga) -> Tuple[Event, Status]:
        pass
