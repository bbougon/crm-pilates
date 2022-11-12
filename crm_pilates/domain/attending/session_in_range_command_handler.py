from typing import List

from crm_pilates.command.command_handler import CommandHandler
from crm_pilates.domain.attending.existing_sessions import (
    ExistingSessions,
    ExistingSession,
)
from crm_pilates.domain.attending.session import Session
from crm_pilates.domain.attending.sessions import Sessions
from crm_pilates.domain.commands import GetSessionsInRangeCommand
from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.event.event_store import Event
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


class SessionInRangeCommandHandler(CommandHandler):
    def execute(self, command: GetSessionsInRangeCommand) -> Event:
        classrooms: List[Classroom] = next(
            RepositoryProvider.read_repositories.classroom.get_classrooms_in_range(
                command.start_date, command.end_date
            )
        )
        sessions = []
        for classroom in classrooms:
            classroom_sessions: [Session] = Sessions.sessions_in_range(
                classroom, command.start_date, command.end_date
            )
            for classroom_session in classroom_sessions:
                session: Session = RepositoryProvider.read_repositories.session.get_by_classroom_id_and_date(
                    classroom_session.classroom_id, classroom_session.start
                )
                sessions.append(ExistingSession(session or classroom_session))
        sessions.sort(key=lambda session: session.start)
        return ExistingSessions(sessions)
