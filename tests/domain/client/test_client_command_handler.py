from datetime import datetime
from typing import Tuple

import pytz
from immobilus import immobilus

from command.command_handler import Status
from domain.classroom.classroom_type import ClassroomType
from domain.client.client_command_handler import ClientCreated, ClientCreationCommandHandler
from domain.commands import ClientCreationCommand, ClientCredits
from event.event_store import StoreLocator


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
        ClientCreationCommand(firstname="John", lastname="Doe", credits=ClientCredits(2, ClassroomType.MAT)))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClientCreated"
    assert events[0].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc)
    assert events[0].payload == {
        "id": result[0].root_id,
        "firstname": "John",
        "lastname": "Doe",
        "credits": {"value": 2, "type": "MAT"}
    }
