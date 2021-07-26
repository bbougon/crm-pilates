from command.command_bus import CommandBus
from domain.classroom.classroom_command_handler import ClassroomCreationCommandHandler
from domain.client.client_command_handler import ClientCreationCommandHandler
from domain.commands import ClassroomCreationCommand, ClientCreationCommand


class CommandBusProvider:
    command_bus: CommandBus


handlers = {
    ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(),
    ClientCreationCommand.__name__: ClientCreationCommandHandler()
}

CommandBusProvider.command_bus = CommandBus(handlers)
