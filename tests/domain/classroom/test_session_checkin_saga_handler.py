from datetime import datetime

from immobilus import immobilus

from domain.classroom.session_checkin_saga_handler import SessionCheckinSagaHandler, SessionCheckedIn
from domain.sagas import SessionCheckinSaga
from event.event_store import StoreLocator
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import ClientContextBuilderForTest, ClassroomContextBuilderForTest, \
    ClassroomBuilderForTest
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

    session: SessionCheckedIn = SessionCheckinSagaHandler(CommandBusProviderForTest().provide().command_bus).execute(
        SessionCheckinSaga(classroom.id, datetime(2020, 4, 3, 11, 0), clients[1].id))

    events = StoreLocator.store.get_all()
    assert len(events) == 2
    assert events[0].type == "ConfirmedSessionEvent"
    assert events[1].type == "SessionCheckedIn"
    assert events[1].timestamp == datetime(2020, 4, 3, 10, 24, 15, 230000)
    assert events[1].payload == {
        "id": session.root_id,
        "classroom_id": classroom.id,
        "name": session.name,
        "position": session.position,
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
