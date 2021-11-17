from uuid import UUID

from domains.classes.classroom.classroom import Classroom
from infrastructure.repository_provider import RepositoryProvider
from web.presentation.domain.detailed_attendee import DetailedAttendee
from web.presentation.domain.detailed_classroom import DetailedClassroom


def get_detailed_classroom(id: UUID):
    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(id)
    return DetailedClassroom(classroom, get_detailed_attendees(classroom))


def get_detailed_attendees(classroom):
    return list(
        map(lambda attendee: to_detailed_attendee(attendee.id, attendee.attendance.value), classroom.attendees))


def to_detailed_attendee(attendee_id: UUID, attendance: str) -> DetailedAttendee:
    client = RepositoryProvider.read_repositories.client.get_by_id(attendee_id)
    return DetailedAttendee(client.id, client.firstname, client.lastname, attendance)
