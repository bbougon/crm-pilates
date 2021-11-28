from typing import List
from uuid import UUID

from domain.classroom.attendee import Attendee
from domain.classroom.attendee_repository import AttendeeRepository
from domain.client.client import Client
from domain.client.client_repository import ClientRepository
from domain.repository import AggregateRoot
from infrastructure.repository.memory.memory_repository import MemoryRepository


class MemoryAttendeeRepository(AttendeeRepository, MemoryRepository):

    def __init__(self, repository: ClientRepository) -> None:
        super().__init__()
        self.__repository = repository

    def persist(self, entity: AggregateRoot):
        raise NotImplementedError

    def get_all(self) -> List:
        yield list(map(lambda client: self.__map_to_attendee(client), self.__repository.get_all()))

    def get_by_id(self, id: UUID):
        return self.__map_to_attendee(self.__repository.get_by_id(id))

    def __map_to_attendee(self, client: Client):
        return Attendee.create(client.id)
