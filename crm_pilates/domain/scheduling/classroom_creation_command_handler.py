from __future__ import annotations

from typing import List, Tuple
from uuid import UUID

from crm_pilates.command.command_handler import CommandHandler, Status
from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.domain.scheduling.classroom import Classroom, Schedule
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.domain.scheduling.duration import Duration, TimeUnits, MinuteTimeUnit
from crm_pilates.domain.commands import ClassroomCreationCommand
from crm_pilates.event.event_store import Event, EventSourced
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


@EventSourced
class ClassroomCreated(Event):
    id: str
    name: str
    position: int
    duration: Duration
    schedule: Schedule

    def __init__(
        self,
        id: UUID,
        name: str,
        position: int,
        subject: ClassroomSubject,
        duration: Duration,
        schedule: Schedule,
        attendees: List[Attendee],
    ):
        self.__root_id = id
        self.name = name
        self.position = position
        self.subject = subject
        self.duration = duration
        self.schedule = schedule
        self.attendees = list(map(lambda attendee: {"id": attendee.id}, attendees))
        super().__init__(id)

    def _to_payload(self):
        return {
            "id": self.root_id,
            "name": self.name,
            "position": self.position,
            "subject": self.subject.value,
            "duration": {
                "duration": self.duration.time_unit.to_unit(MinuteTimeUnit).value,
                "time_unit": "MINUTE",
            },
            "schedule": self.schedule.__dict__,
            "attendees": self.attendees,
        }


class ClassroomCreationCommandHandler(CommandHandler):
    def __init__(self) -> None:
        super().__init__()

    def execute(
        self, command: ClassroomCreationCommand
    ) -> Tuple[ClassroomCreated, Status]:
        classroom = Classroom.create(
            command.name,
            command.start_date,
            command.position,
            command.subject,
            stop_date=command.stop_date,
            duration=Duration(
                TimeUnits.from_duration(
                    command.duration.unit.value, command.duration.duration
                )
            ),
        )
        attendees: List[Attendee] = list(
            map(
                lambda id: RepositoryProvider.write_repositories.attendee.get_by_id(id),
                command.attendees,
            )
        )
        classroom.all_attendees(attendees)
        RepositoryProvider.write_repositories.classroom.persist(classroom)
        return (
            ClassroomCreated(
                id=classroom.id,
                name=classroom.name,
                position=classroom.position,
                subject=classroom.subject,
                duration=classroom.duration,
                schedule=classroom.schedule,
                attendees=attendees,
            ),
            Status.CREATED,
        )
