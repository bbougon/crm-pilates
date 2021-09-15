from __future__ import annotations

from typing import List
from uuid import UUID

from command.command_handler import CommandHandler
from domain.classroom.classroom import Classroom, Schedule, Attendee
from domain.classroom.duration import Duration, TimeUnits, MinuteTimeUnit
from domain.client.client import Client
from domain.commands import ClassroomCreationCommand
from event.event_store import Event, EventSourced
from infrastructure.repository_provider import RepositoryProvider


@EventSourced
class ClassroomCreated(Event):
    id: str
    name: str
    position: int
    duration: Duration
    schedule: Schedule

    def __init__(self, id: UUID, name: str, position: int, duration: Duration, schedule: Schedule,
                 attendees: List[Client]):
        super().__init__(id)
        self.__root_id = id
        self.name = name
        self.position = position
        self.duration = duration
        self.schedule = schedule
        self.attendees = list(map(lambda attendee: {"id": attendee.id}, attendees))
        self.payload = self._to_payload()

    def _to_payload(self):
        return {
            "id": self.root_id,
            "name": self.name,
            "position": self.position,
            "duration": {
                "duration": self.duration.time_unit.to_unit(MinuteTimeUnit).value,
                "time_unit": "MINUTE"
            },
            "schedule": self.schedule.__dict__,
            "attendees": self.attendees
        }


class ClassroomCreationCommandHandler(CommandHandler):

    def __init__(self) -> None:
        super().__init__()

    def execute(self, command: ClassroomCreationCommand) -> ClassroomCreated:
        classroom = Classroom.create(command.name, command.start_date, command.position, stop_date=command.stop_date,
                                     duration=Duration(TimeUnits.from_duration(command.duration.unit.value,
                                                                               command.duration.duration)))
        clients: List[Client] = list(
            map(lambda id: RepositoryProvider.write_repositories.client.get_by_id(id), command.attendees))
        classroom.all_attendees(list(map(lambda client: Attendee.create(client._id), clients)))
        RepositoryProvider.write_repositories.classroom.persist(classroom)
        return ClassroomCreated(id=classroom.id, name=classroom.name, position=classroom.position,
                                duration=classroom.duration, schedule=classroom.schedule, attendees=clients)
