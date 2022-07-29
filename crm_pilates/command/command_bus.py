from typing import Tuple

from crm_pilates.command.command_handler import Command, Status
from crm_pilates.command.response import Response


class CommandBus:
    def __init__(self, handlers: dict, saga_handlers: dict) -> None:
        super().__init__()
        self.handlers = handlers
        for saga, saga_handler in saga_handlers.items():
            self.handlers[saga] = saga_handler(self)

    def send(self, command: Command) -> Tuple[Response, Status]:
        event, status = self.handlers[command.__class__.__name__].execute(command)
        return Response(event), status
