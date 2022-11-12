from datetime import datetime

import pytz
from immobilus import immobilus

from crm_pilates.domain.attending.session_creation_command_handler import (
    SessionCreationCommandHandler,
    ConfirmedSessionEvent,
)
from crm_pilates.domain.commands import SessionCreationCommand
from crm_pilates.event.event_store import StoreLocator
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.asserters.event_asserter import EventAsserter
from tests.builders.builders_for_test import (
    ClassroomBuilderForTest,
    ClassroomContextBuilderForTest,
    ClientContextBuilderForTest,
)


@immobilus("2020-04-03 10:24:15.230")
def test_session_creation_event_is_stored(memory_event_store):
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

    confirmed_session_result: ConfirmedSessionEvent = (
        SessionCreationCommandHandler().execute(
            SessionCreationCommand(
                classroom.id, datetime(2020, 4, 3, 11, 0, tzinfo=pytz.utc)
            )
        )
    )

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ConfirmedSessionEvent"
    assert events[0].timestamp == datetime(
        2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc
    )
    EventAsserter.assert_confirmed_session(
        events[0].payload,
        confirmed_session_result.root_id,
        classroom.id,
        confirmed_session_result.name,
        confirmed_session_result.position,
        confirmed_session_result.subject.value,
        (
            datetime(2020, 4, 3, 11, 0, tzinfo=pytz.utc),
            datetime(2020, 4, 3, 12, 0, tzinfo=pytz.utc),
        ),
        [
            {"id": clients[0].id, "attendance": "REGISTERED"},
            {"id": clients[1].id, "attendance": "REGISTERED"},
        ],
    )
