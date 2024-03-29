from datetime import datetime

import pytz
from immobilus import immobilus

from crm_pilates.domain.attending.session_checkin_saga_handler import (
    SessionCheckinSagaHandler,
    SessionCheckedIn,
)
from crm_pilates.domain.sagas import SessionCheckinSaga
from crm_pilates.event.event_store import StoreLocator
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.asserters.event_asserter import EventAsserter
from tests.builders.builders_for_test import (
    ClientContextBuilderForTest,
    ClassroomContextBuilderForTest,
    ClassroomBuilderForTest,
    SessionContextBuilderForTest,
    ClientBuilderForTest,
)
from tests.builders.providers_for_test import CommandBusProviderForTest


@immobilus("2020-04-03 10:24:15.230")
def test_session_checkin_event_is_stored(memory_event_store):
    client_repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(2)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest()
            .starting_at(datetime(2020, 4, 3, 11, 0))
            .with_attendee(clients[0].id)
            .with_attendee(clients[1].id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom = classrooms[0]

    session_result: SessionCheckedIn = SessionCheckinSagaHandler(
        CommandBusProviderForTest().provide().command_bus
    ).execute(
        SessionCheckinSaga(
            datetime(2020, 4, 3, 11, 0, tzinfo=pytz.utc), classroom.id, clients[1].id
        )
    )

    events = StoreLocator.store.get_all()
    assert len(events) == 3
    assert events[0].type == "ConfirmedSessionEvent"
    assert events[1].type == "SessionCheckedIn"
    assert events[1].timestamp == datetime(
        2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc
    )
    EventAsserter.assert_session_checkin(
        events[1].payload, session_result.root_id, clients[1].id, "CHECKED_IN"
    )


@immobilus("2020-08-03 10:24:15.230")
def test_session_checkin_on_already_confirmed_session(memory_event_store):
    client_repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(2)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest()
            .starting_at(datetime(2020, 8, 3, 11, 0))
            .with_attendee(clients[0].id)
            .with_attendee(clients[1].id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom = classrooms[0]
    SessionContextBuilderForTest().with_classroom(classroom).checkin(clients[0].id).at(
        datetime(2020, 8, 3, 11, 0)
    ).persist(RepositoryProvider.write_repositories.session).build()

    session_result: SessionCheckedIn = SessionCheckinSagaHandler(
        CommandBusProviderForTest().provide().command_bus
    ).execute(
        SessionCheckinSaga(
            datetime(2020, 8, 3, 11, 0, tzinfo=pytz.utc), classroom.id, clients[1].id
        )
    )

    events = StoreLocator.store.get_all()
    assert len(events) == 2
    assert events[0].type == "SessionCheckedIn"
    EventAsserter.assert_session_checkin(
        events[0].payload, session_result.root_id, clients[1].id, "CHECKED_IN"
    )


def test_should_decrease_client_credits_on_checkin(memory_event_store):
    client_repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(1)
        .with_client(ClientBuilderForTest().with_mat_credit(10).build())
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    client = clients[1]
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest()
            .starting_at(datetime(2020, 8, 3, 11, 0))
            .with_attendee(clients[0].id)
            .with_attendee(client.id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom = classrooms[0]

    SessionCheckinSagaHandler(
        CommandBusProviderForTest().provide().command_bus
    ).execute(
        SessionCheckinSaga(
            datetime(2020, 8, 3, 11, 0, tzinfo=pytz.utc), classroom.id, client.id
        )
    )

    assert client.credits[0].value == 9
