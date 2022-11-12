from datetime import datetime

import pytz
from immobilus import immobilus

from crm_pilates.domain.commands import ClassroomScheduleCommand
from crm_pilates.domain.scheduling.classroom_schedule_command_handler import (
    ClassroomScheduleCommandHandler,
    ClassroomScheduled,
)
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.event.event_store import StoreLocator
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from crm_pilates.web.schema.classroom_schemas import Duration
from tests.asserters.event_asserter import EventAsserter
from tests.builders.builders_for_test import ClientContextBuilderForTest


@immobilus("2020-04-03 10:24:15.230")
def test_classroom_creation_event_is_stored(memory_event_store):
    result: ClassroomScheduled = ClassroomScheduleCommandHandler().execute(
        ClassroomScheduleCommand(
            name="classroom",
            position=2,
            _start_date=datetime(2020, 5, 7, 11, 0),
            subject=ClassroomSubject.MACHINE_DUO,
            duration=Duration.parse_obj({"duration": 1, "unit": "HOUR"}),
        )
    )

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClassroomScheduled"
    assert events[0].timestamp == datetime(
        2020, 4, 3, 10, 24, 15, 230000, tzinfo=pytz.utc
    )
    EventAsserter.assert_classroom_created(
        events[0].payload,
        result.root_id,
        "classroom",
        2,
        "MACHINE_DUO",
        (60, "MINUTE"),
        (
            datetime(2020, 5, 7, 11, 0).astimezone(pytz.utc),
            datetime(2020, 5, 7, 12, 0).astimezone(pytz.utc),
        ),
        [],
    )


@immobilus("2019-05-07 08:24:15.230")
def test_classroom_creation_with_attendees_event_is_stored(memory_event_store):
    client_repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(2)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )

    result: ClassroomScheduled = ClassroomScheduleCommandHandler().execute(
        ClassroomScheduleCommand(
            name="classroom",
            position=2,
            _start_date=datetime(2019, 6, 7, 11, 0),
            subject=ClassroomSubject.MAT,
            duration=Duration.parse_obj({"duration": 1, "unit": "HOUR"}),
            attendees=[clients[0]._id, clients[1]._id],
        )
    )

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "ClassroomScheduled"
    assert events[0].timestamp == datetime(
        2019, 5, 7, 8, 24, 15, 230000, tzinfo=pytz.utc
    )
    EventAsserter.assert_classroom_created(
        events[0].payload,
        result.root_id,
        "classroom",
        2,
        "MAT",
        (60, "MINUTE"),
        (
            datetime(2019, 6, 7, 11, 0).astimezone(pytz.utc),
            datetime(2019, 6, 7, 12, 0).astimezone(pytz.utc),
        ),
        [{"id": clients[0]._id}, {"id": clients[1]._id}],
    )
