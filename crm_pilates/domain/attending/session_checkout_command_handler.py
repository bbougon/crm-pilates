from typing import Tuple
from uuid import UUID

from crm_pilates.command.command_handler import CommandHandler, Status
from crm_pilates.domain.attending.session import ConfirmedSession
from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.domain.commands import SessionCheckoutCommand
from crm_pilates.event.event_store import Event, EventSourced
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


@EventSourced
class SessionCheckedOut(Event):
    def __init__(self, root_id: UUID, attendee: Attendee) -> None:
        self.checked_out_attendee = attendee
        super().__init__(root_id)

    def _to_payload(self):
        return {
            "session_id": self.root_id,
            "attendee": {
                "id": self.checked_out_attendee.id,
                "attendance": self.checked_out_attendee.attendance.value,
            },
        }


class SessionCheckoutCommandHandler(CommandHandler):
    def execute(
        self, command: SessionCheckoutCommand
    ) -> Tuple[SessionCheckedOut, Status]:
        session: ConfirmedSession = (
            RepositoryProvider.write_repositories.session.get_by_id(command.session_id)
        )
        attendee: Attendee = session.checkout(Attendee.create(command.attendee))
        return SessionCheckedOut(session.id, attendee), Status.CREATED
