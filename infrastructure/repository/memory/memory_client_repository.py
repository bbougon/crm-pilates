from domain.client.client_repository import ClientRepository
from infrastructure.repository.memory.memory_repository import MemoryRepository


class MemoryClientRepository(ClientRepository, MemoryRepository):
    pass
