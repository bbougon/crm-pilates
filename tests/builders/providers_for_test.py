from __future__ import annotations

from abc import abstractmethod

from command.command_bus import CommandBus
from domain.classroom import classroom_repository
from domain.classroom.classroom_command_handler import ClassroomCreationCommandHandler
from domain.classroom.classroom_repository import ClassroomRepository
from domain.client.client_repository import ClientRepository
from domain.commands import ClassroomCreationCommand
from infrastructure.command_bus_provider import CommandBusProvider
from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repository import MemoryClassroomRepository
from infrastructure.repository.memory.memory_client_repository import MemoryClientRepository
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
        CommandBusProvider.command_bus = CommandBus(self.handlers)
        return CommandBusProvider

    def for_classroom(self) -> CommandBusProviderForTest:
        self.handlers[ClassroomCreationCommand.__name__] = ClassroomCreationCommandHandler()
        return self


class RepositoryProviderForTest(ProviderForTest):

    def __init__(self) -> None:
        super().__init__()
        self.repositories = {}

    def provide(self):
        RepositoryProvider.repositories = Repositories(self.repositories)
        return RepositoryProvider

    def for_classroom(self, classroom_repository: ClassroomRepository = None) -> RepositoryProviderForTest:
        self.repositories["classroom"] = classroom_repository or MemoryClassroomRepository()
        return self

    def for_client(self, client_repository: ClientRepository = None):
        self.repositories["client"] = client_repository or MemoryClientRepository()
        return self
