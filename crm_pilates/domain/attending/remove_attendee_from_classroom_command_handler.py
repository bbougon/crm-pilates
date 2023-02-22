from typing import List

from crm_pilates.command.command_handler import CommandHandler
from crm_pilates.domain.commands import RemoveAttendeeFromClassroomCommand
from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.event.event_store import Event
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


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
