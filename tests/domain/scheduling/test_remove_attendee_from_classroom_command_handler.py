import uuid

import pytz
from immobilus import immobilus
from datetime import datetime

from crm_pilates.domain.commands import RemoveAttendeeFromClassroomCommand
from crm_pilates.domain.scheduling.remove_attendee_from_classroom_command_handler import (
    RemoveAttendeeFromClassroomCommandHandler,
    AttendeeRemovedFromClassroom,
)
from crm_pilates.event.event_store import StoreLocator
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.asserters.event_asserter import EventAsserter
from tests.builders.builders_for_test import ClassroomBuilderForTest


@immobilus("2023-01-05 10:24:15.230")
def test_should_remove_attendee_from_classroom(memory_event_store):
    attendee_to_remove = uuid.uuid4()
    first_classroom = (
        ClassroomBuilderForTest()
        .with_attendees([attendee_to_remove, uuid.uuid4()])
        .build()
    )
    second_classroom = (
        ClassroomBuilderForTest()
        .with_attendees([attendee_to_remove, uuid.uuid4()])
        .build()
    )
    RepositoryProvider.write_repositories.classroom.persist(first_classroom)
    RepositoryProvider.write_repositories.classroom.persist(second_classroom)

    result: AttendeeRemovedFromClassroom = (
        RemoveAttendeeFromClassroomCommandHandler().execute(
            RemoveAttendeeFromClassroomCommand(attendee_to_remove)
        )
    )

    events = StoreLocator.store.get_all()
    assert len(events) == 1
    assert events[0].type == "AttendeeRemovedFromClassroom"
    assert events[0].timestamp == datetime(
        2023, 1, 5, 10, 24, 15, 230000, tzinfo=pytz.utc
    )
    EventAsserter.assert_attendee_removed(
        events[0].payload, result.root_id, [first_classroom.id, second_classroom.id]
    )
