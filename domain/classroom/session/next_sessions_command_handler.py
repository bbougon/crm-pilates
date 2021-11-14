from typing import List, Tuple

from command.command_handler import CommandHandler, Status
from domain.classroom.classroom import Classroom, Session
from domain.classroom.session.existing_sessions import ExistingSessions, ExistingSession
from domain.commands import GetNextSessionsCommand
from infrastructure.repository_provider import RepositoryProvider


class NextSessionsCommandHandler(CommandHandler):

    def execute(self, command: GetNextSessionsCommand) -> Tuple[ExistingSessions, Status]:
        classrooms: List[Classroom] = next(
            RepositoryProvider.read_repositories.classroom.get_next_classrooms_from(command.current_time))
        next_sessions = []
        for classroom in classrooms:
            next_session = classroom.next_session()
            if next_session:
                session: Session = RepositoryProvider.read_repositories.session.get_by_classroom_id_and_date(classroom.id, next_session.start)
                next_sessions.append(ExistingSession(session or next_session))
        return ExistingSessions(next_sessions), Status.NONE
