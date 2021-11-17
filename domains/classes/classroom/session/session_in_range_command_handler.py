from typing import Tuple, List

from command.command_handler import CommandHandler, Status
from domains.classes.classroom.classroom import Classroom, Session
from domains.classes.classroom.session.existing_sessions import ExistingSessions, ExistingSession
from domains.classes.commands import GetSessionsInRangeCommand
from event.event_store import Event
from infrastructure.repository_provider import RepositoryProvider


class SessionInRangeCommandHandler(CommandHandler):
    def execute(self, command: GetSessionsInRangeCommand) -> Tuple[Event, Status]:
        classrooms: List[Classroom] = next(RepositoryProvider.read_repositories.classroom.get_classrooms_in_range(command.start_date, command.end_date))
        sessions = []
        for classroom in classrooms:
            classroom_sessions: [Session] = classroom.sessions_in_range(command.start_date, command.end_date)
            for classroom_session in classroom_sessions:
                session: Session = RepositoryProvider.read_repositories.session.get_by_classroom_id_and_date(classroom_session.classroom_id, classroom_session.start)
                sessions.append(ExistingSession(session or classroom_session))
        sessions.sort(key=lambda session: session.start)
        return ExistingSessions(sessions), Status.NONE
