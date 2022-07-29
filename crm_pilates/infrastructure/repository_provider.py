from crm_pilates import settings
from crm_pilates.infrastructure.repositories import Repositories
from crm_pilates.infrastructure.repository.memory.memory_attendee_repository import MemoryAttendeeRepository
from crm_pilates.infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository, \
    MemoryClassRoomReadRepository
from crm_pilates.infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository, MemoryClientReadRepository
from crm_pilates.infrastructure.repository.memory.memory_session_repository import MemorySessionRepository, \
    MemorySessionReadRepository
from crm_pilates.infrastructure.repository.postgres.user_repository import PostgresUserRepository


class RepositoryProvider:
    write_repositories: Repositories
    read_repositories: Repositories


classroom_repository = MemoryClassroomRepository()
client_repository = MemoryClientRepository()
attendee_repository = MemoryAttendeeRepository(client_repository)
session_repository = MemorySessionRepository()
user_repository = PostgresUserRepository(settings.DATABASE_URL)

RepositoryProvider.write_repositories = Repositories({
    "classroom": classroom_repository,
    "client": client_repository,
    "session": session_repository,
    "attendee": attendee_repository,
    "user": user_repository
})

RepositoryProvider.read_repositories = Repositories({
    "classroom": MemoryClassRoomReadRepository(classroom_repository),
    "client": MemoryClientReadRepository(client_repository),
    "session": MemorySessionReadRepository(session_repository),
})
