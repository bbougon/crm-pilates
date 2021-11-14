from typing import Tuple
from uuid import UUID

from command.command_handler import Status
from command.saga_handler import SagaHandler
from domain.classroom.classroom import ConfirmedSession, Attendee
from domain.classroom.session.session_creation_command_handler import ConfirmedSessionEvent
from domain.commands import SessionCreationCommand
from domain.sagas import SessionCheckinSaga
from event.event_store import Event, EventSourced
from infrastructure.repository_provider import RepositoryProvider


@EventSourced
class SessionCheckedIn(Event):

    def __init__(self, root_id: UUID, attendee: Attendee) -> None:
        self.checked_in_attendee = attendee
        super().__init__(root_id)

    def __map_attendee(self, attendee: Attendee) -> dict:
        return {"id": attendee.id, "attendance": attendee.attendance.value}

    def _to_payload(self):
        return {
            "session_id": self.root_id,
            "attendee": self.__map_attendee(self.checked_in_attendee)
        }


class SessionCheckinSagaHandler(SagaHandler):

    def execute(self, saga: SessionCheckinSaga) -> Tuple[SessionCheckedIn, Status]:
        session = RepositoryProvider.write_repositories.session.get_by_classroom_id_and_date(saga.classroom_id, saga.session_date)
        if session:
            session_id = session.id
            status = Status.UPDATED
        else:
            confirmed_session_event: Tuple[ConfirmedSessionEvent, Status] = self._command_bus.send(
                SessionCreationCommand(saga.classroom_id, saga.session_date))
            session_id = confirmed_session_event[0].event.root_id
            status = Status.CREATED

        confirmed_session: ConfirmedSession = RepositoryProvider.write_repositories.session.get_by_id(session_id)
        checked_in_attendee: Attendee = confirmed_session.checkin(Attendee.create(saga.attendee))
        return SessionCheckedIn(confirmed_session.id, checked_in_attendee), status
