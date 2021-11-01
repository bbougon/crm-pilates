import uuid

from fastapi import status, Response
from fastapi.testclient import TestClient

from domain.client.client import Client
from infrastructure.repository_provider import RepositoryProvider
from main import app
from tests.builders.builders_for_test import ClientJsonBuilderForTest, ClientContextBuilderForTest

http_client = TestClient(app)


def test_should_create_client(sqlite_event_store):
    response = http_client.post("/clients", json=ClientJsonBuilderForTest().build())

    assert response.status_code == 201
    assert response.headers["Location"] == f"/clients/{response.json()['id']}"


def test_should_not_create_client_with_empty_lastname_or_firstname(sqlite_event_store):
    response = http_client.post("/clients", json={"firstname": "", "lastname": ""})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': [{'loc': ['body', 'firstname'],
                                           'msg': 'You must provide the client firstname',
                                           'type': 'value_error'},
                                          {'loc': ['body', 'lastname'],
                                           'msg': 'You must provide the client lastname',
                                           'type': 'value_error'}]}


def test_get_client():
    repository, clients = ClientContextBuilderForTest().with_one_client().persist(
        RepositoryProvider.write_repositories.client).build()

    response: Response = http_client.get(f"/clients/{clients[0]._id}")

    client: Client = clients[0]
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(client._id),
        "firstname": client.firstname,
        "lastname": client.lastname
    }


def test_client_is_not_found():
    unknown_uuid = uuid.uuid4()

    response: Response = http_client.get(f"/clients/{unknown_uuid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Client with id '{unknown_uuid}' not found"


def test_get_clients_should_return_all_clients():
    repository, clients = ClientContextBuilderForTest().with_clients(3).persist(
        RepositoryProvider.write_repositories.client).build()

    response: Response = http_client.get(f"/clients/{clients[0]._id}")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3
