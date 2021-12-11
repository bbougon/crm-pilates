from datetime import datetime
from typing import Tuple

import pytz
from immobilus import immobilus

from command.command_handler import Status
from domain.classroom.classroom_type import ClassroomSubject
from domain.client.client_command_handlers import ClientCreated, ClientCreationCommandHandler, \
    AddCreditsToClientCommandHandler
from domain.commands import ClientCreationCommand, ClientCredits, AddCreditsToClientCommand
from event.event_store import StoreLocator
from infrastructure.repository_provider import RepositoryProvider
from tests.asserters.event_asserter import EventAsserter
from tests.builders.builders_for_test import ClientContextBuilderForTest, ClientBuilderForTest


@immobilus("2020-04-03 10:24:15.230")
def test_classroom_creation_event_is_stored(memory_event_store):
    result: Tuple[ClientCreated, Status] = ClientCreationCommandHandler().execute(
        ClientCreationCommand(firstname="John", lastname="Doe"))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClientCreated"
    assert events[0].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc)
    EventAsserter.assert_client_created(events[0].payload, result[0].root_id, "John", "Doe")


@immobilus("2020-04-03 10:24:15.230")
def test_classroom_creation_event_is_stored_with_credits(memory_event_store):
    result: Tuple[ClientCreated, Status] = ClientCreationCommandHandler().execute(
        ClientCreationCommand(firstname="John", lastname="Doe", credits=[ClientCredits(2, ClassroomSubject.MAT)]))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClientCreated"
    assert events[0].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc)
    EventAsserter.assert_client_created(events[0].payload, result[0].root_id, "John", "Doe", [{"value": 2, "subject": "MAT"}])


def test_should_store_credits_to_client_added(memory_event_store, memory_repositories):
    client = ClientBuilderForTest().build()
    ClientContextBuilderForTest().with_client(client).persist(RepositoryProvider.write_repositories.client).build()

    AddCreditsToClientCommandHandler().execute(AddCreditsToClientCommand(client.id, [ClientCredits(5, ClassroomSubject.MAT), ClientCredits(10, ClassroomSubject.MACHINE_DUO)]))

    events = StoreLocator.store.get_all()
    assert events[0].type == "ClientCreditsUpdated"
    EventAsserter.assert_client_credits_updated(events[0].payload, client.id, [
        {"value": 5, "subject": ClassroomSubject.MAT.value},
        {"value": 10, "subject": ClassroomSubject.MACHINE_DUO.value}
    ])
