from typing import List
from uuid import UUID

from command.command_handler import CommandHandler
from domain.classroom.classroom import Classroom
from domain.client.client import Client
from domain.commands import GetNextSessionsCommand
from domain.session.session import Session
from event.event_store import Event
from infrastructure.repository_provider import RepositoryProvider


class NextScheduledSessions(Event):

    def __init__(self, sessions: [Session], root_id: UUID = None) -> None:
        super().__init__(root_id)
        self.sessions = sessions

    def _to_payload(self):
        pass


class NextSessionsCommandHandler(CommandHandler):

    def execute(self, command: GetNextSessionsCommand) -> Event:
        classrooms: List[Classroom] = next(RepositoryProvider.read_repositories.classroom.get_next_sessions_from(command.current_time))
        next_sessions = []
        for classroom in classrooms:
            attendees: List[Client] = []
            for attendee in classroom.attendees:
                attendees.append(RepositoryProvider.read_repositories.client.get_by_id(attendee.id))
            next_sessions.append(Session(classroom, attendees))
        return NextScheduledSessions(next_sessions)
