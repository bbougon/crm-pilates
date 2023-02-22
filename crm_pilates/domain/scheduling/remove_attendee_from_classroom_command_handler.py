from __future__ import annotations
from typing import List
from uuid import UUID

from crm_pilates.command.command_handler import CommandHandler
from crm_pilates.domain.commands import RemoveAttendeeFromClassroomCommand
from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.event.event_store import Event, EventSourced
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


@EventSourced
class AttendeeRemovedFromClassroom(Event):
    def __init__(self, root_id: UUID, classrooms: List[UUID]):
        self.classrooms = classrooms
        super().__init__(root_id)

    def _to_payload(self) -> dict:
        return {"attendee_id": self.root_id, "classrooms": self.classrooms}


class RemoveAttendeeFromClassroomCommandHandler(CommandHandler):
    def execute(self, command: RemoveAttendeeFromClassroomCommand) -> Event:
        classrooms: List[
            Classroom
        ] = RepositoryProvider.write_repositories.classroom.get_classrooms_where_attendee_in(
            command.id
        )
        for classroom in classrooms:
            attendees = filter(
                lambda attendee: attendee.id == command.id, classroom.attendees
            )
            for attendee in attendees:
                classroom.attendees.remove(attendee)
        return AttendeeRemovedFromClassroom(
            command.id, [classroom.id for classroom in classrooms]
        )
