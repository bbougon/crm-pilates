from command.command_handler import CommandHandler
from domain.classroom.classroom import Classroom, Duration, TimeUnit
from domain.classroom.commands import ClassroomCreationCommand
from infrastructure.repositories import Repositories


class ClassroomCreated:

    def __init__(self, classroom: Classroom) -> None:
        super().__init__()
        self.id = classroom.id
        self.name = classroom.name
        self.duration = classroom.duration
        self.start_date = classroom.start_date


class ClassroomCreationCommandHandler(CommandHandler):

    def __init__(self, repositories: Repositories) -> None:
        super().__init__()
        self.repositories = repositories

    def execute(self, command: ClassroomCreationCommand) -> None:
        classroom = Classroom.create(command.name, command.start_date,
        Duration(command.duration.duration, TimeUnit(command.duration.unit.value)))
        self.repositories.classroom.persist(classroom)
        return ClassroomCreated(classroom)
