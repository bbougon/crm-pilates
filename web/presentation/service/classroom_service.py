from typing import List
from uuid import UUID

from domain.classroom.classroom import Classroom
from domain.client.client import Client
from infrastructure.repository_provider import RepositoryProvider
from web.presentation.domain.detailed_classroom import DetailedClassroom


def get_detailed_classroom(id: UUID):
    classroom: Classroom = RepositoryProvider.read_repositories.classroom.get_by_id(id)
    clients: List[Client] = list(
        map(lambda attendee: RepositoryProvider.read_repositories.client.get_by_id(attendee._id), classroom._attendees))
    attendees: List[dict] = list(
        map(lambda client: {"client_id": client._id, "firstname": client.firstname, "lastname": client.lastname},
            clients))
    return DetailedClassroom(classroom, attendees)
