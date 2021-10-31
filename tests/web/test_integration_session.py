from datetime import datetime
from unittest.mock import ANY

from fastapi import status, Response
from fastapi.testclient import TestClient
from immobilus import immobilus

from domain.classroom.classroom import Classroom, ScheduledSession
from infrastructure.repository_provider import RepositoryProvider
from main import app
from tests.builders.builders_for_test import ClientContextBuilderForTest, \
    ClassroomContextBuilderForTest, ClassroomBuilderForTest, SessionCheckinJsonBuilderForTest, \
    SessionContextBuilderForTest
from tests.helpers.helpers import expected_session_response

client = TestClient(app)


@immobilus("2019-05-07 08:24:15.230")
def test_get_next_sessions(memory_repositories):
    repository, clients = ClientContextBuilderForTest().with_clients(3) \
        .persist(RepositoryProvider.write_repositories.client) \
        .build()
    repository, classrooms = ClassroomContextBuilderForTest() \
        .with_classrooms(ClassroomBuilderForTest().starting_at(datetime(2019, 5, 7, 10))
                         .with_attendee(clients[0]._id).with_attendee(clients[1]._id),
                         ClassroomBuilderForTest().starting_at(datetime(2019, 5, 7, 11))
                         .with_attendee(clients[2]._id),
                         ClassroomBuilderForTest().starting_at(datetime(2019, 5, 8, 10))) \
        .persist(RepositoryProvider.write_repositories.classroom) \
        .build()

    response: Response = client.get("/sessions/next")

    first_classroom: Classroom = classrooms[0]
    second_classroom: Classroom = classrooms[1]
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        expected_session_response(ANY, str(str(first_classroom.id)), first_classroom, "2019-05-07T10:00:00+00:00", "2019-05-07T11:00:00+00:00", [
            {"id": str(clients[0].id), "firstname": clients[0].firstname, "lastname": clients[0].lastname,
             "attendance": "REGISTERED"},
            {"id": str(clients[1].id), "firstname": clients[1].firstname, "lastname": clients[1].lastname,
             "attendance": "REGISTERED"}
        ]),
        expected_session_response(ANY, str(second_classroom.id), second_classroom, "2019-05-07T11:00:00+00:00", "2019-05-07T12:00:00+00:00", [
            {"id": str(clients[2].id), "firstname": clients[2].firstname, "lastname": clients[2].lastname,
             "attendance": "REGISTERED"}
        ])
    ]


@immobilus("2019-05-07 08:24:15.230")
def test_register_checkin(memory_repositories):
    repository, clients = ClientContextBuilderForTest().with_clients(3) \
        .persist(RepositoryProvider.write_repositories.client) \
        .build()
    repository, classrooms = ClassroomContextBuilderForTest() \
        .with_classrooms(ClassroomBuilderForTest().starting_at(datetime(2019, 5, 7, 10))
                         .with_attendee(clients[0]._id).with_attendee(clients[1]._id)) \
        .persist(RepositoryProvider.write_repositories.classroom) \
        .build()

    classroom: Classroom = classrooms[0]
    session: ScheduledSession = classroom.next_session()
    response: Response = client.post("/sessions/checkin",
                                     json=SessionCheckinJsonBuilderForTest().for_session(session).for_attendee(
                                         clients[0]._id).build())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_session_response(ANY, str(classroom.id), classroom, "2019-05-07T10:00:00+00:00", "2019-05-07T11:00:00+00:00", [
        {"id": str(clients[0].id), "firstname": clients[0].firstname, "lastname": clients[0].lastname,
         "attendance": "CHECKED_IN"},
        {"id": str(clients[1].id), "firstname": clients[1].firstname, "lastname": clients[1].lastname,
         "attendance": "REGISTERED"}
    ])


@immobilus("2019-03-08 09:24:15.230")
def test_updated_session_produces_ok_200(memory_event_store):
    client_repository, clients = ClientContextBuilderForTest().with_clients(2).persist(
        RepositoryProvider.write_repositories.client).build()
    repository, classrooms = ClassroomContextBuilderForTest().with_classroom(
        ClassroomBuilderForTest().starting_at(datetime(2020, 3, 8, 11, 0)).with_attendee(clients[0].id).with_attendee(
            clients[1].id)).persist(
        RepositoryProvider.write_repositories.classroom).build()
    classroom = classrooms[0]
    SessionContextBuilderForTest().with_classroom(classroom).checkin(clients[0].id).at(
        datetime(2020, 3, 8, 11, 0)).persist(RepositoryProvider.write_repositories.session).build()

    response: Response = client.post("/sessions/checkin",
                                     json=SessionCheckinJsonBuilderForTest().for_classroom(classroom).for_attendee(
                                         clients[1]._id).at(datetime(2020, 3, 8, 11, 0)).build())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_session_response(ANY, str(classroom.id), classroom, "2020-03-08T11:00:00+00:00", "2020-03-08T12:00:00+00:00", [
        {"id": str(clients[0].id), "firstname": clients[0].firstname, "lastname": clients[0].lastname,
         "attendance": "CHECKED_IN"},
        {"id": str(clients[1].id), "firstname": clients[1].firstname, "lastname": clients[1].lastname,
         "attendance": "CHECKED_IN"}
    ])


@immobilus("2021-09-02 10:00:00")
def test_sessions_should_return_all_sessions_in_range(memory_repositories):
    repository, classrooms = ClassroomContextBuilderForTest().with_classroom(
        ClassroomBuilderForTest().starting_at(datetime(2021, 9, 2, 10, 0)).ending_at(datetime(2021, 9, 16, 10, 0))).persist(
        RepositoryProvider.write_repositories.classroom).build()

    response: Response = client.get("/sessions?start_date=2021-09-02T00:00:00Z&end_date=2021-09-09T23:59:59Z")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["X-Link"] == '</sessions?start_date=2021-08-26T00%3A00%3A00%2B00%3A00&end_date=2021-09-01T23%3A59%3A59%2B00%3A00>; rel="previous", ' \
                                         '</sessions?start_date=2021-09-02T00%3A00%3A00%2B00%3A00&end_date=2021-09-09T23%3A59%3A59%2B00%3A00>; rel="current", ' \
                                         '</sessions?start_date=2021-09-10T00%3A00%3A00%2B00%3A00&end_date=2021-09-17T23%3A59%3A59%2B00%3A00>; rel="next"'
    assert response.json() == [
        expected_session_response(None, str(classrooms[0].id), classrooms[0], "2021-09-02T10:00:00+00:00", "2021-09-02T11:00:00+00:00", []),
        expected_session_response(None, str(classrooms[0].id), classrooms[0], "2021-09-09T10:00:00+00:00", "2021-09-09T11:00:00+00:00", [])
    ]


@immobilus("2021-09-25 10:00:00", tz_offset=2)
def test_sessions_should_return_all_sessions_from_classroom_for_current_month(memory_repositories):
    repository, classrooms = ClassroomContextBuilderForTest().with_classroom(
        ClassroomBuilderForTest().starting_at(datetime(2021, 8, 13, 10, 0)).ending_at(datetime(2022, 6, 16, 10, 0))).persist(
        RepositoryProvider.write_repositories.classroom).build()

    response: Response = client.get("/sessions?start_date=2021-10-01T00:00:00&end_date=2021-10-31T23:59:59")

    assert response.headers["X-Link"] == '</sessions?start_date=2021-09-01T00%3A00%3A00%2B00%3A00&end_date=2021-09-30T23%3A59%3A59%2B00%3A00>; rel="previous", ' \
                                         '</sessions?start_date=2021-10-01T00%3A00%3A00%2B00%3A00&end_date=2021-10-31T23%3A59%3A59%2B00%3A00>; rel="current", ' \
                                         '</sessions?start_date=2021-11-01T00%3A00%3A00%2B00%3A00&end_date=2021-11-30T23%3A59%3A59%2B00%3A00>; rel="next"'
    assert response.json() == [
        expected_session_response(None, str(classrooms[0].id), classrooms[0], "2021-10-01T10:00:00+00:00", "2021-10-01T11:00:00+00:00", []),
        expected_session_response(None, str(classrooms[0].id), classrooms[0], "2021-10-08T10:00:00+00:00", "2021-10-08T11:00:00+00:00", []),
        expected_session_response(None, str(classrooms[0].id), classrooms[0], "2021-10-15T10:00:00+00:00", "2021-10-15T11:00:00+00:00", []),
        expected_session_response(None, str(classrooms[0].id), classrooms[0], "2021-10-22T10:00:00+00:00", "2021-10-22T11:00:00+00:00", []),
        expected_session_response(None, str(classrooms[0].id), classrooms[0], "2021-10-29T10:00:00+00:00", "2021-10-29T11:00:00+00:00", [])
    ]
