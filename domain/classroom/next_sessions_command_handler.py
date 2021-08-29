from typing import List
from uuid import UUID

from command.command_handler import CommandHandler
from domain.classroom.classroom import Classroom, ScheduledSession
from domain.commands import GetNextSessionsCommand
from event.event_store import Event
from infrastructure.repository_provider import RepositoryProvider


class NextScheduledSession(Event):

    def __init__(self, session: ScheduledSession, root_id: UUID = None) -> None:
        super().__init__(root_id)
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

    def execute(self, command: GetNextSessionsCommand) -> NextScheduledSessions:
        classrooms: List[Classroom] = next(
            RepositoryProvider.read_repositories.classroom.get_next_classrooms_from(command.current_time))
        next_sessions = []
        for classroom in classrooms:
            next_sessions.append(NextScheduledSession(classroom.next_session()))
        return NextScheduledSessions(next_sessions)
