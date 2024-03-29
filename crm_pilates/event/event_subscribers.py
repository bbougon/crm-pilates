from crm_pilates.command.command_bus import CommandBus
from crm_pilates.domain.attending.session_checkin_saga_handler import (
    SessionCheckedIn,
)
from crm_pilates.domain.attending.session_checkout_command_handler import (
    SessionCheckedOut,
)
from crm_pilates.domain.client.client_command_handlers import ClientDeleted
from crm_pilates.domain.commands import (
    DecreaseClientCreditsCommand,
    RefundClientCreditsCommand,
    RemoveAttendeeFromClassroomCommand,
)
from crm_pilates.event.event_bus import EventSubscriber


class SessionCheckedInEventSubscriber(EventSubscriber):
    def __init__(self, command_bus: CommandBus) -> None:
        super().__init__("SessionCheckedIn")
        self.command_bus = command_bus

    def consume(self, event: SessionCheckedIn):
        self.command_bus.send(
            DecreaseClientCreditsCommand(event.root_id, event.checked_in_attendee)
        )


class SessionCheckedOutEventSubscriber(EventSubscriber):
    def __init__(self, command_bus: CommandBus) -> None:
        super().__init__("SessionCheckedOut")
        self.command_bus = command_bus

    def consume(self, event: SessionCheckedOut):
        self.command_bus.send(
            RefundClientCreditsCommand(event.root_id, event.checked_out_attendee)
        )


class ClientDeletedEventSubscriber(EventSubscriber):
    def __init__(self, command_bus: CommandBus) -> None:
        super().__init__("ClientDeleted")
        self.command_bus = command_bus

    def consume(self, event: ClientDeleted):
        self.command_bus.send(RemoveAttendeeFromClassroomCommand(event.root_id))
