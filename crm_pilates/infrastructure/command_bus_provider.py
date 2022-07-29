from crm_pilates.command.command_bus import CommandBus
from crm_pilates.domain.classroom.classroom_creation_command_handler import (
    ClassroomCreationCommandHandler,
)
from crm_pilates.domain.classroom.classroom_patch_command_handler import (
    ClassroomPatchCommandHandler,
)
from crm_pilates.domain.classroom.session.session_checkin_saga_handler import (
    SessionCheckinSagaHandler,
)
from crm_pilates.domain.classroom.session.session_checkout_command_handler import (
    SessionCheckoutCommandHandler,
)
from crm_pilates.domain.classroom.session.session_creation_command_handler import (
    SessionCreationCommandHandler,
)
from crm_pilates.domain.classroom.session.session_in_range_command_handler import (
    SessionInRangeCommandHandler,
)
from crm_pilates.domain.classroom.session.attendee_session_cancellation_saga_handler import (
    AttendeeSessionCancellationSagaHandler,
)
from crm_pilates.domain.client.client_command_handlers import (
    ClientCreationCommandHandler,
    AddCreditsToClientCommandHandler,
    DecreaseClientCreditsCommandHandler,
    RefundClientCreditsCommandHandler,
)
from crm_pilates.domain.commands import (
    ClassroomCreationCommand,
    ClientCreationCommand,
    ClassroomPatchCommand,
    GetNextSessionsCommand,
    SessionCreationCommand,
    GetSessionsInRangeCommand,
    SessionCheckoutCommand,
    AddCreditsToClientCommand,
    DecreaseClientCreditsCommand,
    RefundClientCreditsCommand,
)
from crm_pilates.domain.classroom.session.next_sessions_command_handler import (
    NextSessionsCommandHandler,
)
from crm_pilates.domain.sagas import SessionCheckinSaga, AttendeeSessionCancellationSaga
from crm_pilates.event.event_subscribers import (
    SessionCheckedInEventSubscriber,
    SessionCheckedOutEventSubscriber,
)
from crm_pilates.infrastructure.event_bus_provider import EventBusProvider


class CommandBusProvider:
    command_bus: CommandBus


command_handlers = {
    ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(),
    ClassroomPatchCommand.__name__: ClassroomPatchCommandHandler(),
    ClientCreationCommand.__name__: ClientCreationCommandHandler(),
    AddCreditsToClientCommand.__name__: AddCreditsToClientCommandHandler(),
    GetNextSessionsCommand.__name__: NextSessionsCommandHandler(),
    GetSessionsInRangeCommand.__name__: SessionInRangeCommandHandler(),
    SessionCreationCommand.__name__: SessionCreationCommandHandler(),
    SessionCheckoutCommand.__name__: SessionCheckoutCommandHandler(),
    DecreaseClientCreditsCommand.__name__: DecreaseClientCreditsCommandHandler(),
    RefundClientCreditsCommand.__name__: RefundClientCreditsCommandHandler(),
}

saga_handlers = {
    SessionCheckinSaga.__name__: SessionCheckinSagaHandler,
    AttendeeSessionCancellationSaga.__name__: AttendeeSessionCancellationSagaHandler,
}

CommandBusProvider.command_bus = CommandBus(command_handlers, saga_handlers)


SessionCheckedInEventSubscriber(CommandBusProvider.command_bus).subscribe(
    EventBusProvider.event_bus
)
SessionCheckedOutEventSubscriber(CommandBusProvider.command_bus).subscribe(
    EventBusProvider.event_bus
)
