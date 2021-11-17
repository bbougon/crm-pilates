from typing import Tuple
from uuid import UUID

from command.command_handler import Status
from command.saga_handler import SagaHandler
from domains.classes.classroom.classroom import ConfirmedSession, Attendee
from domains.classes.classroom.session.session_creation_command_handler import ConfirmedSessionEvent
from domains.classes.commands import SessionCreationCommand
from domains.sagas import AttendeeSessionCancellationSaga
from event.event_store import Event
from infrastructure.repository_provider import RepositoryProvider


class AttendeeSessionCancelled(Event):

    def __init__(self, root_id: UUID, cancelled_attendee: Attendee) -> None:
        super().__init__(root_id)

    def _to_payload(self):
        pass


class AttendeeSessionCancellationSagaHandler(SagaHandler):

    def execute(self, saga: AttendeeSessionCancellationSaga) -> Tuple[Event, Status]:
        confirmed_session_event: Tuple[ConfirmedSessionEvent, Status] = self._command_bus.send(
            SessionCreationCommand(saga.classroom_id, saga.session_date))
        session_id = confirmed_session_event[0].event.root_id
        status = Status.CREATED

        confirmed_session: ConfirmedSession = RepositoryProvider.write_repositories.session.get_by_id(session_id)
        cancelled_attendee = Attendee.create(saga.attendee_id)
        confirmed_session.cancel(cancelled_attendee)
        return AttendeeSessionCancelled(confirmed_session.id, cancelled_attendee), status
