from fastapi import Response

from infrastructure.repository.memory.memory_client_repositories import MemoryClientRepository
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClientJsonBuilderForTest
from tests.builders.providers_for_test import CommandBusProviderForTest
from web.api.client import create_client
from web.schema.client_creation import ClientCreation


def test_client_creation():
    client = ClientJsonBuilderForTest().build()
    RepositoryProvider.write_repositories.client = MemoryClientRepository()

    response = create_client(ClientCreation.parse_obj(client), Response(), CommandBusProviderForTest().provide())

    assert response["firstname"] == client["firstname"]
    assert response["lastname"] == client["lastname"]
    assert response["id"]
    assert RepositoryProvider.write_repositories.client.get_by_id(response["id"])
