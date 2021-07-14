from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repository import MemoryClassroomRepository
from infrastructure.repository.memory.memory_client_repository import MemoryClientRepository


class RepositoryProvider:
    repositories: Repositories


RepositoryProvider.repositories = Repositories({
    "classroom": MemoryClassroomRepository(),
    "client": MemoryClientRepository()
})
