from fastapi.testclient import TestClient

from event.event_store import StoreLocator
from infrastructure.event.sqlite.sqlite_event_store import SQLiteEventStore
from main import app
from tests.builders.builders_for_test import ClassroomJsonBuilderForTest

client = TestClient(app)


def test_post_classroom(database):
    StoreLocator.store = SQLiteEventStore(database)
    response = client.post("/classrooms", json=ClassroomJsonBuilderForTest().build())

    assert response.status_code == 201
    assert response.headers["Location"] == f"/classrooms/{response.json()['id']}"
