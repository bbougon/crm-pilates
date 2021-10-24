from typing import Tuple, List
from uuid import UUID

from command.command_handler import CommandHandler, Status
from domain.classroom.classroom import Classroom, Session
from domain.commands import GetSessionsInRangeCommand
from event.event_store import Event
from infrastructure.repository_provider import RepositoryProvider


class SessionInRange(Event):

    def __init__(self, session: Session, root_id: UUID = None) -> None:
        super().__init__(root_id)
        self.root_id = session.id
        self.name = session.name
        self.classroom_id = session.classroom_id
        self.position = session.position
        self.start = session.start
        self.stop = session.stop
        self.attendees = list(map(lambda attendee: {
            "id": attendee.id,
            "attendance": attendee.attendance.value
        }, session.attendees))

    def _to_payload(self):
        pass


class SessionsInRange(Event):

    def __init__(self, sessions: [SessionInRange], root_id: UUID = None) -> None:
        super().__init__(root_id)
        self.sessions = sessions

    def _to_payload(self):
        pass


class SessionInRangeCommandHandler(CommandHandler):
    def execute(self, command: GetSessionsInRangeCommand) -> Tuple[Event, Status]:
        classrooms: List[Classroom] = next(RepositoryProvider.read_repositories.classroom.get_classrooms_in_range(command.start_date, command.end_date))
        sessions = []
        for classroom in classrooms:
            classroom_sessions: [Session] = classroom.sessions_in_range(command.start_date, command.end_date)
            for classroom_session in classroom_sessions:
                session: Session = RepositoryProvider.read_repositories.session.get_by_classroom_id_and_date(classroom_session.classroom_id, classroom_session.start)
                sessions.append(SessionInRange(session or classroom_session))
        sessions.sort(key=lambda session: session.start)
        return SessionsInRange(sessions), Status.NONE
