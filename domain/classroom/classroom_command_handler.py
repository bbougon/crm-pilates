from __future__ import annotations

from typing import List
from uuid import UUID

from command.command_handler import CommandHandler
from domain.classroom.classroom import Classroom, Duration, TimeUnit, Schedule
from domain.client.client import Client
from domain.commands import ClassroomCreationCommand
from event.event_store import Event, EventSourced
from infrastructure.repositories import Repositories


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

    def __call__(self, *args, **kwargs):
        pass

    def _to_payload(self):
        return {
            "id": self.root_id,
            "name": self.name,
            "position": self.position,
            "duration": self.duration.__dict__,
            "schedule": self.schedule.__dict__,
            "attendees": self.attendees
        }


class Attendee:

    def __init__(self, id: UUID) -> None:
        super().__init__()
        self.id = id

    @staticmethod
    def create(id: UUID) -> Attendee:
        return Attendee(id)


class ClassroomCreationCommandHandler(CommandHandler):

    def __init__(self, repositories: Repositories) -> None:
        super().__init__()
        self.repositories = repositories

    def execute(self, command: ClassroomCreationCommand) -> ClassroomCreated:
        classroom = Classroom.create(command.name, command.start_date, command.position, stop_date=command.stop_date,
                                     duration=Duration(duration=command.duration.duration,
                                                       time_unit=TimeUnit(command.duration.unit.value)))
        clients: List[Client] = list(map(lambda id: self.repositories.client.get_by_id(id), command.attendees))
        classroom.add_attendees(list(map(lambda client: Attendee.create(client.id), clients)))
        self.repositories.classroom.persist(classroom)
        return ClassroomCreated(id=classroom.id, name=classroom.name, position=classroom.position,
                                duration=classroom.duration, schedule=classroom.schedule, attendees=clients)
