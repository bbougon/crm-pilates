import uuid
from datetime import datetime

import pytest
from immobilus import immobilus

from domain.classroom.classroom_patch_command_handler import ClassroomPatchCommandHandler
from domain.commands import ClassroomPatchCommand
from domain.exceptions import AggregateNotFoundException
from event.event_store import StoreLocator
from tests.builders.builders_for_test import ClassroomContextBuilderForTest, ClientContextBuilderForTest, \
    ClassroomBuilderForTest
from tests.builders.providers_for_test import RepositoryProviderForTest


@immobilus("2019-03-19 10:24:15.100")
def test_classroom_patch_with_attendees(memory_event_store):
    client_repository, clients = ClientContextBuilderForTest().with_clients(2).persist().build()
    classroom_repository, classroom = ClassroomContextBuilderForTest().with_classroom(
        ClassroomBuilderForTest().with_position(2)).persist().build()
    RepositoryProviderForTest().for_classroom(classroom_repository).for_client(client_repository).provide()

    attendees_set = ClassroomPatchCommandHandler().execute(
        ClassroomPatchCommand(classroom.id, [clients[0].id, clients[1].id]))

    events = StoreLocator.store.get_all()
    assert len(classroom.attendees) == 2
    assert attendees_set
    assert len(events) == 1
    assert events[0].type == "AllAttendeesAdded"
    assert events[0].timestamp == datetime(2019, 3, 19, 10, 24, 15, 100000)
    assert events[0].root_id == classroom.id
    assert events[0].payload == {
        "attendees": [
            {"id": clients[0].id},
            {"id": clients[1].id}
        ]
    }


def test_cannot_patch_classroom_with_attendees_for_unknown_clients(memory_event_store):
    classroom_repository, classroom = ClassroomContextBuilderForTest().persist().build()
    RepositoryProviderForTest().for_classroom(classroom_repository).for_client().provide()
    unknown_client_id = uuid.uuid4()

    with pytest.raises(AggregateNotFoundException) as e:
        ClassroomPatchCommandHandler().execute(ClassroomPatchCommand(classroom.id, [unknown_client_id]))

    assert e.value.message == f"Aggregate 'Client' with id '{unknown_client_id}' not found"
