import sqlite3

import immobilus  # noqa
import pytest

from command.command_bus import CommandBus
from domain.classroom.classroom_creation_command_handler import ClassroomCreationCommandHandler
from domain.classroom.classroom_patch_command_handler import ClassroomPatchCommandHandler
from domain.client.client_command_handler import ClientCreationCommandHandler
from domain.commands import ClientCreationCommand, ClassroomCreationCommand, ClassroomPatchCommand, \
    GetNextSessionsCommand
from domain.classroom.next_sessions_command_handler import NextSessionsCommandHandler
from event.event_store import StoreLocator
from infrastructure.command_bus_provider import CommandBusProvider
from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository, \
    MemoryClassRoomReadRepository
from infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository, \
    MemoryClientReadRepository
from infrastructure.repository_provider import RepositoryProvider
from tests.infrastructure.event.memory_event_store import MemoryEventStore


@pytest.fixture
def database(tmpdir):
    database_file = tmpdir.join("event_store.db")
    connect = sqlite3.connect(database_file)
    cursor = connect.cursor()
    cursor.execute('''CREATE TABLE event (id text, root_id text, type text, timestamp text, payload text)''')
    connect.commit()
    connect.close()
    return database_file


@pytest.fixture
def memory_event_store():
    StoreLocator.store = MemoryEventStore()


@pytest.fixture
def command_bus():
    command_bus = CommandBus(
        {
            ClientCreationCommand.__name__: ClientCreationCommandHandler(),
            ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(),
            ClassroomPatchCommand.__name__: ClassroomPatchCommandHandler(),
            GetNextSessionsCommand.__name__: NextSessionsCommandHandler()
        }
    )
    CommandBusProvider.command_bus = command_bus


@pytest.fixture
def memory_repositories():
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
