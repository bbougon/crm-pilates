from fastapi.testclient import TestClient

from event.event_store import StoreLocator
from infrastructure.event.sqlite.sqlite_event_store import SQLiteEventStore
from infrastructure.providers import repository_provider
from main import app
from tests.builders.builders_for_test import ClassroomJsonBuilderForTest, ClientContextBuilderForTest

client = TestClient(app)


def test_post_classroom(database):
    StoreLocator.store = SQLiteEventStore(database)
    response = client.post("/classrooms", json=ClassroomJsonBuilderForTest().build())

    assert response.status_code == 201
    assert response.headers["Location"] == f"/classrooms/{response.json()['id']}"


def test_post_classroom_with_attendees(database):
    StoreLocator.store = SQLiteEventStore(database)
    repository, clients = ClientContextBuilderForTest().with_one_client().persist(repository_provider().client).build()

    response = client.post("/classrooms", json=ClassroomJsonBuilderForTest().with_attendees([clients[0].id]).build())

    assert response.status_code == 201
    assert response.headers["Location"] == f"/classrooms/{response.json()['id']}"
