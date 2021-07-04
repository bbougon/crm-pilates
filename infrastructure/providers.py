from command.command_bus import CommandBus
from domain.classroom.classroom_command_handler import ClassroomCreationCommandHandler
from domain.commands import ClassroomCreationCommand
from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repository import MemoryClassroomRepository

repo = Repositories({"classroom": MemoryClassroomRepository()})

handlers = {
    ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(repo)
}


def repository_provider():
    return repo


command_bus = CommandBus(handlers)


def command_bus_provider():
    return command_bus
