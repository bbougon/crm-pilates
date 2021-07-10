from command.command_handler import CommandHandler
from domain.classroom.classroom import Classroom, Duration, TimeUnit, Schedule
from domain.commands import ClassroomCreationCommand
from infrastructure.event.event_store import Event, EventSourced
from infrastructure.repositories import Repositories


@EventSourced
class ClassroomCreated(Event):
    id: str
    name: str
    position: int
    duration: Duration
    schedule: Schedule

    def __init__(self, id: str, name: str, position: int, duration: Duration, schedule: Schedule) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.position = position
        self.duration = duration
        self.schedule = schedule

    def __call__(self, *args, **kwargs):
        pass

    def _to_payload(self):
        return {
            "id": self.id,
            "name": self.name,
            "position": self.position,
            "duration": self.duration.__dict__,
            "schedule": self.schedule.__dict__
        }


class ClassroomCreationCommandHandler(CommandHandler):

    def __init__(self, repositories: Repositories) -> None:
        super().__init__()
        self.repositories = repositories

    def execute(self, command: ClassroomCreationCommand) -> ClassroomCreated:
        classroom = Classroom.create(command.name, command.start_date, command.position, stop_date=command.stop_date,
                                     duration=Duration(duration=command.duration.duration,
                                                       time_unit=TimeUnit(command.duration.unit.value)))
        self.repositories.classroom.persist(classroom)
        return ClassroomCreated(id=classroom.id, name=classroom.name, position=classroom.position,
                                duration=classroom.duration,
                                schedule=classroom.schedule)
