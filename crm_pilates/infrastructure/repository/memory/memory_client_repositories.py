from typing import List
from uuid import UUID

from crm_pilates.domain.client.client_repository import ClientRepository
from crm_pilates.domain.repository import AggregateRoot
from crm_pilates.infrastructure.repository.memory.memory_repository import MemoryRepository


class MemoryClientRepository(ClientRepository, MemoryRepository):
    pass


class MemoryClientReadRepository(ClientRepository, MemoryRepository):

    def __init__(self, repository: ClientRepository) -> None:
        super().__init__()
        self.__repository = repository

    def persist(self, entity: AggregateRoot):
        raise NotImplementedError

    def get_by_id(self, id: UUID):
        return self.__repository.get_by_id(id)

    def get_all(self) -> List:
        return self.__repository.get_all()
