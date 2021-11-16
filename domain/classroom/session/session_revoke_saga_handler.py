from typing import Tuple
from uuid import UUID

from command.command_handler import Status
from command.saga_handler import SagaHandler
from domain.classroom.classroom import ConfirmedSession, Attendee
from domain.classroom.session.session_creation_command_handler import ConfirmedSessionEvent
from domain.commands import SessionCreationCommand
from domain.sagas import SessionRevokeSaga
from event.event_store import Event
from infrastructure.repository_provider import RepositoryProvider


class SessionRevoked(Event):

    def __init__(self, root_id: UUID, revoked_attendee: Attendee) -> None:
        super().__init__(root_id)

    def _to_payload(self):
        pass


class SessionRevokeSagaHandler(SagaHandler):

    def execute(self, saga: SessionRevokeSaga) -> Tuple[Event, Status]:
        confirmed_session_event: Tuple[ConfirmedSessionEvent, Status] = self._command_bus.send(
            SessionCreationCommand(saga.classroom_id, saga.session_date))
        session_id = confirmed_session_event[0].event.root_id
        status = Status.CREATED

        confirmed_session: ConfirmedSession = RepositoryProvider.write_repositories.session.get_by_id(session_id)
        revoked_attendee = Attendee.create(saga.attendee_id)
        confirmed_session.revoke(revoked_attendee)
        return SessionRevoked(confirmed_session.id, revoked_attendee), status
