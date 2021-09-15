import sqlite3

import immobilus  # noqa
import pytest

from event.event_store import StoreLocator
from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository, \
    MemoryClassRoomReadRepository
from infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository, \
    MemoryClientReadRepository
from infrastructure.repository.memory.memory_session_repository import MemorySessionRepository, \
    MemorySessionReadRepository
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


@pytest.fixture(autouse=True)
def memory_repositories():
    classroom_repository = MemoryClassroomRepository()
    client_repository = MemoryClientRepository()
    session_repository = MemorySessionRepository()
    RepositoryProvider.write_repositories = Repositories({
        "classroom": classroom_repository,
        "client": client_repository,
        "session": session_repository
    })
    RepositoryProvider.read_repositories = Repositories({
        "classroom": MemoryClassRoomReadRepository(classroom_repository),
        "client": MemoryClientReadRepository(client_repository),
        "session": MemorySessionReadRepository(session_repository),
    })
