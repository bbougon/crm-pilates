from fastapi import Response

from domain.client.client import Client
from infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClientJsonBuilderForTest, ClientBuilderForTest
from tests.builders.providers_for_test import CommandBusProviderForTest
from web.api.clients import create_client, get_clients
from web.schema.client_creation import ClientCreation


def test_client_creation():
    client = ClientJsonBuilderForTest().build()
    RepositoryProvider.write_repositories.client = MemoryClientRepository()

    response = create_client(ClientCreation.parse_obj(client), Response(), CommandBusProviderForTest().provide())

    assert response["firstname"] == client["firstname"]
    assert response["lastname"] == client["lastname"]
    assert response["id"]
    assert RepositoryProvider.write_repositories.client.get_by_id(response["id"])


def test_get_clients_should_return_all_clients(memory_repositories):
    first_client = ClientBuilderForTest().build()
    second_client = ClientBuilderForTest().build()
    RepositoryProvider.write_repositories.client.persist(first_client)
    RepositoryProvider.write_repositories.client.persist(second_client)

    response = get_clients()

    assert len(response) == 2
    assert response_contains_client(response, first_client)
    assert response_contains_client(response, second_client)


def response_contains_client(response, client: Client):
    expected_client = {
        "lastname": client.lastname,
        "firstname": client.firstname,
        "id": client.id
    }

    return expected_client in response
