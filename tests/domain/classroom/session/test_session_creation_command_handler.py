from datetime import datetime
from typing import Tuple

import pytz
from immobilus import immobilus

from command.command_handler import Status
from domains.classes.classroom.session.session_creation_command_handler import SessionCreationCommandHandler, ConfirmedSessionEvent
from domains.classes.commands import SessionCreationCommand
from event.event_store import StoreLocator
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClassroomBuilderForTest, ClassroomContextBuilderForTest, \
    ClientContextBuilderForTest


@immobilus("2020-04-03 10:24:15.230")
def test_session_creation_event_is_stored(memory_event_store):
    client_repository, clients = ClientContextBuilderForTest().with_clients(2).persist(
        RepositoryProvider.write_repositories.client).build()
    repository, classrooms = ClassroomContextBuilderForTest().with_classroom(
        ClassroomBuilderForTest().starting_at(datetime(2020, 4, 3, 11, 0)).with_attendee(clients[0].id).with_attendee(
            clients[1].id)).persist(
        RepositoryProvider.write_repositories.classroom).build()
    classroom = classrooms[0]

    confirmed_session_result: Tuple[ConfirmedSessionEvent, Status] = SessionCreationCommandHandler().execute(SessionCreationCommand(
        classroom.id, datetime(2020, 4, 3, 11, 0, tzinfo=pytz.utc)))

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ConfirmedSessionEvent"
    assert events[0].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc)
    result = confirmed_session_result[0]
    assert events[0].payload == {
        "id": result.root_id,
        "classroom_id": classroom.id,
        "name": result.name,
        "position": result.position,
        "schedule": {
            "start": datetime(2020, 4, 3, 11, 0, tzinfo=pytz.utc),
            "stop": datetime(2020, 4, 3, 12, 0, tzinfo=pytz.utc)
        },
        "attendees": [
            {
                "id": clients[0].id,
                "attendance": "REGISTERED"
            },
            {
                "id": clients[1].id,
                "attendance": "REGISTERED"
            }
        ]
    }
