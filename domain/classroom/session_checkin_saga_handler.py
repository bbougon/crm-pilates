from datetime import datetime
from typing import List
from uuid import UUID

from command.saga_handler import SagaHandler
from domain.classroom.classroom import ConfirmedSession, Attendee
from domain.classroom.session_creation_command_handler import ConfirmedSessionEvent
from domain.commands import SessionCreationCommand
from domain.sagas import SessionCheckinSaga
from event.event_store import Event
from infrastructure.repository_provider import RepositoryProvider


class SessionCheckedIn(Event):
    id: UUID
    name: str
    classroom_id: UUID
    position: int
    start: datetime
    stop: datetime
    attendees: List[dict]

    def __init__(self, root_id: UUID, name: str, classroom_id: UUID, position: int, start: datetime, stop: datetime,
                 attendees: List[Attendee]) -> None:
        super().__init__(root_id)
        self.name = name
        self.classroom_id = classroom_id
        self.position = position
        self.start = start
        self.stop = stop
        self.attendees = list(map(lambda attendee: self.__map_attendee(attendee), attendees))

    def __map_attendee(self, attendee: Attendee) -> dict:
        return {"id": attendee.id, "status": attendee.attendance.value}

    def _to_payload(self):
        pass


class SessionCheckinSagaHandler(SagaHandler):

    def execute(self, saga: SessionCheckinSaga) -> SessionCheckedIn:
        confirmed_session_event: ConfirmedSessionEvent = self._command_bus.send(
            SessionCreationCommand(saga.classroom_id, saga.session_date)).event
        confirmed_session: ConfirmedSession = RepositoryProvider.write_repositories.session.get_by_id(
            confirmed_session_event.root_id)
        confirmed_session.checkin(Attendee.create(saga.attendee))
        return SessionCheckedIn(confirmed_session.id, confirmed_session.name, confirmed_session.classroom_id,
                                confirmed_session.position, confirmed_session.start, confirmed_session.stop,
                                confirmed_session.attendees)
