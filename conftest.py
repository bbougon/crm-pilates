import immobilus
import sqlite3

import pytest

from command.command_bus import CommandBus
from domain.classroom.classroom_creation_command_handler import ClassroomCreationCommandHandler
from domain.classroom.classroom_patch_command_handler import ClassroomPatchCommandHandler
from domain.client.client_command_handler import ClientCreationCommandHandler
from domain.commands import ClientCreationCommand, ClassroomCreationCommand, ClassroomPatchCommand
from event.event_store import StoreLocator
from infrastructure.command_bus_provider import CommandBusProvider
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
            ClassroomPatchCommand.__name__: ClassroomPatchCommandHandler()
        }
    )
    CommandBusProvider.command_bus = command_bus