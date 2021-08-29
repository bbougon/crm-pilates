from uuid import UUID

from command.command_handler import CommandHandler
from domain.classroom.classroom import Classroom, ConfirmedSession
from domain.commands import SessionCreationCommand
from event.event_store import Event
from infrastructure.repository_provider import RepositoryProvider


class ConfirmedSessionEvent(Event):
    id: UUID

    def _to_payload(self):
        pass


class SessionCreationCommandHandler(CommandHandler):

    def execute(self, command: SessionCreationCommand) -> ConfirmedSessionEvent:
        classroom: Classroom = RepositoryProvider.write_repositories.classroom.get_by_id(command.classroom_id)
        session: ConfirmedSession = classroom.confirm_session_at(command.session_date)
        RepositoryProvider.write_repositories.session.persist(session)
        return ConfirmedSessionEvent(session.id)
