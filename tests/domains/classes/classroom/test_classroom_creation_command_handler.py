from datetime import datetime
from typing import Tuple

import pytz
from immobilus import immobilus

from command.command_handler import Status
from domains.classes.classroom.classroom_creation_command_handler import ClassroomCreationCommandHandler, ClassroomCreated
from domains.classes.commands import ClassroomCreationCommand
from event.event_store import StoreLocator
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClientContextBuilderForTest
from web.schema.classroom_schemas import Duration


@immobilus("2020-04-03 10:24:15.230")
def test_classroom_creation_event_is_stored(memory_event_store):
    result: Tuple[ClassroomCreated, Status] = ClassroomCreationCommandHandler().execute(
        ClassroomCreationCommand(name="classroom", position=2, _start_date=datetime(2020, 5, 7, 11, 0),
                                 duration=Duration.parse_obj({"duration": 1, "unit": "HOUR"})))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClassroomCreated"
    assert events[0].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc)
    assert events[0].payload == {
        "id": result[0].root_id,
        "name": "classroom", "position": 2,
        "duration": {
            "duration": 60,
            "time_unit": "MINUTE"
        },
        "schedule": {
            "start": datetime(2020, 5, 7, 11, 0).astimezone(pytz.utc),
            "stop": datetime(2020, 5, 7, 12, 0).astimezone(pytz.utc)
        },
        "attendees": []
    }


@immobilus("2019-05-07 08:24:15.230")
def test_classroom_creation_with_attendees_event_is_stored(memory_event_store):
    client_repository, clients = ClientContextBuilderForTest().with_clients(2).persist(
        RepositoryProvider.write_repositories.client).build()

    result: Tuple[ClassroomCreated, Status] = ClassroomCreationCommandHandler().execute(
        ClassroomCreationCommand(name="classroom", position=2, _start_date=datetime(2019, 6, 7, 11, 0),
                                 duration=Duration.parse_obj({"duration": 1, "unit": "HOUR"}),
                                 attendees=[clients[0]._id, clients[1]._id]))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClassroomCreated"
    assert events[0].timestamp == datetime(2019, 5, 7, 8, 24, 15, 230000, tzinfo=pytz.utc)
    assert events[0].payload == {
        "id": result[0].root_id,
        "name": "classroom", "position": 2,
        "duration": {
            "duration": 60,
            "time_unit": "MINUTE"
        },
        "schedule": {
            "start": datetime(2019, 6, 7, 11, 0).astimezone(pytz.utc),
            "stop": datetime(2019, 6, 7, 12, 0).astimezone(pytz.utc)
        },
        "attendees": [
            {"id": clients[0]._id},
            {"id": clients[1]._id}
        ]
    }
