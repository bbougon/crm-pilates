from uuid import UUID

from domain.classroom.classroom import Classroom
from domain.client.client import Client, Credits
from infrastructure.repository_provider import RepositoryProvider
from web.presentation.domain.detailed_attendee import DetailedAttendee, AvailableCredits
from web.presentation.domain.detailed_classroom import DetailedClassroom


def get_detailed_classroom(id: UUID):
    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(id)
    return DetailedClassroom(classroom, get_detailed_attendees(classroom))


def get_detailed_attendees(classroom):
    return list(
        map(lambda attendee: to_detailed_attendee(attendee.id, attendee.attendance.value), classroom.attendees))


def to_detailed_attendee(attendee_id: UUID, attendance: str) -> DetailedAttendee:
    attendee: Client = RepositoryProvider.read_repositories.client.get_by_id(attendee_id)

    def __to_credits(_credits: Credits):
        return AvailableCredits(_credits.subject.value, _credits.value)

    attendee_credits = list(map(lambda credit: __to_credits(credit), attendee.credits))
    return DetailedAttendee(attendee.id, attendee.firstname, attendee.lastname, attendance, attendee_credits)
