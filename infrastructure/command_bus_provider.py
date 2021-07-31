from command.command_bus import CommandBus
from domain.classroom.classroom_creation_command_handler import ClassroomCreationCommandHandler
from domain.classroom.classroom_patch_command_handler import ClassroomPatchCommandHandler
from domain.client.client_command_handler import ClientCreationCommandHandler
from domain.commands import ClassroomCreationCommand, ClientCreationCommand, ClassroomPatchCommand


class CommandBusProvider:
    command_bus: CommandBus


handlers = {
    ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(),
    ClassroomPatchCommand.__name__: ClassroomPatchCommandHandler(),
    ClientCreationCommand.__name__: ClientCreationCommandHandler()
}

CommandBusProvider.command_bus = CommandBus(handlers)
