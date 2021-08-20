from typing import List
from uuid import UUID

from command.command_handler import CommandHandler
from domain.classroom.classroom import Classroom, ScheduledSession
from domain.classroom.duration import MinuteTimeUnit
from domain.client.client import Client
from domain.commands import GetNextSessionsCommand
from event.event_store import Event
from infrastructure.repository_provider import RepositoryProvider


class NextScheduledSession(Event):

    def __init__(self, session: ScheduledSession, attendees: List[Client], root_id: UUID = None) -> None:
        super().__init__(root_id)
        self.name = session.name
        self.id = session.id
        self.position = session.position
        self.start = session.start
        self.stop = session.stop
        self.duration = {
            "time_unit": "MINUTE",
            "duration": session.duration.time_unit.to_unit(MinuteTimeUnit).value
        }
        self.attendees = list(map(lambda client: {
            "client_id": str(client._id),
            "firstname": client.firstname,
            "lastname": client.lastname}, attendees))

    def _to_payload(self):
        pass


class NextScheduledSessions(Event):

    def __init__(self, sessions: [NextScheduledSession], root_id: UUID = None) -> None:
        super().__init__(root_id)
        self.sessions = sessions

    def _to_payload(self):
        pass


class NextSessionsCommandHandler(CommandHandler):

    def execute(self, command: GetNextSessionsCommand) -> Event:
        classrooms: List[Classroom] = next(
            RepositoryProvider.read_repositories.classroom.get_next_classrooms_from(command.current_time))
        next_sessions = []
        for classroom in classrooms:
            attendees: List[Client] = []
            for attendee in classroom.attendees:
                attendees.append(RepositoryProvider.read_repositories.client.get_by_id(attendee._id))
            session: ScheduledSession = classroom.next_session()
            next_sessions.append(NextScheduledSession(session, attendees))
        return NextScheduledSessions(next_sessions)
