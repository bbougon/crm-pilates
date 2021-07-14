import sqlite3

import immobilus
import pytest

from event.event_store import StoreLocator
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