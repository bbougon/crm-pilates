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
from tests.helpers.helpers import expected_session_response
from web.api.session import session_checkin, next_sessions, sessions
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
        expected_session_response(None, first_classroom.id, first_classroom, "2020-03-19T10:00:00",
                                  "2020-03-19T11:00:00", [
                                      DetailedAttendee(clients[0].id, clients[0].firstname, clients[0].lastname,
                                                       "REGISTERED"),
                                      DetailedAttendee(clients[1].id, clients[1].firstname, clients[1].lastname,
                                                       "REGISTERED")
                                  ]),
        expected_session_response(session.id, second_classroom.id, second_classroom, "2020-03-19T11:00:00",
                                  "2020-03-19T12:00:00", [
                                      DetailedAttendee(clients[2].id, clients[2].firstname, clients[2].lastname,
                                                       "REGISTERED")
                                  ])
    ]


@immobilus("2021-09-05 08:24:15.230")
def test_sessions_should_return_sessions_in_current_month_range():
    repository, clients = ClientContextBuilderForTest().with_clients(3) \
        .persist(RepositoryProvider.write_repositories.client) \
        .build()
    repository, classrooms = ClassroomContextBuilderForTest() \
        .with_classrooms(ClassroomBuilderForTest().starting_at(datetime(2021, 9, 2, 10)).ending_at(datetime(2022, 6, 25, 11))
                         .with_attendee(clients[0]._id).with_attendee(clients[1]._id),
                         ClassroomBuilderForTest().starting_at(datetime(2021, 9, 18, 11))
                         .ending_at(datetime(2022, 6, 25, 12)).with_attendee(clients[2]._id),
                         ClassroomBuilderForTest().starting_at(datetime(2021, 10, 1, 10)).ending_at(datetime(2022, 6, 25, 11))) \
        .persist(RepositoryProvider.write_repositories.classroom) \
        .build()
    session_repository, confirmed_session = SessionContextBuilderForTest().with_classroom(classrooms[1]).at(
        datetime(2021, 9, 25, 11)).confirm().persist(RepositoryProvider.write_repositories.session).build()

    response = Response()
    result = sessions(response, CommandBusProviderForTest().provide())

    assert response.headers["X-Link"] == '</sessions?start_date=2021-08-01T00:00:00&end_date=2021-08-31T23:59:59>; rel="previous", ' \
                                         '</sessions?start_date=2021-09-01T00:00:00&end_date=2021-09-30T23:59:59>; rel="current", ' \
                                         '</sessions?start_date=2021-10-01T00:00:00&end_date=2021-10-31T23:59:59>; rel="next"'
    first_classroom = classrooms[0]
    second_classroom = classrooms[1]
    assert result == [
        expected_session_response(None, first_classroom.id, first_classroom, "2021-09-02T10:00:00",
                                  "2021-09-02T11:00:00", [
                                      DetailedAttendee(clients[0].id, clients[0].firstname, clients[0].lastname,
                                                       "REGISTERED"),
                                      DetailedAttendee(clients[1].id, clients[1].firstname, clients[1].lastname,
                                                       "REGISTERED")
                                  ]),
        expected_session_response(None, first_classroom.id, first_classroom, "2021-09-09T10:00:00",
                                  "2021-09-09T11:00:00", [
                                      DetailedAttendee(clients[0].id, clients[0].firstname, clients[0].lastname,
                                                       "REGISTERED"),
                                      DetailedAttendee(clients[1].id, clients[1].firstname, clients[1].lastname,
                                                       "REGISTERED")
                                  ]),
        expected_session_response(None, first_classroom.id, first_classroom, "2021-09-16T10:00:00",
                                  "2021-09-16T11:00:00", [
                                      DetailedAttendee(clients[0].id, clients[0].firstname, clients[0].lastname,
                                                       "REGISTERED"),
                                      DetailedAttendee(clients[1].id, clients[1].firstname, clients[1].lastname,
                                                       "REGISTERED")
                                  ]),
        expected_session_response(None, second_classroom.id, second_classroom, "2021-09-18T11:00:00",
                                  "2021-09-18T12:00:00", [
                                      DetailedAttendee(clients[2].id, clients[2].firstname, clients[2].lastname,
                                                       "REGISTERED")
                                  ]),
        expected_session_response(None, first_classroom.id, first_classroom, "2021-09-23T10:00:00",
                                  "2021-09-23T11:00:00", [
                                      DetailedAttendee(clients[0].id, clients[0].firstname, clients[0].lastname,
                                                       "REGISTERED"),
                                      DetailedAttendee(clients[1].id, clients[1].firstname, clients[1].lastname,
                                                       "REGISTERED")
                                  ]),
        expected_session_response(confirmed_session.id, second_classroom.id, second_classroom, "2021-09-25T11:00:00",
                                  "2021-09-25T12:00:00", [
                                      DetailedAttendee(clients[2].id, clients[2].firstname, clients[2].lastname,
                                                       "REGISTERED")
                                  ]),
        expected_session_response(None, first_classroom.id, first_classroom, "2021-09-30T10:00:00",
                                  "2021-09-30T11:00:00", [
                                      DetailedAttendee(clients[0].id, clients[0].firstname, clients[0].lastname,
                                                       "REGISTERED"),
                                      DetailedAttendee(clients[1].id, clients[1].firstname, clients[1].lastname,
                                                       "REGISTERED")
                                  ])
    ]
