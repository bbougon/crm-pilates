import sqlite3

import immobilus  # noqa
import psycopg
import pytest

from event.event_store import StoreLocator
from infrastructure.event.postgres.postgres_sql_event_store import PostgresSQLEventStore
from infrastructure.event.sqlite.sqlite_event_store import SQLiteEventStore
from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_attendee_repository import MemoryAttendeeRepository
from infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository, \
    MemoryClassRoomReadRepository
from infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository, \
    MemoryClientReadRepository
from infrastructure.repository.memory.memory_session_repository import MemorySessionRepository, \
    MemorySessionReadRepository
from infrastructure.repository_provider import RepositoryProvider
from tests.infrastructure.event.memory_event_store import MemoryEventStore


def pytest_addoption(parser):
    parser.addoption("--db-type", action="store", default="sqlite")


@pytest.fixture
def persisted_event_store(request, tmpdir):
    if request.config.getoption("--db-type") == "sqlite":
        database_file = tmpdir.join("event_store.db")
        connect = sqlite3.connect(database_file)
        cursor = connect.cursor()
        cursor.execute('''CREATE TABLE event (id text, root_id text, type text, timestamp text, payload text)''')
        connect.commit()
        connect.close()
        StoreLocator.store = SQLiteEventStore(database_file)
        yield database_file

    if request.config.getoption("--db-type") == "postgres":
        StoreLocator.store = PostgresSQLEventStore("postgresql://crm-pilates-test:example@localhost:5433/crm-pilates-test")
        yield
        with psycopg.connect(StoreLocator.store.connection_url) as connection:
            connection.execute("DELETE FROM event")
            connection.commit()


@pytest.fixture
def postgres_event_store():
    StoreLocator.store = PostgresSQLEventStore("postgresql://crm-pilates-test:example@localhost:5433/crm-pilates-test")
    yield
    with psycopg.connect(StoreLocator.store.connection_url) as connection:
        connection.execute("DELETE FROM event")
        connection.commit()


@pytest.fixture
def sqlite_event_store(tmpdir):
    database_file = tmpdir.join("event_store.db")
    connect = sqlite3.connect(database_file)
    cursor = connect.cursor()
    cursor.execute('''CREATE TABLE event (id text, root_id text, type text, timestamp text, payload text)''')
    connect.commit()
    connect.close()
    StoreLocator.store = SQLiteEventStore(database_file)
    yield database_file


@pytest.fixture(autouse=True)
def memory_event_store():
    StoreLocator.store = MemoryEventStore()
    yield StoreLocator.store


@pytest.fixture(autouse=True)
def memory_repositories():
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
