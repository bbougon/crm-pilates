from command.command_bus import CommandBus
from domain.classroom.classroom_creation_command_handler import ClassroomCreationCommandHandler
from domain.classroom.classroom_patch_command_handler import ClassroomPatchCommandHandler
from domain.classroom.session_checkin_saga_handler import SessionCheckinSagaHandler
from domain.classroom.session_checkout_command_handler import SessionCheckoutCommandHandler
from domain.classroom.session_creation_command_handler import SessionCreationCommandHandler
from domain.classroom.session_in_range_command_handler import SessionInRangeCommandHandler
from domain.client.client_command_handler import ClientCreationCommandHandler
from domain.commands import ClassroomCreationCommand, ClientCreationCommand, ClassroomPatchCommand, \
    GetNextSessionsCommand, SessionCreationCommand, GetSessionsInRangeCommand, SessionCheckoutCommand
from domain.classroom.next_sessions_command_handler import NextSessionsCommandHandler
from domain.sagas import SessionCheckinSaga


class CommandBusProvider:
    command_bus: CommandBus


command_handlers = {
    ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(),
    ClassroomPatchCommand.__name__: ClassroomPatchCommandHandler(),
    ClientCreationCommand.__name__: ClientCreationCommandHandler(),
    GetNextSessionsCommand.__name__: NextSessionsCommandHandler(),
    GetSessionsInRangeCommand.__name__: SessionInRangeCommandHandler(),
    SessionCreationCommand.__name__: SessionCreationCommandHandler(),
    SessionCheckoutCommand.__name__: SessionCheckoutCommandHandler()
}

saga_handlers = {
    SessionCheckinSaga.__name__: SessionCheckinSagaHandler
}

CommandBusProvider.command_bus = CommandBus(command_handlers, saga_handlers)
