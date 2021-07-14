from datetime import datetime

from fastapi import Response

from command.command_bus import CommandBus
from domain.classroom.classroom_command_handler import ClassroomCreationCommandHandler
from domain.commands import ClassroomCreationCommand
from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repository import MemoryClassroomRepository
from tests.builders.builders_for_test import ClassroomJsonBuilderForTest, ClientContextBuilderForTest
from web.api.classroom import create_classroom
from web.schema.classroom_creation import ClassroomCreation, TimeUnit


def test_create_classroom(memory_event_store):
    repository = MemoryClassroomRepository()
    classroom_json = ClassroomJsonBuilderForTest().with_name("advanced classroom").with_start_date(
        datetime(2020, 2, 11, 10)).with_position(3).with_duration(45, TimeUnit.MINUTE).build()

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(),
                                CommandBus({ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(
                                    Repositories({"classroom": repository}))}))

    assert response["name"] == "advanced classroom"
    assert response["start_date"] == datetime(2020, 2, 11, 10, 0)
    assert response["position"] == 3
    assert response["duration"]["duration"] == 45
    assert response["duration"]["unit"] == "MINUTE"
    assert response["id"]
    assert repository.get_by_id(response["id"])


def test_create_scheduled_classroom(memory_event_store):
    repository = MemoryClassroomRepository()
    start_date = datetime(2020, 2, 11, 10, 0)
    stop_date = datetime(2020, 3, 11, 10, 0)
    classroom_json = ClassroomJsonBuilderForTest().with_start_date(start_date).with_stop_date(stop_date).build()

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(),
                                CommandBus({ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(
                                    Repositories({"classroom": repository}))}))

    assert response["start_date"] == start_date
    assert response["stop_date"] == stop_date


def test_create_classroom_with_attendees(memory_event_store):
    classroom_repository = MemoryClassroomRepository()
    client_repository, clients = ClientContextBuilderForTest().with_clients(2).persist().build()
    classroom_json = ClassroomJsonBuilderForTest().with_attendees([clients[0].id,clients[1].id]).build()

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(),
                                CommandBus({ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(
                                    Repositories({"classroom": classroom_repository, "client": client_repository}))}))

    assert len(response["attendees"]) == 2
    assert response["attendees"][1]["id"] == clients[1].id
