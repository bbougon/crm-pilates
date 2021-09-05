import uuid
from datetime import datetime

from fastapi import Response, HTTPException, status
from immobilus import immobilus

from domain.classroom.classroom import Classroom
from domain.exceptions import AggregateNotFoundException
from infrastructure.repository.memory.memory_classroom_repositories import MemoryClassroomRepository
from infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import SessionCheckinJsonBuilderForTest, ClientContextBuilderForTest, \
    ClassroomContextBuilderForTest, ClassroomBuilderForTest, SessionContextBuilderForTest
from tests.builders.providers_for_test import CommandBusProviderForTest
from web.api.session import session_checkin, next_sessions
from web.presentation.domain.detailed_attendee import DetailedAttendee
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
    mocker.patch.object(MemoryClassroomRepository, "get_by_id",
                        side_effect=AggregateNotFoundException(classroom_id, "Classroom"))
    session_checkin_json = SessionCheckin.parse_obj(
        SessionCheckinJsonBuilderForTest().for_classroom_id(classroom_id).for_attendee(uuid.uuid4()).at(
            datetime(2019, 5, 8, 10, 30)).build())
    try:
        session_checkin(session_checkin_json, Response(), CommandBusProviderForTest().provide())
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND
        assert e.detail == f"Classroom with id '{str(classroom_id)}' not found"


@immobilus("2020-03-19 08:24:15.230")
def test_get_next_sessions_with_confirmed_sessions():
    repository, clients = ClientContextBuilderForTest().with_clients(3) \
        .persist(RepositoryProvider.write_repositories.client) \
        .build()
    repository, classrooms = ClassroomContextBuilderForTest() \
        .with_classrooms(ClassroomBuilderForTest().starting_at(datetime(2020, 3, 19, 10))
                         .with_attendee(clients[0]._id).with_attendee(clients[1]._id),
                         ClassroomBuilderForTest().starting_at(datetime(2020, 3, 12, 11))
                         .ending_at(datetime(2020, 6, 25, 12)).with_attendee(clients[2]._id),
                         ClassroomBuilderForTest().starting_at(datetime(2020, 3, 20, 10))) \
        .persist(RepositoryProvider.write_repositories.classroom) \
        .build()
    session_repository, session = SessionContextBuilderForTest().with_classroom(classrooms[1]).at(
        datetime(2020, 3, 19, 11)).confirm().persist(RepositoryProvider.write_repositories.session).build()

    response = next_sessions(CommandBusProviderForTest().provide())

    first_classroom = classrooms[0]
    second_classroom = classrooms[1]
    assert response == [
        {
            "id": None,
            "name": first_classroom.name,
            "classroom_id": first_classroom.id,
            "position": first_classroom.position,
            "schedule": {
                "start": "2020-03-19T10:00:00",
                "stop": "2020-03-19T11:00:00"
            },
            "attendees": [
                DetailedAttendee(clients[0].id, clients[0].firstname, clients[0].lastname, "REGISTERED"),
                DetailedAttendee(clients[1].id, clients[1].firstname, clients[1].lastname, "REGISTERED")
            ]
        },
        {
            "id": session.id,
            "name": second_classroom.name,
            "classroom_id": second_classroom.id,
            "position": second_classroom.position,
            "schedule": {
                "start": "2020-03-19T11:00:00",
                "stop": "2020-03-19T12:00:00"
            },
            "attendees": [
                DetailedAttendee(clients[2].id, clients[2].firstname, clients[2].lastname, "REGISTERED")
            ]
        }
    ]
