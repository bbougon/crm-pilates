from dataclasses import dataclass

from command.command_bus import CommandBus
from command.command_handler import CommandHandler, Command
from event.event_store import Event


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

    def execute(self, command: SimpleCommand) -> SimpleCommandExecuted:
        return SimpleCommandExecuted(name = command.name)


def test_send_a_command_and_retrieve_response():
    command_bus = CommandBus({"SimpleCommand": SimpleCommandHandler()})

    response = command_bus.send(SimpleCommand(name="name"))

    assert isinstance(response.event, SimpleCommandExecuted)
    assert response.event.id == 123
    assert response.event.name == "name"