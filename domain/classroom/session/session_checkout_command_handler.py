from typing import Tuple
from uuid import UUID

from command.command_handler import CommandHandler, Status
from domain.classroom.classroom import ConfirmedSession, Attendee
from domain.commands import SessionCheckoutCommand
from event.event_store import Event, EventSourced
from infrastructure.repository_provider import RepositoryProvider


@EventSourced
class SessionCheckedOut(Event):

    def __init__(self, root_id: UUID, attendee: Attendee) -> None:
        self.checked_out_attendee = attendee
        super().__init__(root_id)

    def _to_payload(self):
        return {
            "session_id": self.root_id,
            "attendee": {"id": self.checked_out_attendee.id, "attendance": self.checked_out_attendee.attendance.value}
        }


class SessionCheckoutCommandHandler(CommandHandler):
    def execute(self, command: SessionCheckoutCommand) -> Tuple[SessionCheckedOut, Status]:
        session: ConfirmedSession = RepositoryProvider.write_repositories.session.get_by_id(command.session_id)
        attendee: Attendee = session.checkout(command.attendee)
        return SessionCheckedOut(session.id, attendee), Status.CREATED
