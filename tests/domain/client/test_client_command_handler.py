from immobilus import immobilus

from datetime import datetime

from domain.client.client_command_handler import ClientCreated, ClientCreationCommandHandler
from domain.commands import ClientCreationCommand
from event.event_store import StoreLocator


@immobilus("2020-04-03 10:24:15.230")
def test_classroom_creation_event_is_stored(memory_event_store):
    client_created: ClientCreated = ClientCreationCommandHandler().execute(
        ClientCreationCommand(firstname="John", lastname="Doe"))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClientCreated"
    assert events[0].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000)
    assert events[0].payload == {
        "id": client_created.root_id,
        "firstname": "John",
        "lastname": "Doe",
    }
