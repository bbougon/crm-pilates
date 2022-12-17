from typing import List
from uuid import UUID

from crm_pilates.command.command_handler import CommandHandler
from crm_pilates.domain.attending.attendees import Attendees
from crm_pilates.domain.commands import ClassroomPatchCommand
from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.event.event_store import Event, EventSourced
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


@EventSourced
class AllAttendeesAdded(Event):
    def __init__(self, root_id: UUID, attendees: List[Attendee]) -> None:
        self.attendees = list(map(lambda attendee: {"id": attendee._id}, attendees))
        super().__init__(root_id)

    def _to_payload(self):
        return {"attendees": self.attendees}


class ClassroomPatchCommandHandler(CommandHandler):
    def execute(self, command: ClassroomPatchCommand) -> AllAttendeesAdded:
        attendees: List[Attendee] = Attendees.by_ids(command.attendees)
        classroom: Classroom = (
            RepositoryProvider.write_repositories.classroom.get_by_id(
                command.classroom_id
            )
        )
        classroom.all_attendees(attendees)
        return AllAttendeesAdded(classroom._id, attendees)
