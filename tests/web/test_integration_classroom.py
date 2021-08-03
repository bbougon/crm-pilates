from fastapi import status, Response
from fastapi.testclient import TestClient

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

    response = client.post("/classrooms", json=ClassroomJsonBuilderForTest().with_attendees([clients[0].id]).build())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.headers["Location"] == f"/classrooms/{response.json()['id']}"


def test_get_classroom(memory_repositories):
    client_repository, clients = ClientContextBuilderForTest().with_clients(2).persist(
        RepositoryProvider.write_repositories.client).build()
    repository, classroom = ClassroomContextBuilderForTest()\
        .with_classroom(ClassroomBuilderForTest()
                        .with_attendee(clients[0].id)
                        .with_attendee(clients[1].id)
                        .with_position(2))\
        .persist(RepositoryProvider.write_repositories.classroom)\
        .build()

    response: Response = client.get(f"/classrooms/{classroom.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "name": classroom.name,
        "id": str(classroom.id),
        "position": classroom.position,
        "schedule": {
            "start": classroom.schedule.start.isoformat(),
            "stop": classroom.schedule.stop.isoformat() if classroom.schedule.stop else None
        },
        "duration": {
            "time_unit": classroom.duration.time_unit.value,
            "duration": classroom.duration.duration
        },
        "attendees": [
            {"client_id": str(clients[0].id), "firstname": clients[0].firstname, "lastname": clients[0].lastname},
            {"client_id": str(clients[1].id), "firstname": clients[1].firstname, "lastname": clients[1].lastname}
        ]
    }


def test_add_attendee_to_a_classroom():
    repository, clients = ClientContextBuilderForTest().with_clients(2).persist(
        RepositoryProvider.write_repositories.client).build()
    repository, classroom = ClassroomContextBuilderForTest().with_classroom(
        ClassroomBuilderForTest().with_position(2).with_attendee(clients[0].id)).persist(
        RepositoryProvider.write_repositories.classroom).build()

    response: Response = client.patch(f"/classrooms/{classroom.id}",
                                      json={"attendees": [{"client_id": clients[1].id.hex}]})

    assert response.status_code == status.HTTP_204_NO_CONTENT
