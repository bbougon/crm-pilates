from datetime import datetime
from unittest.mock import ANY

from fastapi import status, Response
from fastapi.testclient import TestClient
from immobilus import immobilus

from domain.classroom.classroom import Classroom, ScheduledSession
from infrastructure.repository_provider import RepositoryProvider
from main import app
from tests.builders.builders_for_test import ClientContextBuilderForTest, \
    ClassroomContextBuilderForTest, ClassroomBuilderForTest, SessionCheckinJsonBuilderForTest

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
        {
            "id": None,
            "name": first_classroom.name,
            "classroom_id": str(first_classroom.id),
            "position": first_classroom.position,
            "schedule": {
                "start": "2019-05-07T10:00:00",
                "stop": "2019-05-07T11:00:00"
            },
            "attendees": [
                {"id": str(clients[0].id), "firstname": clients[0].firstname, "lastname": clients[0].lastname, "attendance": "REGISTERED"},
                {"id": str(clients[1].id), "firstname": clients[1].firstname, "lastname": clients[1].lastname, "attendance": "REGISTERED"}
            ]
        },
        {
            "id": None,
            "name": second_classroom.name,
            "classroom_id": str(second_classroom.id),
            "position": second_classroom.position,
            "schedule": {
                "start": "2019-05-07T11:00:00",
                "stop": "2019-05-07T12:00:00"
            },
            "attendees": [
                {"id": str(clients[2].id), "firstname": clients[2].firstname, "lastname": clients[2].lastname, "attendance": "REGISTERED"},
            ]
        }
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
    response: Response = client.post("/sessions/checkin", json=SessionCheckinJsonBuilderForTest(session).for_attendee(
        clients[0]._id).build())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": ANY,
        "name": session.name,
        "classroom_id": str(classroom.id),
        "position": session.position,
        "schedule": {
            "start": "2019-05-07T10:00:00",
            "stop": "2019-05-07T11:00:00"
        },
        "attendees": [
            {"id": str(clients[0].id), "firstname": clients[0].firstname, "lastname": clients[0].lastname, "attendance": "CHECKED_IN"},
            {"id": str(clients[1].id), "firstname": clients[1].firstname, "lastname": clients[1].lastname, "attendance": "REGISTERED"}
        ]
    }
