from typing import List
from uuid import UUID

from crm_pilates.domain.classroom.attendee import Attendee
from crm_pilates.domain.classroom.attendee_repository import AttendeeRepository
from crm_pilates.domain.client.client import Client
from crm_pilates.domain.client.client_repository import ClientRepository
from crm_pilates.domain.repository import AggregateRoot
from crm_pilates.infrastructure.repository.memory.memory_repository import (
    MemoryRepository,
)


class MemoryAttendeeRepository(AttendeeRepository, MemoryRepository):
    def __init__(self, repository: ClientRepository) -> None:
        super().__init__()
        self.__repository = repository

    def persist(self, entity: AggregateRoot):
        raise NotImplementedError

    def get_all(self) -> List:
        yield list(
            map(
                lambda client: self.__map_to_attendee(client),
                self.__repository.get_all(),
            )
        )

    def get_by_id(self, id: UUID):
        return self.__map_to_attendee(self.__repository.get_by_id(id))

    def __map_to_attendee(self, client: Client):
        return Attendee.create(client.id)
