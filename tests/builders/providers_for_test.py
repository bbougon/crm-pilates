from __future__ import annotations

from abc import abstractmethod

from crm_pilates.command.command_bus import CommandBus
from crm_pilates.domain.classroom.classroom_repository import ClassroomRepository
from crm_pilates.domain.client.client_repository import ClientRepository
from crm_pilates.infrastructure.command_bus_provider import CommandBusProvider, command_handlers, saga_handlers
from crm_pilates.infrastructure.repositories import Repositories
from crm_pilates.infrastructure.repository.memory.memory_attendee_repository import MemoryAttendeeRepository
from crm_pilates.infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository
from crm_pilates.infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository
from crm_pilates.infrastructure.repository.memory.memory_session_repository import MemorySessionRepository
from crm_pilates.infrastructure.repository_provider import RepositoryProvider


class ProviderForTest:

    @abstractmethod
    def provide(self):
        ...


class CommandBusProviderForTest(ProviderForTest):

    def __init__(self) -> None:
        super().__init__()
        self.handlers = {}

    def provide(self):
        CommandBusProvider.command_bus = CommandBus(command_handlers, saga_handlers)
        return CommandBusProvider


class RepositoryProviderForTest(ProviderForTest):

    def __init__(self) -> None:
        super().__init__()
        client_repository = MemoryClientRepository()
        self.repositories = {
            "classroom": MemoryClassroomRepository(),
            "client": client_repository,
            "session": MemorySessionRepository(),
            "attendee": MemoryAttendeeRepository(client_repository)
        }

    def provide(self):
        RepositoryProvider.write_repositories = Repositories(self.repositories)
        return RepositoryProvider

    def for_classroom(self, classroom_repository: ClassroomRepository = None) -> RepositoryProviderForTest:
        self.repositories["classroom"] = classroom_repository or MemoryClassroomRepository()
        return self

    def for_client(self, client_repository: ClientRepository = None):
        self.repositories["client"] = client_repository or MemoryClientRepository()
        self.repositories["attendee"] = MemoryAttendeeRepository(client_repository) or MemoryAttendeeRepository(MemoryClientRepository())
        return self
