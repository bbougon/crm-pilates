from datetime import datetime
from typing import Tuple

import pytz
from immobilus import immobilus

from command.command_handler import Status
from domain.classroom.classroom_type import ClassroomType
from domain.client.client_command_handlers import ClientCreated, ClientCreationCommandHandler, \
    AddCreditsToClientCommandHandler
from domain.commands import ClientCreationCommand, ClientCredits, AddCreditsToClientCommand
from event.event_store import StoreLocator
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClientContextBuilderForTest, ClientBuilderForTest


@immobilus("2020-04-03 10:24:15.230")
def test_classroom_creation_event_is_stored(memory_event_store):
    result: Tuple[ClientCreated, Status] = ClientCreationCommandHandler().execute(
        ClientCreationCommand(firstname="John", lastname="Doe"))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClientCreated"
    assert events[0].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc)
    assert events[0].payload == {
        "id": result[0].root_id,
        "firstname": "John",
        "lastname": "Doe",
    }


@immobilus("2020-04-03 10:24:15.230")
def test_classroom_creation_event_is_stored_with_credits(memory_event_store):
    result: Tuple[ClientCreated, Status] = ClientCreationCommandHandler().execute(
        ClientCreationCommand(firstname="John", lastname="Doe", credits=[ClientCredits(2, ClassroomType.MAT)]))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClientCreated"
    assert events[0].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc)
    assert events[0].payload == {
        "id": result[0].root_id,
        "firstname": "John",
        "lastname": "Doe",
        "credits": [{"value": 2, "type": "MAT"}]
    }


def test_should_store_credits_to_client_added(memory_event_store, memory_repositories):
    client = ClientBuilderForTest().build()
    ClientContextBuilderForTest().with_client(client).persist(RepositoryProvider.write_repositories.client).build()

    AddCreditsToClientCommandHandler().execute(AddCreditsToClientCommand(client.id, [ClientCredits(5, ClassroomType.MAT), ClientCredits(10, ClassroomType.MACHINE_DUO)]))

    events = StoreLocator.store.get_all()
    assert events[0].type == "CreditsToClientAdded"
    assert events[0].payload == {
        "id": client.id,
        "credits": [
            {"value": 5, "type": ClassroomType.MAT.value},
            {"value": 10, "type": ClassroomType.MACHINE_DUO.value}
        ]
    }
