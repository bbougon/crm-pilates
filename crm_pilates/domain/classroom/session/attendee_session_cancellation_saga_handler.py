from typing import Tuple
from uuid import UUID

from crm_pilates.command.command_handler import Status
from crm_pilates.command.saga_handler import SagaHandler
from crm_pilates.domain.classroom.classroom import ConfirmedSession, Session
from crm_pilates.domain.classroom.attendee import Attendee
from crm_pilates.domain.classroom.session.session_creation_command_handler import ConfirmedSessionEvent
from crm_pilates.domain.commands import SessionCreationCommand
from crm_pilates.domain.sagas import AttendeeSessionCancellationSaga
from crm_pilates.event.event_store import Event, EventSourced
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


@EventSourced
class AttendeeSessionCancelled(Event):

    def __init__(self, root_id: UUID, cancelled_attendee: Attendee) -> None:
        self.cancelled_attendee = cancelled_attendee
        super().__init__(root_id)

    def _to_payload(self):
        return {
            "session_id": self.root_id,
            "attendee": {
                "id": self.cancelled_attendee.id
            }
        }


class AttendeeSessionCancellationSagaHandler(SagaHandler):

    def execute(self, saga: AttendeeSessionCancellationSaga) -> Tuple[AttendeeSessionCancelled, Status]:
        session: Session = RepositoryProvider.write_repositories.session.get_by_classroom_id_and_date(saga.classroom_id, saga.session_date)
        if session:
            session_id = session.id
            status = Status.UPDATED
        else:
            confirmed_session_event: Tuple[ConfirmedSessionEvent, Status] = self._command_bus.send(
                SessionCreationCommand(saga.classroom_id, saga.session_date))
            session_id = confirmed_session_event[0].event.root_id
            status = Status.CREATED

        confirmed_session: ConfirmedSession = RepositoryProvider.write_repositories.session.get_by_id(session_id)
        cancelled_attendee = Attendee.create(saga.attendee_id)
        confirmed_session.cancel(cancelled_attendee)
        return AttendeeSessionCancelled(confirmed_session.id, cancelled_attendee), status
