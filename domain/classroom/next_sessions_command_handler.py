from typing import List, Tuple
from uuid import UUID

from command.command_handler import CommandHandler, Status
from domain.classroom.classroom import Classroom, Session
from domain.commands import GetNextSessionsCommand
from event.event_store import Event
from infrastructure.repository_provider import RepositoryProvider


class NextScheduledSession(Event):

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


class NextScheduledSessions(Event):

    def __init__(self, sessions: [NextScheduledSession], root_id: UUID = None) -> None:
        super().__init__(root_id)
        self.sessions = sessions

    def _to_payload(self):
        pass


class NextSessionsCommandHandler(CommandHandler):

    def execute(self, command: GetNextSessionsCommand) -> Tuple[NextScheduledSessions, Status]:
        classrooms: List[Classroom] = next(
            RepositoryProvider.read_repositories.classroom.get_next_classrooms_from(command.current_time))
        next_sessions = []
        for classroom in classrooms:
            next_session = classroom.next_session()
            if next_session:
                session: Session = RepositoryProvider.read_repositories.session.get_by_classroom_id_and_date(classroom.id, next_session.start)
                next_sessions.append(NextScheduledSession(session or next_session))
        return NextScheduledSessions(next_sessions), Status.NONE
