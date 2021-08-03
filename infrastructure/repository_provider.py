from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository, \
    MemoryClassRoomReadRepository
from infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository, MemoryClientReadRepository


class RepositoryProvider:
    write_repositories: Repositories
    read_repositories: Repositories


classroom_repository = MemoryClassroomRepository()
client_repository = MemoryClientRepository()

RepositoryProvider.write_repositories = Repositories({
    "classroom": classroom_repository,
    "client": client_repository
})

RepositoryProvider.read_repositories = Repositories({
    "classroom": MemoryClassRoomReadRepository(classroom_repository),
    "client": MemoryClientReadRepository(client_repository),
})
