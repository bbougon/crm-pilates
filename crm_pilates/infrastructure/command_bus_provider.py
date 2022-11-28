from crm_pilates.command.command_bus import CommandBus
from crm_pilates.domain.attending.add_attendees_to_session_command_handler import (
    AddAttendeesToSessionSagaHandler,
)
from crm_pilates.domain.scheduling.classroom_schedule_command_handler import (
    ClassroomScheduleCommandHandler,
)
from crm_pilates.domain.scheduling.classroom_patch_command_handler import (
    ClassroomPatchCommandHandler,
)
from crm_pilates.domain.attending.session_checkin_saga_handler import (
    SessionCheckinSagaHandler,
)
from crm_pilates.domain.attending.session_checkout_command_handler import (
    SessionCheckoutCommandHandler,
)
from crm_pilates.domain.attending.session_creation_command_handler import (
    SessionCreationCommandHandler,
)
from crm_pilates.domain.attending.session_in_range_command_handler import (
    SessionInRangeCommandHandler,
)
from crm_pilates.domain.attending.attendee_session_cancellation_saga_handler import (
    AttendeeSessionCancellationSagaHandler,
)
from crm_pilates.domain.client.client_command_handlers import (
    ClientCreationCommandHandler,
    AddCreditsToClientCommandHandler,
    DecreaseClientCreditsCommandHandler,
    RefundClientCreditsCommandHandler,
    DeleteClientCommandHandler,
)
from crm_pilates.domain.commands import (
    ClassroomScheduleCommand,
    ClientCreationCommand,
    ClassroomPatchCommand,
    GetNextSessionsCommand,
    SessionCreationCommand,
    GetSessionsInRangeCommand,
    SessionCheckoutCommand,
    AddCreditsToClientCommand,
    DecreaseClientCreditsCommand,
    RefundClientCreditsCommand,
    DeleteClientCommand,
)
from crm_pilates.domain.attending.next_sessions_command_handler import (
    NextSessionsCommandHandler,
)
from crm_pilates.domain.sagas import (
    SessionCheckinSaga,
    AttendeeSessionCancellationSaga,
    AddAttendeesToSessionSaga,
)
from crm_pilates.event.event_subscribers import (
    SessionCheckedInEventSubscriber,
    SessionCheckedOutEventSubscriber,
)
from crm_pilates.infrastructure.event_bus_provider import EventBusProvider


class CommandBusProvider:
    command_bus: CommandBus


command_handlers = {
    ClassroomScheduleCommand.__name__: ClassroomScheduleCommandHandler(),
    ClassroomPatchCommand.__name__: ClassroomPatchCommandHandler(),
    ClientCreationCommand.__name__: ClientCreationCommandHandler(),
    AddCreditsToClientCommand.__name__: AddCreditsToClientCommandHandler(),
    GetNextSessionsCommand.__name__: NextSessionsCommandHandler(),
    GetSessionsInRangeCommand.__name__: SessionInRangeCommandHandler(),
    SessionCreationCommand.__name__: SessionCreationCommandHandler(),
    SessionCheckoutCommand.__name__: SessionCheckoutCommandHandler(),
    DecreaseClientCreditsCommand.__name__: DecreaseClientCreditsCommandHandler(),
    RefundClientCreditsCommand.__name__: RefundClientCreditsCommandHandler(),
    DeleteClientCommand.__name__: DeleteClientCommandHandler(),
}

saga_handlers = {
    SessionCheckinSaga.__name__: SessionCheckinSagaHandler,
    AttendeeSessionCancellationSaga.__name__: AttendeeSessionCancellationSagaHandler,
    AddAttendeesToSessionSaga.__name__: AddAttendeesToSessionSagaHandler,
}

CommandBusProvider.command_bus = CommandBus(command_handlers, saga_handlers)


SessionCheckedInEventSubscriber(CommandBusProvider.command_bus).subscribe(
    EventBusProvider.event_bus
)
SessionCheckedOutEventSubscriber(CommandBusProvider.command_bus).subscribe(
    EventBusProvider.event_bus
)
