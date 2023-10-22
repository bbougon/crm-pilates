from datetime import date
from typing import TypedDict

from crm_pilates.command.command_bus import CommandBus
from crm_pilates.domain.attending.session_checkin_saga_handler import (
    SessionCheckedIn,
)
from crm_pilates.domain.attending.session_checkout_command_handler import (
    SessionCheckedOut,
)
from crm_pilates.domain.client.client_command_handlers import (
    ClientDeleted,
    ClientCreditsDecreased,
)
from crm_pilates.domain.commands import (
    DecreaseClientCreditsCommand,
    RefundClientCreditsCommand,
    RemoveAttendeeFromClassroomCommand,
)
from crm_pilates.domain.email_notifier import MessageNotifier, Message, Body
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


class ClientCreditsDecreasedEmailBody(Body):
    template: str
    parameters: TypedDict(
        "parameters", {"date": str, "subject": str, "credits_left": int}
    )


class ClientCreditsDecreasedEmail(Message):
    body: ClientCreditsDecreasedEmailBody


class ClientCreditDecreasedEventSubscriber(EventSubscriber):
    def __init__(self, event: str, email_notifier: MessageNotifier) -> None:
        super().__init__(event)
        self.email_notifier = email_notifier

    def consume(self, event: ClientCreditsDecreased):
        credit = list(
            filter(
                lambda current_credit: current_credit.subject == event.subject,
                event.credits,
            )
        ).pop(0)
        if credit.value <= 1:
            email: ClientCreditsDecreasedEmail = {
                "to": "bertrand.bougon@gmail.com",
                "body": {
                    "template": "low_credits_notification",
                    "parameters": {
                        "date": date.today().isoformat(),
                        "subject": event.subject.name,
                        "credits_left": credit.value,
                    },
                },
            }
            self.email_notifier.send(email)
