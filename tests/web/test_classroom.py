import uuid
from datetime import datetime
from fastapi import HTTPException

from fastapi import Response

from domain.classroom.classroom import Classroom
from domain.client.client import Client
from domain.exceptions import DomainException, AggregateNotFoundException
from infrastructure.repository.memory.memory_classroom_repository import MemoryClassroomRepository
from infrastructure.repository.memory.memory_client_repository import MemoryClientRepository
from tests.builders.builders_for_test import ClassroomJsonBuilderForTest, ClientContextBuilderForTest
from tests.builders.providers_for_test import CommandBusProviderForTest, RepositoryProviderForTest
from web.api.classroom import create_classroom
from web.schema.classroom_creation import ClassroomCreation, TimeUnit


def test_create_classroom(memory_event_store):
    repository = MemoryClassroomRepository()
    classroom_json = ClassroomJsonBuilderForTest().with_name("advanced classroom").with_start_date(
        datetime(2020, 2, 11, 10)).with_position(3).with_duration(45, TimeUnit.MINUTE).build()
    RepositoryProviderForTest().for_classroom(repository).provide()

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(),
                                CommandBusProviderForTest().for_classroom().provide())

    assert response["name"] == "advanced classroom"
    assert response["start_date"] == datetime(2020, 2, 11, 10, 0)
    assert response["position"] == 3
    assert response["duration"]["duration"] == 45
    assert response["duration"]["unit"] == "MINUTE"
    assert response["id"]
    assert repository.get_by_id(response["id"])


def test_create_scheduled_classroom(memory_event_store):
    start_date = datetime(2020, 2, 11, 10, 0)
    stop_date = datetime(2020, 3, 11, 10, 0)
    classroom_json = ClassroomJsonBuilderForTest().with_start_date(start_date).with_stop_date(stop_date).build()
    RepositoryProviderForTest().for_classroom().provide()

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(),
                                CommandBusProviderForTest().for_classroom().provide())

    assert response["start_date"] == start_date
    assert response["stop_date"] == stop_date


def test_create_classroom_with_attendees(memory_event_store):
    client_repository, clients = ClientContextBuilderForTest().with_clients(2).persist().build()
    classroom_json = ClassroomJsonBuilderForTest().with_attendees([clients[0].id, clients[1].id]).build()
    RepositoryProviderForTest().for_classroom().for_client(client_repository).provide()

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(),
                                CommandBusProviderForTest().for_classroom().provide())

    assert len(response["attendees"]) == 2
    assert response["attendees"][1]["id"] == clients[1].id


def test_handle_business_exception(memory_event_store, mocker):
    mocker.patch.object(Classroom, "add_attendees", side_effect=DomainException("something wrong occurred"))
    classroom_json = ClassroomJsonBuilderForTest().build()

    try:
        create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(),
                         CommandBusProviderForTest().for_classroom().provide())
    except HTTPException as e:
        assert e.status_code == 409
        assert e.detail == "something wrong occurred"


def test_handle_aggregate_not_found_exception(memory_event_store, mocker):
    unknown_uuid = uuid.uuid4()
    mocker.patch.object(MemoryClientRepository, "get_by_id", side_effect=AggregateNotFoundException(unknown_uuid, Client.__name__))
    classroom_json = ClassroomJsonBuilderForTest().with_attendees([unknown_uuid]).build()

    try:
        create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(),
                         CommandBusProviderForTest().for_classroom().provide())
    except HTTPException as e:
        assert e.status_code == 404
        assert e.detail == f"One of the attendees with id '{unknown_uuid}' has not been found"