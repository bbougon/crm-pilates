import uuid
from http import HTTPStatus

import pytest
from fastapi import Response, HTTPException

from crm_pilates.domain.classroom.classroom_type import ClassroomSubject
from crm_pilates.domain.client.client import Client
from crm_pilates.infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClientJsonBuilderForTest, ClientBuilderForTest, CreditsJsonBuilderForTest
from tests.builders.providers_for_test import CommandBusProviderForTest
from crm_pilates.web.api.clients import create_client, get_clients, add_credits_to_client
from crm_pilates.web.schema.client_schemas import ClientCreation, Credits


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
    first_client = ClientBuilderForTest().with_mat_credit(-1).build()
    second_client = ClientBuilderForTest().with_mat_credit(5).build()
    RepositoryProvider.write_repositories.client.persist(first_client)
    RepositoryProvider.write_repositories.client.persist(second_client)

    response = get_clients()

    assert len(response) == 2
    assert client_payload(first_client) in response
    assert client_payload(second_client) in response


def test_should_get_all_clients_sorted_by_name_and_firstname(memory_repositories):
    first_client = ClientBuilderForTest().with_lastname("bardot").with_firstname("Jean").build()
    second_client = ClientBuilderForTest().with_lastname("Debussy").with_firstname("claude").build()
    third_client = ClientBuilderForTest().with_lastname("Martin").with_firstname("Lucien").build()
    fourth_client = ClientBuilderForTest().with_lastname("BArdot").with_firstname("Brigitte").build()
    fifth_client = ClientBuilderForTest().with_lastname("Brecht").with_firstname("Bertolt").build()
    sixth_client = ClientBuilderForTest().with_lastname("Wagner").with_firstname("Alfred").build()
    RepositoryProvider.write_repositories.client.persist(first_client)
    RepositoryProvider.write_repositories.client.persist(third_client)
    RepositoryProvider.write_repositories.client.persist(fifth_client)
    RepositoryProvider.write_repositories.client.persist(sixth_client)
    RepositoryProvider.write_repositories.client.persist(fourth_client)
    RepositoryProvider.write_repositories.client.persist(second_client)

    response = get_clients()

    assert response == [
        client_payload(fourth_client),
        client_payload(first_client),
        client_payload(fifth_client),
        client_payload(second_client),
        client_payload(third_client),
        client_payload(sixth_client)
    ]


def test_should_add_credits_to_client(memory_repositories):
    client: Client = ClientBuilderForTest().with_credit(2, ClassroomSubject.MAT).build()
    RepositoryProvider.write_repositories.client.persist(client)

    add_credits_to_client(client.id, [Credits.parse_obj(CreditsJsonBuilderForTest().mat(2).build()), Credits.parse_obj(CreditsJsonBuilderForTest().machine_duo(10).build())], CommandBusProviderForTest().provide())

    assert len(client.credits) == 2
    assert client.credits[0].value == 4
    assert client.credits[1].value == 10
    assert client.credits[1].subject == ClassroomSubject.MACHINE_DUO


def test_should_return_an_error_when_client_not_found():
    with pytest.raises(HTTPException) as e:
        uuid_ = uuid.uuid4()
        add_credits_to_client(uuid_, [Credits.parse_obj(CreditsJsonBuilderForTest().mat(2).build()), Credits.parse_obj(CreditsJsonBuilderForTest().machine_duo(10).build())], CommandBusProviderForTest().provide())

    assert e.value.detail == f"The client with id '{uuid_}' has not been found"
    assert e.value.status_code == HTTPStatus.NOT_FOUND


def client_payload(client):
    expected_client = {
        "lastname": client.lastname,
        "firstname": client.firstname,
        "id": client.id,
    }
    if client.credits:
        expected_client["credits"] = list(map(lambda credit: credit_to_payload(credit), client.credits))
    return expected_client


def credit_to_payload(credits: Credits):
    return {"value": credits.value, "subject": credits.subject.value}
