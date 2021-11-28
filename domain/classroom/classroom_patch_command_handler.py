from typing import List, Tuple
from uuid import UUID

from command.command_handler import CommandHandler, Status
from domain.classroom.classroom import Classroom
from domain.classroom.attendee import Attendee
from domain.commands import ClassroomPatchCommand
from event.event_store import Event, EventSourced
from infrastructure.repository_provider import RepositoryProvider


@EventSourced
class AllAttendeesAdded(Event):

    def __init__(self, root_id: UUID, attendees: List[Attendee]) -> None:
        self.attendees = list(map(lambda attendee: {"id": attendee._id}, attendees))
        super().__init__(root_id)

    def _to_payload(self):
        return {
            "attendees": self.attendees
        }


class ClassroomPatchCommandHandler(CommandHandler):

    def execute(self, command: ClassroomPatchCommand) -> Tuple[AllAttendeesAdded, Status]:
        self.__check_attendees_are_clients(command)
        classroom: Classroom = RepositoryProvider.write_repositories.classroom.get_by_id(command.classroom_id)
        attendees: List[Attendee] = list(map(lambda attendee: Attendee(attendee), command.attendees))
        classroom.all_attendees(attendees)
        return AllAttendeesAdded(classroom._id, attendees), Status.CREATED

    @classmethod
    def __check_attendees_are_clients(cls, command):
        list(map(lambda id: RepositoryProvider.write_repositories.client.get_by_id(id), command.attendees))
