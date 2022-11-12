from datetime import datetime
from typing import List
from uuid import UUID

from crm_pilates.command.command_handler import CommandHandler
from crm_pilates.domain.attending.session import ConfirmedSession
from crm_pilates.domain.commands import SessionCreationCommand
from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.event.event_store import Event, EventSourced
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


@EventSourced
class ConfirmedSessionEvent(Event):
    def __init__(
        self,
        root_id: UUID,
        classroom_id: UUID,
        name: str,
        position: int,
        subject: ClassroomSubject,
        start: datetime,
        stop: datetime,
        attendees: List[Attendee],
    ) -> None:
        self.classroom_id = classroom_id
        self.name = name
        self.position = position
        self.subject = subject
        self.start = start
        self.stop = stop
        self.attendees = attendees
        super().__init__(root_id)

    def _to_payload(self):
        return {
            "id": self.root_id,
            "classroom_id": self.classroom_id,
            "name": self.name,
            "position": self.position,
            "subject": self.subject.value,
            "schedule": {"start": self.start, "stop": self.stop},
            "attendees": list(
                map(
                    lambda attendee: {
                        "id": attendee.id,
                        "attendance": attendee.attendance.value,
                    },
                    self.attendees,
                )
            ),
        }


class SessionCreationCommandHandler(CommandHandler):
    def execute(self, command: SessionCreationCommand) -> ConfirmedSessionEvent:
        classroom: Classroom = (
            RepositoryProvider.write_repositories.classroom.get_by_id(
                command.classroom_id
            )
        )
        session: ConfirmedSession = ConfirmedSession.create(
            classroom, command.session_date
        )
        RepositoryProvider.write_repositories.session.persist(session)
        return ConfirmedSessionEvent(
            session.id,
            session.classroom_id,
            session.name,
            session.position,
            session.subject,
            session.start,
            session.stop,
            session.attendees,
        )
