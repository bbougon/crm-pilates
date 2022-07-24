import uuid

from fastapi import status, Response
from fastapi.testclient import TestClient
from mock.mock import ANY

from crm_pilates.domain.classroom.classroom_type import ClassroomSubject
from crm_pilates.domain.client.client import Client
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from crm_pilates.main import app
from tests.builders.builders_for_test import ClientJsonBuilderForTest, ClientContextBuilderForTest, ClientBuilderForTest

http_client = TestClient(app)


def test_should_create_client(persisted_event_store):
    client_builder = ClientJsonBuilderForTest()
    response = http_client.post("/clients", json=client_builder.build())

    assert response.status_code == 201
    assert response.headers["Location"] == f"/clients/{response.json()['id']}"
    assert response.json() == {
        "credits": None,
        "firstname": client_builder.firstname,
        "lastname": client_builder.lastname,
        "id": ANY
    }


def test_should_create_client_with_credits(persisted_event_store):
    client_builder = ClientJsonBuilderForTest().with_credits(2, ClassroomSubject.MACHINE_DUO)

    response = http_client.post("/clients", json=client_builder.build())

    assert response.status_code == 201
    assert response.headers["Location"] == f"/clients/{response.json()['id']}"
    assert response.json() == {
        "firstname": client_builder.firstname,
        "lastname": client_builder.lastname,
        "id": ANY,
        "credits": [
            {"value": 2, "subject": "MACHINE_DUO"}
        ]
    }


def test_should_not_create_client_with_empty_lastname_or_firstname(persisted_event_store):
    response = http_client.post("/clients", json={"firstname": "", "lastname": ""})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': [{'loc': ['body', 'firstname'],
                                           'msg': 'You must provide the client firstname',
                                           'type': 'value_error'},
                                          {'loc': ['body', 'lastname'],
                                           'msg': 'You must provide the client lastname',
                                           'type': 'value_error'}]}


def test_should_not_accept_negative_credits():
    client_builder = ClientJsonBuilderForTest().with_credits(-1, ClassroomSubject.MACHINE_DUO)

    response = http_client.post("/clients", json=client_builder.build())

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': [{'loc': ['body', 'credits', 0, 'value'],
                                           'msg': "Credits cannot be null or negative, please provide a positive credit.",
                                           'type': 'value_error'}]}


def test_get_client():
    repository, clients = ClientContextBuilderForTest().with_client(ClientBuilderForTest().with_mat_credit(2).with_machine_duo_credit(-1).build()).persist(
        RepositoryProvider.write_repositories.client).build()

    response: Response = http_client.get(f"/clients/{clients[0]._id}")

    client: Client = clients[0]
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "credits": [{'subject': 'MAT', 'value': 2}, {'subject': 'MACHINE_DUO', 'value': -1}],
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
    ClientContextBuilderForTest().with_client(ClientBuilderForTest().with_lastname("AA").with_credit(2, ClassroomSubject.MACHINE_TRIO).build()).with_clients(2).persist(RepositoryProvider.write_repositories.client).build()

    response: Response = http_client.get("/clients")

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert len(payload) == 3
    assert payload[0]["credits"][0]["value"] == 2
    assert payload[0]["credits"][0]["subject"] == "MACHINE_TRIO"


def test_should_add_credits_to_client():
    repository, clients = ClientContextBuilderForTest().with_client(
        ClientBuilderForTest().with_credit(2, ClassroomSubject.MACHINE_TRIO).build()).persist(
        RepositoryProvider.write_repositories.client).build()
    client_to_update: Client = clients[0]

    response: Response = http_client.post(f"clients/{str(client_to_update.id)}/credits", json=[{"value": 2, "subject": "MACHINE_TRIO"}, {"value": 10, "subject": "MAT"}])

    assert response.status_code == status.HTTP_200_OK
