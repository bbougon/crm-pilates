from command.command_bus import CommandBus
from domain.classroom.classroom_creation_command_handler import ClassroomCreationCommandHandler
from domain.classroom.classroom_patch_command_handler import ClassroomPatchCommandHandler
from domain.classroom.session.session_checkin_saga_handler import SessionCheckinSagaHandler
from domain.classroom.session.session_checkout_command_handler import SessionCheckoutCommandHandler
from domain.classroom.session.session_creation_command_handler import SessionCreationCommandHandler
from domain.classroom.session.session_in_range_command_handler import SessionInRangeCommandHandler
from domain.classroom.session.attendee_session_cancellation_saga_handler import AttendeeSessionCancellationSagaHandler
from domain.client.client_command_handlers import ClientCreationCommandHandler, ClientUpdateCommandHandler
from domain.commands import ClassroomCreationCommand, ClientCreationCommand, ClassroomPatchCommand, \
    GetNextSessionsCommand, SessionCreationCommand, GetSessionsInRangeCommand, SessionCheckoutCommand, \
    ClientUpdateCommand
from domain.classroom.session.next_sessions_command_handler import NextSessionsCommandHandler
from domain.sagas import SessionCheckinSaga, AttendeeSessionCancellationSaga


class CommandBusProvider:
    command_bus: CommandBus


command_handlers = {
    ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(),
    ClassroomPatchCommand.__name__: ClassroomPatchCommandHandler(),
    ClientCreationCommand.__name__: ClientCreationCommandHandler(),
    ClientUpdateCommand.__name__: ClientUpdateCommandHandler(),
    GetNextSessionsCommand.__name__: NextSessionsCommandHandler(),
    GetSessionsInRangeCommand.__name__: SessionInRangeCommandHandler(),
    SessionCreationCommand.__name__: SessionCreationCommandHandler(),
    SessionCheckoutCommand.__name__: SessionCheckoutCommandHandler()
}

saga_handlers = {
    SessionCheckinSaga.__name__: SessionCheckinSagaHandler,
    AttendeeSessionCancellationSaga.__name__: AttendeeSessionCancellationSagaHandler
}

CommandBusProvider.command_bus = CommandBus(command_handlers, saga_handlers)
