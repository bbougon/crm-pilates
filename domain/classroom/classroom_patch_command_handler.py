from command.command_handler import CommandHandler, Command
from domain.classroom.classroom import Classroom, Attendee
from domain.commands import ClassroomPatchCommand
from event.event_store import Event
from infrastructure.repository_provider import RepositoryProvider


class ClassroomPatchCommandHandler(CommandHandler):

    def execute(self, command: ClassroomPatchCommand) -> Event:
        classroom: Classroom = RepositoryProvider.repositories.classroom.get_by_id(command.classroom_id)
        classroom.set_attendees(list(map(lambda attendee: Attendee(attendee), command.attendees)))
