import sqlite3
from typing import Any

import immobilus  # noqa
import psycopg
import pytest

from crm_pilates import settings
from crm_pilates.domain.services import CipherServiceProvider, CipherService
from crm_pilates.event.event_bus import EventBus, EventSubscriber
from crm_pilates.event.event_store import StoreLocator
from crm_pilates.infrastructure.event.postgres.postgres_sql_event_store import (
    PostgresSQLEventStore,
)
from crm_pilates.infrastructure.event.sqlite.sqlite_event_store import SQLiteEventStore
from crm_pilates.infrastructure.event_bus_provider import EventBusProvider
from crm_pilates.infrastructure.repositories import Repositories
from crm_pilates.infrastructure.repository.memory.memory_attendee_repository import (
    MemoryAttendeeRepository,
)
from crm_pilates.infrastructure.repository.memory.memory_classroom_repositories import (
    MemoryClassroomRepository,
    MemoryClassRoomReadRepository,
)
from crm_pilates.infrastructure.repository.memory.memory_client_repositories import (
    MemoryClientRepository,
    MemoryClientReadRepository,
)
from crm_pilates.infrastructure.repository.memory.memory_session_repository import (
    MemorySessionRepository,
    MemorySessionReadRepository,
)
from crm_pilates.infrastructure.repository.memory.memory_user_repository import (
    MemoryUserRepository,
)
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from crm_pilates.app import app
from crm_pilates.web.api.authentication import authentication_service
from tests.faker.custom_authentication_service import CustomAuthenticationService
from tests.infrastructure.event.memory_event_store import MemoryEventStore
from tests.infrastructure.migration.test_migration import PILATES_TEST


def pytest_addoption(parser):
    parser.addoption("--db-type", action="store", default="sqlite")


class DummyEventBus(EventBus):
    def publish(self, event: any):
        pass

    def subscribe(self, event_subscriber: EventSubscriber):
        pass


@pytest.fixture
def persisted_event_store(request, tmpdir):
    if request.config.getoption("--db-type") == "sqlite":
        database_file = tmpdir.join("event_store.db")
        connect = sqlite3.connect(database_file)
        cursor = connect.cursor()
        cursor.execute(
            """CREATE TABLE event (id text, root_id text, type text, timestamp text, payload text)"""
        )
        connect.commit()
        connect.close()
        StoreLocator.store = SQLiteEventStore(database_file)
        yield database_file

    if request.config.getoption("--db-type") == "postgres":
        StoreLocator.store = PostgresSQLEventStore(
            "postgresql://crm-pilates-test:example@localhost:5433/crm-pilates-test"
        )
        yield
        with psycopg.connect(StoreLocator.store.connection_url) as connection:
            connection.execute("DELETE FROM event")
            connection.commit()

    EventBusProvider.event_bus = DummyEventBus()


@pytest.fixture
def create_database():
    with psycopg.connect(settings.DATABASE_URL) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS users (id text, username text, password text, config text)"""
        )
        connection.execute(
            """CREATE TABLE IF NOT EXISTS migration (id SERIAL PRIMARY KEY, timestamp_ timestamp, script_path text)"""
        )
        connection.commit()


@pytest.fixture
def clean_database(create_database):
    StoreLocator.store = PostgresSQLEventStore(
        "postgresql://crm-pilates-test:example@localhost:5433/crm-pilates-test"
    )
    yield
    with psycopg.connect(settings.DATABASE_URL) as connection:
        connection.execute("DELETE FROM event")
        connection.execute("DELETE FROM users")
        connection.execute("DELETE FROM migration")
        connection.commit()


@pytest.fixture
def drop_tables():
    yield
    with psycopg.connect(settings.DATABASE_URL) as connection:
        connection.execute("DROP TABLE users")
        connection.commit()


@pytest.fixture
def sqlite_event_store(tmpdir):
    database_file = tmpdir.join("event_store.db")
    connect = sqlite3.connect(database_file)
    cursor = connect.cursor()
    cursor.execute(
        """CREATE TABLE event (id text, root_id text, type text, timestamp text, payload text)"""
    )
    connect.commit()
    connect.close()
    StoreLocator.store = SQLiteEventStore(database_file)
    yield database_file


@pytest.fixture(autouse=True)
def memory_event_store():
    StoreLocator.store = MemoryEventStore()
    yield StoreLocator.store


@pytest.fixture
def authenticated_user():
    app.dependency_overrides[authentication_service] = CustomAuthenticationService
    yield
    app.dependency_overrides = {}


@pytest.fixture(autouse=True, scope="function")
def memory_repositories():
    classroom_repository = MemoryClassroomRepository()
    client_repository = MemoryClientRepository()
    attendee_repository = MemoryAttendeeRepository(client_repository)
    session_repository = MemorySessionRepository()
    user_repository = MemoryUserRepository()
    RepositoryProvider.write_repositories = Repositories(
        {
            "classroom": classroom_repository,
            "client": client_repository,
            "session": session_repository,
            "attendee": attendee_repository,
            "user": user_repository,
        }
    )
    RepositoryProvider.read_repositories = Repositories(
        {
            "classroom": MemoryClassRoomReadRepository(classroom_repository),
            "client": MemoryClientReadRepository(client_repository),
            "session": MemorySessionReadRepository(session_repository),
        }
    )


class DummyCipherService(CipherService):
    def decrypt(self, encrypt_content: Any) -> bytes:
        return bytes(
            encrypt_content.decode("utf-8").removeprefix("encrypted_"), "utf-8"
        )

    def encrypt(self, content: bytes) -> bytes:
        return bytes(f"encrypted_{content}", "utf-8")


@pytest.fixture(autouse=True)
def dummy_cipher():
    CipherServiceProvider.service = DummyCipherService()


@pytest.fixture
def event_bus():
    if isinstance(EventBusProvider.event_bus, DummyEventBus):
        EventBusProvider.event_bus = EventBus()


@pytest.fixture
def connection_url_arg():
    return [f"--connection-url={PILATES_TEST}"]
