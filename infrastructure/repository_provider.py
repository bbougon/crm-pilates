from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repository import MemoryClassroomRepository
from infrastructure.repository.memory.memory_client_repository import MemoryClientRepository


class RepositoryProvider:
    write_repositories: Repositories


classroom_repository = MemoryClassroomRepository()
client_repository = MemoryClientRepository()

RepositoryProvider.write_repositories = Repositories({
    "classroom": classroom_repository,
    "client": client_repository
})
