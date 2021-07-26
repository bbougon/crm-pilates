from fastapi.testclient import TestClient

from event.event_store import StoreLocator
from infrastructure.event.sqlite.sqlite_event_store import SQLiteEventStore
from main import app
from tests.builders.builders_for_test import ClientJsonBuilderForTest

client = TestClient(app)


def test_post_client(database):
    StoreLocator.store = SQLiteEventStore(database)

    response = client.post("/clients", json=ClientJsonBuilderForTest().build())

    assert response.status_code == 201
    assert response.headers["Location"] == f"/clients/{response.json()['id']}"
