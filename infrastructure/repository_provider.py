from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_attendee_repository import MemoryAttendeeRepository
from infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository, \
    MemoryClassRoomReadRepository
from infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository, MemoryClientReadRepository
from infrastructure.repository.memory.memory_session_repository import MemorySessionRepository, \
    MemorySessionReadRepository


class RepositoryProvider:
    write_repositories: Repositories
    read_repositories: Repositories


classroom_repository = MemoryClassroomRepository()
client_repository = MemoryClientRepository()
attendee_repository = MemoryAttendeeRepository(client_repository)
session_repository = MemorySessionRepository()

RepositoryProvider.write_repositories = Repositories({
    "classroom": classroom_repository,
    "client": client_repository,
    "session": session_repository,
    "attendee": attendee_repository
})

RepositoryProvider.read_repositories = Repositories({
    "classroom": MemoryClassRoomReadRepository(classroom_repository),
    "client": MemoryClientReadRepository(client_repository),
    "session": MemorySessionReadRepository(session_repository),
})
