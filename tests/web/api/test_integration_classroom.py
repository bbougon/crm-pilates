import uuid

import arrow
from dateutil.tz import tzutc
from fastapi import status, Response
from fastapi.testclient import TestClient

from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from crm_pilates.main import app
from tests.builders.builders_for_test import (
    ClassroomJsonBuilderForTest,
    ClientContextBuilderForTest,
    ClassroomContextBuilderForTest,
    ClassroomBuilderForTest,
)

client = TestClient(app)


def test_create_classroom(persisted_event_store, authenticated_user):
    response = client.post("/classrooms", json=ClassroomJsonBuilderForTest().build())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.headers["Location"] == f"/classrooms/{response.json()['id']}"


def test_create_classroom_with_attendees(persisted_event_store, authenticated_user):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_one_client()
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    classroom: dict = (
        ClassroomJsonBuilderForTest().with_attendees([clients[0]._id]).build()
    )

    response = client.post("/classrooms", json=classroom)

    assert response.status_code == status.HTTP_201_CREATED
    classroom_id = response.json()["id"]
    assert response.headers["Location"] == f"/classrooms/{classroom_id}"
    assert response.json() == {
        "name": classroom["name"],
        "id": classroom_id,
        "position": classroom["position"],
        "subject": classroom["subject"],
        "schedule": {
            "start": arrow.get(
                classroom["start_date"], tzinfo=tzutc()
            ).datetime.isoformat(),
            "stop": arrow.get(classroom["start_date"], tzinfo=tzutc())
            .shift(hours=+1)
            .datetime.isoformat(),
        },
        "duration": {"time_unit": "HOUR", "duration": 1},
        "attendees": [
            {"id": str(clients[0].id)},
        ],
    }


def test_handle_aggregate_not_found_exception_on_classroom_creation(authenticated_user):
    unknown_uuid = uuid.uuid4()
    classroom_json = (
        ClassroomJsonBuilderForTest().with_attendees([unknown_uuid]).build()
    )

    response = client.post("/classrooms", json=classroom_json)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == [
        {
            "msg": f"One of the attendees with id '{unknown_uuid}' has not been found",
            "type": "create classroom",
        }
    ]


def test_should_not_create_a_classroom_if_not_authenticated(memory_event_store):
    response = client.post("/classrooms", json=ClassroomJsonBuilderForTest().build())

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_get_classroom(memory_repositories, authenticated_user):
    client_repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(2)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest()
            .with_attendee(clients[0]._id)
            .with_attendee(clients[1]._id)
            .with_position(2)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom: Classroom = classrooms[0]

    response: Response = client.get(f"/classrooms/{classroom._id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "name": classroom.name,
        "id": str(classroom.id),
        "position": classroom.position,
        "subject": classroom.subject.value,
        "schedule": {
            "start": classroom.schedule.start.isoformat(),
            "stop": classroom.schedule.stop.isoformat()
            if classroom.schedule.stop
            else None,
        },
        "duration": {
            "time_unit": "HOUR",
            "duration": classroom.duration.time_unit.value,
        },
        "attendees": [
            {
                "id": str(clients[0].id),
                "firstname": clients[0].firstname,
                "lastname": clients[0].lastname,
            },
            {
                "id": str(clients[1].id),
                "firstname": clients[1].firstname,
                "lastname": clients[1].lastname,
            },
        ],
    }


def test_classroom_not_found(authenticated_user):
    unknown_uuid = uuid.uuid4()

    response: Response = client.get(f"/classrooms/{unknown_uuid}")

    assert response.status_code == 404
    assert response.json()["detail"] == [
        {
            "msg": f"Classroom with id '{str(unknown_uuid)}' not found",
            "type": "get classroom",
        }
    ]


def test_add_attendee_to_a_classroom(authenticated_user):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(2)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest().with_position(2).with_attendee(clients[0]._id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )

    response: Response = client.patch(
        f"/classrooms/{classrooms[0]._id}",
        json={"attendees": [{"id": clients[1]._id.hex}]},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_handle_aggregate_not_found_on_classroom_patch(authenticated_user):
    unknown_uuid = uuid.uuid4()
    classroom_repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(ClassroomBuilderForTest().with_position(2))
        .persist()
        .build()
    )

    response: Response = client.patch(
        f"/classrooms/{classrooms[0]._id}",
        json={"attendees": [{"id": str(unknown_uuid)}]},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == [
        {
            "msg": f"One of the attendees with id '{unknown_uuid}' has not been found",
            "type": "update classroom",
        }
    ]
