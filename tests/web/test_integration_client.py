import uuid

from fastapi import status, Response
from fastapi.testclient import TestClient

from domain.client.client import Client
from event.event_store import StoreLocator
from infrastructure.event.sqlite.sqlite_event_store import SQLiteEventStore
from infrastructure.repository_provider import RepositoryProvider
from main import app
from tests.builders.builders_for_test import ClientJsonBuilderForTest, ClientContextBuilderForTest

http_client = TestClient(app)


def test_post_client(database):
    StoreLocator.store = SQLiteEventStore(database)

    response = http_client.post("/clients", json=ClientJsonBuilderForTest().build())

    assert response.status_code == 201
    assert response.headers["Location"] == f"/clients/{response.json()['id']}"


def test_get_client():
    repository, clients = ClientContextBuilderForTest().with_one_client().persist(
        RepositoryProvider.repositories.client).build()

    response: Response = http_client.get(f"/clients/{clients[0].id}")

    client: Client = clients[0]
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(client.id),
        "firstname": client.firstname,
        "lastname": client.lastname
    }


def test_client_is_not_found():
    unknown_uuid = uuid.uuid4()

    response: Response = http_client.get(f"/clients/{unknown_uuid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Client with id '{unknown_uuid}' not found"
