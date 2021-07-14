from datetime import datetime

from fastapi import Response

from command.command_bus import CommandBus
from domain.classroom.classroom_command_handler import ClassroomCreationCommandHandler
from domain.commands import ClassroomCreationCommand
from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repository import MemoryClassroomRepository
from infrastructure.repository.memory.memory_client_repository import MemoryClientRepository
from tests.builders.builders_for_test import ClientBuilderForTest
from web.api.classroom import create_classroom
from web.schema.classroom_creation import ClassroomCreation


def test_create_classroom(memory_event_store):
    repository = MemoryClassroomRepository()
    classroom_json = {"name": "advanced classroom", "start_date": "2020-02-11T10:00:00", "position": 3,
                      "duration": {"duration": 45, "unit": "MINUTE"}}

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
    classroom_json = {"name": "advanced classroom", "start_date": "2020-02-11T10:00:00", "position": 4,
                      "stop_date": "2020-03-11T10:00:00", "duration": {"duration": 45, "unit": "MINUTE"}}

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(),
                                CommandBus({ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(
                                    Repositories({"classroom": repository}))}))

    assert response["start_date"] == datetime(2020, 2, 11, 10, 0)
    assert response["stop_date"] == datetime(2020, 3, 11, 10, 0)


def test_create_classroom_with_attendees(memory_event_store):
    classroom_repository = MemoryClassroomRepository()
    client_repository = MemoryClientRepository()
    first_client = ClientBuilderForTest().build()
    second_client = ClientBuilderForTest().build()
    client_repository.persist(first_client)
    client_repository.persist(second_client)
    classroom_json = {"name": "advanced classroom", "start_date": "2020-02-11T10:00:00", "position": 4,
                      "stop_date": "2020-03-11T10:00:00", "duration": {"duration": 45, "unit": "MINUTE"},
                      "attendees": [{"client_id": first_client.id}, {"client_id": second_client.id}]}

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(),
                                CommandBus({ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(
                                    Repositories({"classroom": classroom_repository, "client": client_repository}))}))

    assert len(response["attendees"]) == 2
    assert response["attendees"][1]["id"] == second_client.id
