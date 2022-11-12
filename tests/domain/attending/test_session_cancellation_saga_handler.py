from datetime import datetime

import pytz
from immobilus import immobilus

from crm_pilates.domain.attending.attendee_session_cancellation_saga_handler import (
    AttendeeSessionCancelled,
    AttendeeSessionCancellationSagaHandler,
)
from crm_pilates.domain.sagas import AttendeeSessionCancellationSaga
from crm_pilates.event.event_store import StoreLocator
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.asserters.event_asserter import EventAsserter
from tests.builders.builders_for_test import (
    ClientContextBuilderForTest,
    ClassroomContextBuilderForTest,
    ClassroomBuilderForTest,
    SessionContextBuilderForTest,
)
from tests.builders.providers_for_test import CommandBusProviderForTest


@immobilus("2020-04-03 10:24:15.230")
def test_attendee_session_cancellation_event_should_be_stored(memory_event_store):
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

    session_result: AttendeeSessionCancelled = AttendeeSessionCancellationSagaHandler(
        CommandBusProviderForTest().provide().command_bus
    ).execute(
        AttendeeSessionCancellationSaga(
            clients[1].id, classroom.id, datetime(2020, 4, 3, 11, 0, tzinfo=pytz.utc)
        )
    )

    events = StoreLocator.store.get_all()
    assert len(events) == 2
    assert events[0].type == "ConfirmedSessionEvent"
    assert events[1].type == "AttendeeSessionCancelled"
    assert events[1].timestamp == datetime(
        2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc
    )
    EventAsserter.assert_attendee_session_cancelled(
        events[1].payload, session_result.root_id, clients[1].id
    )


@immobilus("2020-08-03 10:24:15.230")
def test_attendee_session_cancellation_on_already_confirmed_session_should_be_updated(
    memory_event_store,
):
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
    SessionContextBuilderForTest().with_classroom(classroom).cancel(clients[0].id).at(
        datetime(2020, 8, 3, 11, 0)
    ).persist(RepositoryProvider.write_repositories.session).build()

    session_result: AttendeeSessionCancelled = AttendeeSessionCancellationSagaHandler(
        CommandBusProviderForTest().provide().command_bus
    ).execute(
        AttendeeSessionCancellationSaga(
            clients[1].id, classroom.id, datetime(2020, 8, 3, 11, 0, tzinfo=pytz.utc)
        )
    )

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "AttendeeSessionCancelled"
    EventAsserter.assert_attendee_session_cancelled(
        events[0].payload, session_result.root_id, clients[1].id
    )
