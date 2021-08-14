from datetime import datetime

from immobilus import immobilus

from domain.classroom.duration import TimeUnit
from domain.classroom.classroom_creation_command_handler import ClassroomCreationCommandHandler, ClassroomCreated
from domain.commands import ClassroomCreationCommand
from event.event_store import StoreLocator
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClientContextBuilderForTest
from web.schema.classroom_schemas import Duration


@immobilus("2020-04-03 10:24:15.230")
def test_classroom_creation_event_is_stored(memory_event_store):
    classroom_created: ClassroomCreated = ClassroomCreationCommandHandler().execute(
        ClassroomCreationCommand(name="classroom", position=2, start_date=datetime(2020, 5, 7, 11, 0),
                                 duration=Duration.parse_obj({"duration": 1, "unit": "HOUR"})))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClassroomCreated"
    assert events[0].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000)
    assert events[0].payload == {
        "id": classroom_created.root_id,
        "name": "classroom", "position": 2,
        "duration": {
            "duration": 1,
            "time_unit": TimeUnit.HOUR
        },
        "schedule": {
            "start": datetime(2020, 5, 7, 11, 0),
            "stop": None
        },
        "attendees": []
    }


@immobilus("2019-05-07 08:24:15.230")
def test_classroom_creation_with_attendees_event_is_stored(memory_event_store):
    client_repository, clients = ClientContextBuilderForTest().with_clients(2).persist(
        RepositoryProvider.write_repositories.client).build()

    classroom_created: ClassroomCreated = ClassroomCreationCommandHandler().execute(
        ClassroomCreationCommand(name="classroom", position=2, start_date=datetime(2019, 6, 7, 11, 0),
                                 duration=Duration.parse_obj({"duration": 1, "unit": "HOUR"}),
                                 attendees=[clients[0].id, clients[1].id]))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClassroomCreated"
    assert events[0].timestamp == datetime(2019, 5, 7, 8, 24, 15, 230000)
    assert events[0].payload == {
        "id": classroom_created.root_id,
        "name": "classroom", "position": 2,
        "duration": {
            "duration": 1,
            "time_unit": TimeUnit.HOUR
        },
        "schedule": {
            "start": datetime(2019, 6, 7, 11, 0),
            "stop": None
        },
        "attendees": [
            {"id": clients[0].id},
            {"id": clients[1].id}
        ]
    }
