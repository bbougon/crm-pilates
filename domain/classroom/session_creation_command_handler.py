from datetime import datetime
from typing import List
from uuid import UUID

from command.command_handler import CommandHandler
from domain.classroom.classroom import Classroom, ConfirmedSession, Attendee
from domain.commands import SessionCreationCommand
from event.event_store import Event, EventSourced
from infrastructure.repository_provider import RepositoryProvider


@EventSourced
class ConfirmedSessionEvent(Event):

    def __init__(self, root_id: UUID, classroom_id: UUID, name: str, position: int, start: datetime, stop: datetime, attendees: List[Attendee]) -> None:
        super().__init__(root_id)
        self.classroom_id = classroom_id
        self.name = name
        self.position = position
        self.start = start
        self.stop = stop
        self.attendees = attendees
        self.payload = self._to_payload()

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
            "attendees": list(map(lambda attendee: {"id": attendee.id, "attendance": attendee.attendance.value}, self.attendees))
        }


class SessionCreationCommandHandler(CommandHandler):

    def execute(self, command: SessionCreationCommand) -> ConfirmedSessionEvent:
        classroom: Classroom = RepositoryProvider.write_repositories.classroom.get_by_id(command.classroom_id)
        session: ConfirmedSession = classroom.confirm_session_at(command.session_date)
        RepositoryProvider.write_repositories.session.persist(session)
        return ConfirmedSessionEvent(session.id, session.classroom_id, session.name, session.position, session.start, session.stop, session.attendees)
