from __future__ import annotations

from abc import abstractmethod

from command.command_bus import CommandBus
from domains.classes.classroom.classroom_repository import ClassroomRepository
from domains.classes.client.client_repository import ClientRepository
from infrastructure.command_bus_provider import CommandBusProvider, command_handlers, saga_handlers
from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository
from infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository
from infrastructure.repository.memory.memory_session_repository import MemorySessionRepository
from infrastructure.repository_provider import RepositoryProvider


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
        self.repositories = {
            "classroom": MemoryClassroomRepository(),
            "client": MemoryClientRepository(),
            "session": MemorySessionRepository()
        }

    def provide(self):
        RepositoryProvider.write_repositories = Repositories(self.repositories)
        return RepositoryProvider

    def for_classroom(self, classroom_repository: ClassroomRepository = None) -> RepositoryProviderForTest:
        self.repositories["classroom"] = classroom_repository or MemoryClassroomRepository()
        return self

    def for_client(self, client_repository: ClientRepository = None):
        self.repositories["client"] = client_repository or MemoryClientRepository()
        return self
