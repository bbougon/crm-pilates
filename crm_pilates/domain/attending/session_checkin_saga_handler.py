from uuid import UUID

from crm_pilates.command.command_bus import CommandBus
from crm_pilates.command.response import Response
from crm_pilates.command.saga_handler import SagaHandler
from crm_pilates.domain.attending.session import ConfirmedSession
from crm_pilates.domain.commands import SessionCreationCommand
from crm_pilates.domain.sagas import SessionCheckinSaga
from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.event.event_store import Event, EventSourced
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


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
            "attendee": self.__map_attendee(self.checked_in_attendee),
        }


class SessionCheckinSagaHandler(SagaHandler):
    def __init__(self, command_bus: CommandBus) -> None:
        super().__init__(command_bus)

    def execute(self, saga: SessionCheckinSaga) -> SessionCheckedIn:
        session = (
            RepositoryProvider.write_repositories.session.get_by_classroom_id_and_date(
                saga.classroom_id, saga.session_date
            )
        )
        if session:
            session_id = session.id
        else:
            confirmed_session_event: Response = self._command_bus.send(
                SessionCreationCommand(saga.classroom_id, saga.session_date)
            )
            session_id = confirmed_session_event.event.root_id

        confirmed_session: ConfirmedSession = (
            RepositoryProvider.write_repositories.session.get_by_id(session_id)
        )
        checked_in_attendee: Attendee = confirmed_session.checkin(
            Attendee.create(saga.attendee)
        )
        return SessionCheckedIn(confirmed_session.id, checked_in_attendee)
