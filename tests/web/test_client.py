from fastapi import Response

from infrastructure.command_bus_provider import CommandBusProvider
from infrastructure.repository.memory.memory_client_repository import MemoryClientRepository
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClientJsonBuilderForTest
from web.api.client import create_client
from web.schema.client_creation import ClientCreation


def test_client_creation(command_bus):
    client = ClientJsonBuilderForTest().build()
    RepositoryProvider.write_repositories.client = MemoryClientRepository()

    response = create_client(ClientCreation.parse_obj(client), Response(), CommandBusProvider)

    assert response["firstname"] == client["firstname"]
    assert response["lastname"] == client["lastname"]
    assert response["id"]
    assert RepositoryProvider.write_repositories.client.get_by_id(response["id"])
