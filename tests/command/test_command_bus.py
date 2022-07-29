from dataclasses import dataclass
from typing import Tuple

from crm_pilates.command.command_bus import CommandBus
from crm_pilates.command.command_handler import CommandHandler, Command, Status
from crm_pilates.event.event_store import Event


@dataclass
class SimpleCommand(Command):
    name: str


@dataclass
class SimpleCommandExecuted(Event):
    def _to_payload(self):
        pass

    name: str
    id: int = 123


class SimpleCommandHandler(CommandHandler):
    def execute(self, command: SimpleCommand) -> Tuple[SimpleCommandExecuted, Status]:
        return SimpleCommandExecuted(name=command.name), Status.NONE


def test_send_a_command_and_retrieve_response():
    command_bus = CommandBus({"SimpleCommand": SimpleCommandHandler()}, {})

    response, status = command_bus.send(SimpleCommand(name="name"))

    assert isinstance(response.event, SimpleCommandExecuted)
    assert response.event.id == 123
    assert response.event.name == "name"
