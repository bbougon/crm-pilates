from typing import List
from uuid import UUID

from command.command_handler import CommandHandler
from domain.classroom.classroom import Classroom, Attendee
from domain.commands import ClassroomPatchCommand
from event.event_store import Event, EventSourced
from infrastructure.repository_provider import RepositoryProvider


@EventSourced
class AttendeesSet(Event):

    def __init__(self, root_id: UUID, attendees: List[Attendee]) -> None:
        super().__init__(root_id)
        self.attendees = list(map(lambda attendee: {"id": attendee.id}, attendees))

    def _to_payload(self):
        return {
            "attendees": self.attendees
        }


class ClassroomPatchCommandHandler(CommandHandler):

    def execute(self, command: ClassroomPatchCommand) -> AttendeesSet:
        self.__check_attendees_are_clients(command)
        classroom: Classroom = RepositoryProvider.repositories.classroom.get_by_id(command.classroom_id)
        attendees: List[Attendee] = list(map(lambda attendee: Attendee(attendee), command.attendees))
        classroom.set_attendees(attendees)
        return AttendeesSet(classroom.id, attendees)

    @classmethod
    def __check_attendees_are_clients(cls, command):
        list(map(lambda id: RepositoryProvider.repositories.client.get_by_id(id), command.attendees))