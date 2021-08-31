import uuid
from datetime import datetime

from fastapi import Response, HTTPException, status

from domain.classroom.classroom import Classroom
from domain.exceptions import AggregateNotFoundException
from infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import SessionCheckinJsonBuilderForTest, ClientContextBuilderForTest, \
    ClassroomContextBuilderForTest, ClassroomBuilderForTest
from tests.builders.providers_for_test import CommandBusProviderForTest
from web.api.session import session_checkin
from web.schema.session_schemas import SessionCheckin


def test_handle_domain_exception_on_invalid_confirmed_session():
    repository, clients = ClientContextBuilderForTest().with_clients(3) \
        .persist(RepositoryProvider.write_repositories.client) \
        .build()
    repository, classrooms = ClassroomContextBuilderForTest() \
        .with_classrooms(ClassroomBuilderForTest().starting_at(datetime(2019, 5, 7, 10))
                         .with_attendee(clients[0]._id).with_attendee(clients[1]._id)) \
        .persist(RepositoryProvider.write_repositories.classroom) \
        .build()
    classroom: Classroom = classrooms[0]
    response = Response()
    session_checkin_json = SessionCheckin.parse_obj(
        SessionCheckinJsonBuilderForTest().for_classroom(classroom).for_attendee(clients[0].id).at(
            datetime(2019, 5, 8, 10, 30)).build())

    try:
        session_checkin(session_checkin_json, response, CommandBusProviderForTest().provide())
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == f"Classroom '{classroom.name}' starting at '2019-05-07T10:00:00' cannot be set at '2019-05-08T10:30:00', closest possible dates are '2019-05-07T10:00:00' or '2019-05-14T10:00:00'"


def test_handle_aggregate_not_found_exception(mocker):
    classroom_id = uuid.uuid4()
    mocker.patch.object(MemoryClassroomRepository, "get_by_id", side_effect=AggregateNotFoundException(classroom_id, "Classroom"))
    session_checkin_json = SessionCheckin.parse_obj(
        SessionCheckinJsonBuilderForTest().for_classroom_id(classroom_id).for_attendee(uuid.uuid4()).at(
            datetime(2019, 5, 8, 10, 30)).build())
    try:
        session_checkin(session_checkin_json, Response(), CommandBusProviderForTest().provide())
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND
        assert e.detail == f"Classroom with id '{str(classroom_id)}' not found"
