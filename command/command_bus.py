from command.command import Command
from domain.classroom.classroom_command_handler import ClassroomCreationCommandHandler
from infrastructure.repositories import Repositories


class CommandBus:

    def __init__(self, repositories: Repositories) -> None:
        super().__init__()
        self.repositories = repositories
        self.handlers = {"classroom_creation_command": ClassroomCreationCommandHandler(repositories)}

    def send(self, command: Command) -> None:
        return self.handlers["classroom_creation_command"].execute(command)