from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

from command.saga_handler import SagaHandler
from domain.classroom.classroom import ConfirmedSession, Attendee
from domain.classroom.session_creation_command_handler import ConfirmedSessionEvent
from domain.commands import SessionCreationCommand
from domain.sagas import SessionCheckinSaga
from event.event_store import Event, EventSourced
from infrastructure.repository_provider import RepositoryProvider


class SessionCheckedInStatus(Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"


@EventSourced
class SessionCheckedIn(Event):

    def __init__(self, root_id: UUID, name: str, classroom_id: UUID, position: int, start: datetime, stop: datetime,
                 attendees: List[Attendee], status: SessionCheckedInStatus) -> None:
        super().__init__(root_id)
        self.name = name
        self.classroom_id = classroom_id
        self.position = position
        self.start = start
        self.stop = stop
        self.attendees = list(map(lambda attendee: self.__map_attendee(attendee), attendees))
        self.status: SessionCheckedInStatus = status
        self.payload = self._to_payload()

    def __map_attendee(self, attendee: Attendee) -> dict:
        return {"id": attendee.id, "attendance": attendee.attendance.value}

    def _to_payload(self):
        return {
            "id": self.root_id,
            "classroom_id": self.classroom_id,
            "name": self.name,
            "position": self.position,
            "schedule": {
                "start": self.start,
                "stop": self.stop
            },
            "attendees": list(map(lambda attendee: {"id": attendee["id"], "attendance": attendee["attendance"]}, self.attendees))
        }


class SessionCheckinSagaHandler(SagaHandler):

    def execute(self, saga: SessionCheckinSaga) -> SessionCheckedIn:
        session = RepositoryProvider.write_repositories.session.get_by_classroom_id_and_date(saga.classroom_id, saga.session_date)
        if session:
            session_id = session.id
            session_status = SessionCheckedInStatus.UPDATED
        else:
            confirmed_session_event: ConfirmedSessionEvent = self._command_bus.send(
                SessionCreationCommand(saga.classroom_id, saga.session_date)).event
            session_id = confirmed_session_event.root_id
            session_status = SessionCheckedInStatus.CREATED

        confirmed_session: ConfirmedSession = RepositoryProvider.write_repositories.session.get_by_id(session_id)
        confirmed_session.checkin(Attendee.create(saga.attendee))
        return SessionCheckedIn(confirmed_session.id, confirmed_session.name, confirmed_session.classroom_id,
                                confirmed_session.position, confirmed_session.start, confirmed_session.stop,
                                confirmed_session.attendees, session_status)
