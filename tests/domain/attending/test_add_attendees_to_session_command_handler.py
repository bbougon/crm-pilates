import uuid
from datetime import datetime

import pytest
import pytz
from immobilus import immobilus

from crm_pilates.domain.attending.add_attendees_to_session_command_handler import (
    AddAttendeesToSessionSagaHandler,
)
from crm_pilates.domain.exceptions import DomainException
from crm_pilates.domain.sagas import AddAttendeesToSessionSaga
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
def test_should_source_attendees_to_session_added_events():
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
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom = classrooms[0]

    result = AddAttendeesToSessionSagaHandler(
        CommandBusProviderForTest().provide().command_bus
    ).execute(
        AddAttendeesToSessionSaga(
            datetime(2020, 4, 3, 11, 0, tzinfo=pytz.utc), classroom.id, {clients[1].id}
        )
    )

    events = StoreLocator.store.get_all()
    assert len(events) == 2
    assert events[0].type == "ConfirmedSessionEvent"
    assert events[1].type == "AttendeesToSessionAdded"
    assert events[1].timestamp == datetime(
        2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc
    )
    EventAsserter.assert_add_attendees_to_session(
        events[1].payload, result.root_id, [clients[1].id]
    )


@immobilus("2020-08-03 10:24:15.230")
def test_should_add_attendees_on_already_confirmed_session():
    client_repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(3)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest()
            .starting_at(datetime(2020, 8, 3, 11, 0))
            .with_attendee(clients[0].id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom = classrooms[0]
    SessionContextBuilderForTest().with_classroom(classroom).at(
        datetime(2020, 8, 3, 11, 0)
    ).persist(RepositoryProvider.write_repositories.session).build()

    result = AddAttendeesToSessionSagaHandler(
        CommandBusProviderForTest().provide().command_bus
    ).execute(
        AddAttendeesToSessionSaga(
            datetime(2020, 8, 3, 11, 0, tzinfo=pytz.utc),
            classroom.id,
            [clients[1].id, clients[2].id],
        )
    )

    assert len(next(RepositoryProvider.write_repositories.session.get_all())) == 1
    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "AttendeesToSessionAdded"
    assert events[0].timestamp == datetime(
        2020, 8, 3, 10, 24, 15, 230000, tzinfo=pytz.utc
    )
    EventAsserter.assert_add_attendees_to_session(
        events[0].payload, result.root_id, [clients[1].id, clients[2].id]
    )


@immobilus("2020-08-03 10:24:15.230")
def test_should_check_attendees_exist():
    with pytest.raises(DomainException) as e:
        unknown_id = uuid.uuid4()
        AddAttendeesToSessionSagaHandler(
            CommandBusProviderForTest().provide().command_bus
        ).execute(
            AddAttendeesToSessionSaga(
                datetime(2020, 8, 3, 11, 0, tzinfo=pytz.utc),
                uuid.uuid4(),
                [unknown_id],
            )
        )

    assert (
        e.value.message
        == f"One of the attendees with id '{unknown_id}' has not been found"
    )
