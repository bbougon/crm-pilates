from command.command_bus import CommandBus
from domain.classroom.classroom_command_handler import ClassroomCreationCommandHandler
from domain.commands import ClassroomCreationCommand


class CommandBusProvider:
    command_bus: CommandBus


handlers = {
    ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler()
}

CommandBusProvider.command_bus = CommandBus(handlers)
