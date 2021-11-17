from command.command_bus import CommandBus
from domains.classes.classroom.classroom_creation_command_handler import ClassroomCreationCommandHandler
from domains.classes.classroom.classroom_patch_command_handler import ClassroomPatchCommandHandler
from domains.classes.classroom.session.session_checkin_saga_handler import SessionCheckinSagaHandler
from domains.classes.classroom.session.session_checkout_command_handler import SessionCheckoutCommandHandler
from domains.classes.classroom.session.session_creation_command_handler import SessionCreationCommandHandler
from domains.classes.classroom.session.session_in_range_command_handler import SessionInRangeCommandHandler
from domains.classes.classroom.session.attendee_session_cancellation_saga_handler import AttendeeSessionCancellationSagaHandler
from domains.classes.commands import ClassroomCreationCommand, ClassroomPatchCommand, \
    GetNextSessionsCommand, SessionCreationCommand, GetSessionsInRangeCommand, SessionCheckoutCommand
from domains.client.client_command_handler import ClientCreationCommandHandler
from domains.client.commands import ClientCreationCommand
from domains.classes.classroom.session.next_sessions_command_handler import NextSessionsCommandHandler
from domains.sagas import SessionCheckinSaga, AttendeeSessionCancellationSaga


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
    SessionCheckinSaga.__name__: SessionCheckinSagaHandler,
    AttendeeSessionCancellationSaga.__name__: AttendeeSessionCancellationSagaHandler
}

CommandBusProvider.command_bus = CommandBus(command_handlers, saga_handlers)
