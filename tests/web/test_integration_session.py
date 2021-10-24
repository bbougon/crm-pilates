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
        expected_session_response(ANY, str(str(first_classroom.id)), first_classroom, "2019-05-07T10:00:00", "2019-05-07T11:00:00", [
            {"id": str(clients[0].id), "firstname": clients[0].firstname, "lastname": clients[0].lastname,
             "attendance": "REGISTERED"},
            {"id": str(clients[1].id), "firstname": clients[1].firstname, "lastname": clients[1].lastname,
             "attendance": "REGISTERED"}
        ]),
        expected_session_response(ANY, str(second_classroom.id), second_classroom, "2019-05-07T11:00:00", "2019-05-07T12:00:00", [
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
    assert response.json() == expected_session_response(ANY, str(classroom.id), classroom, "2019-05-07T10:00:00", "2019-05-07T11:00:00", [
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

    assert response.json() == expected_session_response(ANY, str(classroom.id), classroom, "2020-03-08T11:00:00", "2020-03-08T12:00:00", [
        {"id": str(clients[0].id), "firstname": clients[0].firstname, "lastname": clients[0].lastname,
         "attendance": "CHECKED_IN"},
        {"id": str(clients[1].id), "firstname": clients[1].firstname, "lastname": clients[1].lastname,
         "attendance": "CHECKED_IN"}
    ])
