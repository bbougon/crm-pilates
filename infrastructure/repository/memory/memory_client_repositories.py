from uuid import UUID

from domain.client.client_repository import ClientRepository
from domain.repository import AggregateRoot
from infrastructure.repository.memory.memory_repository import MemoryRepository


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
