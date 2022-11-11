import uuid
from datetime import datetime

import pytest
import pytz
from immobilus import immobilus

from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.scheduling.classroom_patch_command_handler import (
    ClassroomPatchCommandHandler,
)
from crm_pilates.domain.commands import ClassroomPatchCommand
from crm_pilates.domain.exceptions import AggregateNotFoundException
from crm_pilates.event.event_store import StoreLocator
from tests.asserters.event_asserter import EventAsserter
from tests.builders.builders_for_test import (
    ClassroomContextBuilderForTest,
    ClientContextBuilderForTest,
    ClassroomBuilderForTest,
)
from tests.builders.providers_for_test import RepositoryProviderForTest


@immobilus("2019-03-19 10:24:15.100")
def test_classroom_patch_with_attendees(memory_event_store):
    client_repository, clients = (
        ClientContextBuilderForTest().with_clients(2).persist().build()
    )
    classroom_repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(ClassroomBuilderForTest().with_position(2))
        .persist()
        .build()
    )
    RepositoryProviderForTest().for_classroom(classroom_repository).for_client(
        client_repository
    ).provide()
    classroom: Classroom = classrooms[0]

    attendees_set = ClassroomPatchCommandHandler().execute(
        ClassroomPatchCommand(classroom._id, [clients[0]._id, clients[1]._id])
    )

    events = StoreLocator.store.get_all()
    assert len(classroom.attendees) == 2
    assert attendees_set
    assert len(events) == 1
    assert events[0].type == "AllAttendeesAdded"
    assert events[0].timestamp == datetime(
        2019, 3, 19, 10, 24, 15, 100000, tzinfo=pytz.utc
    )
    assert events[0].root_id == classroom._id
    EventAsserter.assert_all_attendees_added(
        events[0].payload, [{"id": clients[0]._id}, {"id": clients[1]._id}]
    )


def test_cannot_patch_classroom_with_attendees_for_unknown_clients(memory_event_store):
    classroom_repository, classrooms = (
        ClassroomContextBuilderForTest().persist().build()
    )
    RepositoryProviderForTest().for_classroom(
        classroom_repository
    ).for_client().provide()
    unknown_client_id = uuid.uuid4()

    with pytest.raises(AggregateNotFoundException) as e:
        ClassroomPatchCommandHandler().execute(
            ClassroomPatchCommand(classrooms[0]._id, [unknown_client_id])
        )

    assert (
        e.value.message == f"Aggregate 'Client' with id '{unknown_client_id}' not found"
    )
