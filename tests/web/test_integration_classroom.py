from fastapi import status, Response
from fastapi.testclient import TestClient

from domain.classroom.classroom import Classroom
from event.event_store import StoreLocator
from infrastructure.event.sqlite.sqlite_event_store import SQLiteEventStore
from infrastructure.repository_provider import RepositoryProvider
from main import app
from tests.builders.builders_for_test import ClassroomJsonBuilderForTest, ClientContextBuilderForTest, \
    ClassroomContextBuilderForTest, ClassroomBuilderForTest

client = TestClient(app)


def test_create_classroom(database):
    StoreLocator.store = SQLiteEventStore(database)
    response = client.post("/classrooms", json=ClassroomJsonBuilderForTest().build())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.headers["Location"] == f"/classrooms/{response.json()['id']}"


def test_create_classroom_with_attendees(database):
    StoreLocator.store = SQLiteEventStore(database)
    repository, clients = ClientContextBuilderForTest().with_one_client().persist(
        RepositoryProvider.write_repositories.client).build()

    response = client.post("/classrooms", json=ClassroomJsonBuilderForTest().with_attendees([clients[0]._id]).build())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.headers["Location"] == f"/classrooms/{response.json()['id']}"


def test_get_classroom(memory_repositories):
    client_repository, clients = ClientContextBuilderForTest().with_clients(2).persist(
        RepositoryProvider.write_repositories.client).build()
    repository, classrooms = ClassroomContextBuilderForTest()\
        .with_classroom(ClassroomBuilderForTest()
                        .with_attendee(clients[0]._id)
                        .with_attendee(clients[1]._id)
                        .with_position(2))\
        .persist(RepositoryProvider.write_repositories.classroom)\
        .build()
    classroom: Classroom = classrooms[0]

    response: Response = client.get(f"/classrooms/{classroom._id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "name": classroom._name,
        "id": str(classroom._id),
        "position": classroom._position,
        "schedule": {
            "start": classroom._schedule.start.isoformat(),
            "stop": classroom._schedule.stop.isoformat() if classroom._schedule.stop else None
        },
        "duration": {
            "time_unit": classroom._duration.time_unit.value,
            "duration": classroom._duration.duration
        },
        "attendees": [
            {"client_id": str(clients[0]._id), "firstname": clients[0].firstname, "lastname": clients[0].lastname},
            {"client_id": str(clients[1]._id), "firstname": clients[1].firstname, "lastname": clients[1].lastname}
        ]
    }


def test_add_attendee_to_a_classroom():
    repository, clients = ClientContextBuilderForTest().with_clients(2).persist(
        RepositoryProvider.write_repositories.client).build()
    repository, classrooms = ClassroomContextBuilderForTest().with_classroom(
        ClassroomBuilderForTest().with_position(2).with_attendee(clients[0]._id)).persist(
        RepositoryProvider.write_repositories.classroom).build()

    response: Response = client.patch(f"/classrooms/{classrooms[0]._id}",
                                      json={"attendees": [{"client_id": clients[1]._id.hex}]})

    assert response.status_code == status.HTTP_204_NO_CONTENT
