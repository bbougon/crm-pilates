from command.command_handler import Command
from command.response import Response


class CommandBus:

    def __init__(self, handlers: dict) -> None:
        super().__init__()
        self.handlers = handlers

    def send(self, command: Command) -> Response:
        return Response(self.handlers[command.__class__.__name__].execute(command))
