from dataclasses import dataclass
from datetime import datetime

from command.response import Event
from command.command_handler import CommandHandler
from domain.classroom.classroom import Classroom, Duration, TimeUnit
from domain.commands import ClassroomCreationCommand
from infrastructure.repositories import Repositories


@dataclass
class ClassroomCreated(Event):
    id: int
    name: str
    duration: Duration
    start_date: datetime


class ClassroomCreationCommandHandler(CommandHandler):

    def __init__(self, repositories: Repositories) -> None:
        super().__init__()
        self.repositories = repositories

    def execute(self, command: ClassroomCreationCommand) -> ClassroomCreated:
        classroom = Classroom.create(command.name, command.start_date,
                                     Duration(command.duration.duration, TimeUnit(command.duration.unit.value)))
        self.repositories.classroom.persist(classroom)
        return ClassroomCreated(id=classroom.id, name=classroom.name, duration=classroom.duration,
                                start_date=classroom.start_date)
