from dataclasses import dataclass

from command.command_handler import Command


@dataclass
class ClientCreationCommand(Command):
    firstname: str
    lastname: str
