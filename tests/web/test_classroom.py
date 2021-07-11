from datetime import datetime

from fastapi import Response

from command.command_bus import CommandBus
from domain.classroom.classroom_command_handler import ClassroomCreationCommandHandler
from domain.commands import ClassroomCreationCommand
from event.event_store import StoreLocator
from infrastructure.repositories import Repositories
from infrastructure.repository.memory.memory_classroom_repository import MemoryClassroomRepository
from tests.infrastructure.event.memory_event_store import MemoryEventStore
from web.api.classroom import create_classroom
from web.schema.classroom_creation import ClassroomCreation


def test_create_classroom():
    StoreLocator.store = MemoryEventStore()
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


def test_create_scheduled_classroom():
    StoreLocator.store = MemoryEventStore()
    repository = MemoryClassroomRepository()
    classroom_json = {"name": "advanced classroom", "start_date": "2020-02-11T10:00:00", "position": 4,
                      "stop_date": "2020-03-11T10:00:00", "duration": {"duration": 45, "unit": "MINUTE"}}

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(),
                                CommandBus({ClassroomCreationCommand.__name__: ClassroomCreationCommandHandler(
                                    Repositories({"classroom": repository}))}))

    assert response["start_date"] == datetime(2020, 2, 11, 10, 0)
    assert response["stop_date"] == datetime(2020, 3, 11, 10, 0)
