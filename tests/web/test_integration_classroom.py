from fastapi import status, Response
from fastapi.testclient import TestClient

from domain.classroom.classroom import Classroom
from event.event_store import StoreLocator
from infrastructure.event.sqlite.sqlite_event_store import SQLiteEventStore
from infrastructure.repository_provider import RepositoryProvider
from main import app
from tests.builders.builders_for_test import ClassroomJsonBuilderForTest, ClientContextBuilderForTest, \
    ClassroomContextBuilderForTest

client = TestClient(app)


def test_post_classroom(database):
    StoreLocator.store = SQLiteEventStore(database)
    response = client.post("/classrooms", json=ClassroomJsonBuilderForTest().build())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.headers["Location"] == f"/classrooms/{response.json()['id']}"


def test_post_classroom_with_attendees(database):
    StoreLocator.store = SQLiteEventStore(database)
    repository, clients = ClientContextBuilderForTest().with_one_client().persist(RepositoryProvider.repositories.client).build()

    response = client.post("/classrooms", json=ClassroomJsonBuilderForTest().with_attendees([clients[0].id]).build())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.headers["Location"] == f"/classrooms/{response.json()['id']}"


def test_get_classroom():
    repository, classrooms = ClassroomContextBuilderForTest().with_one_classroom().persist(RepositoryProvider.repositories.classroom).build()

    response: Response = client.get(f"/classrooms/{classrooms[0].id}")

    classroom: Classroom = classrooms[0]
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
        "attendees": []
    }