from typing import List, Tuple

from crm_pilates.command.command_handler import CommandHandler, Status
from crm_pilates.domain.attending.sessions import Sessions
from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.attending.session import Session
from crm_pilates.domain.attending.existing_sessions import (
    ExistingSessions,
    ExistingSession,
)
from crm_pilates.domain.commands import GetNextSessionsCommand
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


class NextSessionsCommandHandler(CommandHandler):
    def execute(
        self, command: GetNextSessionsCommand
    ) -> Tuple[ExistingSessions, Status]:
        classrooms: List[Classroom] = next(
            RepositoryProvider.read_repositories.classroom.get_next_classrooms_from(
                command.current_time
            )
        )
        next_sessions = []
        for classroom in classrooms:
            _next_session = Sessions.next_session(classroom)
            if _next_session:
                session: Session = RepositoryProvider.read_repositories.session.get_by_classroom_id_and_date(
                    classroom.id, _next_session.start
                )
                next_sessions.append(ExistingSession(session or _next_session))
        return ExistingSessions(next_sessions), Status.NONE
