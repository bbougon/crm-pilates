from datetime import datetime
from typing import Tuple

from immobilus import immobilus

from command.command_handler import Status
from domain.classroom.session_checkin_saga_handler import SessionCheckinSagaHandler, SessionCheckedIn
from domain.sagas import SessionCheckinSaga
from event.event_store import StoreLocator
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClientContextBuilderForTest, ClassroomContextBuilderForTest, \
    ClassroomBuilderForTest, SessionContextBuilderForTest
from tests.builders.providers_for_test import CommandBusProviderForTest


@immobilus("2020-04-03 10:24:15.230")
def test_session_checkin_event_is_stored(memory_event_store):
    client_repository, clients = ClientContextBuilderForTest().with_clients(2).persist(
        RepositoryProvider.write_repositories.client).build()
    repository, classrooms = ClassroomContextBuilderForTest().with_classroom(
        ClassroomBuilderForTest().starting_at(datetime(2020, 4, 3, 11, 0)).with_attendee(clients[0].id).with_attendee(
            clients[1].id)).persist(
        RepositoryProvider.write_repositories.classroom).build()
    classroom = classrooms[0]

    session_result: Tuple[SessionCheckedIn, Status] = SessionCheckinSagaHandler(CommandBusProviderForTest().provide().command_bus).execute(
        SessionCheckinSaga(classroom.id, datetime(2020, 4, 3, 11, 0), clients[1].id))

    result = session_result[0]
    assert session_result[1] == Status.CREATED
    events = StoreLocator.store.get_all()
    assert len(events) == 2
    assert events[0].type == "ConfirmedSessionEvent"
    assert events[1].type == "SessionCheckedIn"
    assert events[1].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000)
    assert events[1].payload == {
        "id": result.root_id,
        "classroom_id": classroom.id,
        "name": result.name,
        "position": result.position,
        "schedule": {
            "start": datetime(2020, 4, 3, 11, 0),
            "stop": datetime(2020, 4, 3, 12, 0)
        },
        "attendees": [
            {
                "id": clients[0].id,
                "attendance": "REGISTERED"
            },
            {
                "id": clients[1].id,
                "attendance": "CHECKED_IN"
            }
        ]
    }


@immobilus("2020-08-03 10:24:15.230")
def test_session_checkin_on_already_confirmed_session(memory_event_store):
    client_repository, clients = ClientContextBuilderForTest().with_clients(2).persist(
        RepositoryProvider.write_repositories.client).build()
    repository, classrooms = ClassroomContextBuilderForTest().with_classroom(
        ClassroomBuilderForTest().starting_at(datetime(2020, 8, 3, 11, 0)).with_attendee(clients[0].id).with_attendee(
            clients[1].id)).persist(
        RepositoryProvider.write_repositories.classroom).build()
    classroom = classrooms[0]
    SessionContextBuilderForTest().with_classroom(classroom).checkin(clients[0].id).at(datetime(2020, 8, 3, 11, 0)).persist(RepositoryProvider.write_repositories.session).build()

    session_result: Tuple[SessionCheckedIn, Status] = SessionCheckinSagaHandler(CommandBusProviderForTest().provide().command_bus).execute(
        SessionCheckinSaga(classroom.id, datetime(2020, 8, 3, 11, 0), clients[1].id))

    result = session_result[0]
    assert session_result[1] == Status.UPDATED
    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "SessionCheckedIn"
    assert events[0].payload == {
        "id": result.root_id,
        "classroom_id": classroom.id,
        "name": result.name,
        "position": result.position,
        "schedule": {
            "start": datetime(2020, 8, 3, 11, 0),
            "stop": datetime(2020, 8, 3, 12, 0)
        },
        "attendees": [
            {
                "id": clients[0].id,
                "attendance": "CHECKED_IN"
            },
            {
                "id": clients[1].id,
                "attendance": "CHECKED_IN"
            }
        ]
    }
