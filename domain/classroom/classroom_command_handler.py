from dataclasses import dataclass

from command.command_handler import CommandHandler
from command.response import Event
from domain.classroom.classroom import Classroom, Duration, TimeUnit, Schedule
from domain.commands import ClassroomCreationCommand
from infrastructure.repositories import Repositories


@dataclass
class ClassroomCreated(Event):
    id: int
    name: str
    duration: Duration
    schedule: Schedule


class ClassroomCreationCommandHandler(CommandHandler):

    def __init__(self, repositories: Repositories) -> None:
        super().__init__()
        self.repositories = repositories

    def execute(self, command: ClassroomCreationCommand) -> ClassroomCreated:
        classroom = Classroom.create(command.name, command.start_date, stop_date=command.stop_date,
                                     duration=Duration(duration=command.duration.duration,
                                                       time_unit=TimeUnit(command.duration.unit.value)))
        self.repositories.classroom.persist(classroom)
        return ClassroomCreated(id=classroom.id, name=classroom.name, duration=classroom.duration,
                                schedule=classroom.schedule)
