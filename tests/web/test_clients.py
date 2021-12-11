import uuid
from http import HTTPStatus

import pytest
from fastapi import Response, HTTPException

from domain.classroom.classroom_type import ClassroomSubject
from domain.client.client import Client
from infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClientJsonBuilderForTest, ClientBuilderForTest, CreditsJsonBuilderForTest
from tests.builders.providers_for_test import CommandBusProviderForTest
from web.api.clients import create_client, get_clients, update_client
from web.schema.client_schemas import ClientCreation, ClientPatch


def test_client_creation():
    client = ClientJsonBuilderForTest().build()
    RepositoryProvider.write_repositories.client = MemoryClientRepository()

    response = create_client(ClientCreation.parse_obj(client), Response(), CommandBusProviderForTest().provide())

    assert response["firstname"] == client["firstname"]
    assert response["lastname"] == client["lastname"]
    assert response["id"]
    assert RepositoryProvider.write_repositories.client.get_by_id(response["id"])


def test_should_create_client_with_credits_for_mat_and_machine():
    client = ClientJsonBuilderForTest()\
        .with_credits(5, ClassroomSubject.MAT)\
        .with_credits(10, ClassroomSubject.MACHINE_DUO)\
        .with_credits(8, ClassroomSubject.MACHINE_TRIO)\
        .with_credits(9, ClassroomSubject.MACHINE_PRIVATE)\
        .build()
    RepositoryProvider.write_repositories.client = MemoryClientRepository()

    response = create_client(ClientCreation.parse_obj(client), Response(), CommandBusProviderForTest().provide())

    assert response["credits"] == [
        {"value": 5, "subject": "MAT"},
        {"value": 10, "subject": "MACHINE_DUO"},
        {"value": 8, "subject": "MACHINE_TRIO"},
        {"value": 9, "subject": "MACHINE_PRIVATE"}
    ]


def test_get_clients_should_return_all_clients(memory_repositories):
    first_client = ClientBuilderForTest().build()
    second_client = ClientBuilderForTest().build()
    RepositoryProvider.write_repositories.client.persist(first_client)
    RepositoryProvider.write_repositories.client.persist(second_client)

    response = get_clients()

    assert len(response) == 2
    assert response_contains_client(response, first_client)
    assert response_contains_client(response, second_client)


def test_should_add_credits_to_client(memory_repositories):
    client: Client = ClientBuilderForTest().with_credit(2, ClassroomSubject.MAT).build()
    RepositoryProvider.write_repositories.client.persist(client)

    update_client(client.id, ClientPatch.parse_obj(CreditsJsonBuilderForTest().mat(2).machine_duo(10).build()), CommandBusProviderForTest().provide())

    assert len(client.credits) == 2
    assert client.credits[0].value == 2
    assert client.credits[1].value == 10
    assert client.credits[1].subject == ClassroomSubject.MACHINE_DUO


def test_should_return_an_error_when_client_not_found():
    with pytest.raises(HTTPException) as e:
        uuid_ = uuid.uuid4()
        update_client(uuid_, ClientPatch.parse_obj(CreditsJsonBuilderForTest().mat(2).machine_duo(10).build()), CommandBusProviderForTest().provide())

    assert e.value.detail == f"The client with id '{uuid_}' has not been found"
    assert e.value.status_code == HTTPStatus.NOT_FOUND


def response_contains_client(response, client: Client):
    expected_client = {
        "lastname": client.lastname,
        "firstname": client.firstname,
        "id": client.id
    }

    return expected_client in response
