from uuid import UUID

from domain.classroom.classroom import Classroom
from domain.classroom.classroom_type import ClassroomSubject
from domain.client.client import Client
from infrastructure.repository_provider import RepositoryProvider
from web.presentation.domain.detailed_attendee import DetailedAttendee, AvailableCredits
from web.presentation.domain.detailed_classroom import DetailedClassroom


def get_detailed_classroom(id: UUID):
    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(id)
    return DetailedClassroom(classroom, get_detailed_attendees(classroom))


def get_detailed_attendees(classroom):
    return list(
        map(lambda attendee: to_detailed_attendee(attendee.id, attendee.attendance.value, classroom.subject), classroom.attendees))


def to_detailed_attendee(attendee_id: UUID, attendance: str, session_subject: ClassroomSubject) -> DetailedAttendee:
    attendee: Client = RepositoryProvider.read_repositories.client.get_by_id(attendee_id)
    attendee_credits = next(filter(lambda credit: credit.subject is session_subject, attendee.credits), None)
    return DetailedAttendee(attendee.id, attendee.firstname, attendee.lastname, attendance, AvailableCredits(attendee_credits.subject.value, attendee_credits.value) if attendee_credits else None)
