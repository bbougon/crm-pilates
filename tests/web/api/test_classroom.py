from datetime import datetime, timedelta

import arrow
import pytz
from fastapi import Response

from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.infrastructure.repository.memory.memory_classroom_repositories import (
    MemoryClassroomRepository,
)
from crm_pilates.web.api.classroom import (
    create_classroom,
    update_classroom,
)
from crm_pilates.web.schema.classroom_schemas import ClassroomSchedule, TimeUnit
from tests.builders.builders_for_test import (
    ClassroomJsonBuilderForTest,
    ClientContextBuilderForTest,
    ClassroomContextBuilderForTest,
    ClassroomBuilderForTest,
    ClassroomPatchJsonBuilderForTest,
)
from tests.builders.providers_for_test import (
    CommandBusProviderForTest,
    RepositoryProviderForTest,
)


def test_should_create_classroom(memory_event_store):
    repository = MemoryClassroomRepository()
    classroom_json = (
        ClassroomJsonBuilderForTest()
        .with_name("advanced classroom")
        .with_start_date(datetime(2020, 2, 11, 10))
        .with_position(3)
        .for_mat()
        .with_duration(45, TimeUnit.MINUTE)
        .build()
    )
    RepositoryProviderForTest().for_classroom(repository).provide()

    response = create_classroom(
        ClassroomSchedule.parse_obj(classroom_json),
        Response(),
        CommandBusProviderForTest().provide(),
    )

    assert_response_has_expected_values(
        response,
        "advanced classroom",
        datetime(2020, 2, 11, 10, 0),
        3,
        ClassroomSubject.MAT,
        45,
        "MINUTE",
        datetime(2020, 2, 11, 10, 45),
    )
    assert repository.get_by_id(response["id"])


def test_should_create_scheduled_classroom(memory_event_store):
    start_date = datetime(2020, 2, 11, 10, 0).astimezone(pytz.timezone("Europe/Paris"))
    stop_date = datetime(2020, 3, 11, 10, 0).astimezone(pytz.timezone("Europe/Paris"))
    classroom_json = (
        ClassroomJsonBuilderForTest()
        .with_start_date(start_date)
        .with_stop_date(stop_date)
        .build()
    )
    RepositoryProviderForTest().for_classroom().provide()

    response = create_classroom(
        ClassroomSchedule.parse_obj(classroom_json),
        Response(),
        CommandBusProviderForTest().provide(),
    )

    assert_response_has_expected_values(
        response,
        classroom_json["name"],
        start_date,
        classroom_json["position"],
        ClassroomSubject.MAT,
        stop_date=stop_date,
    )


def test_should_create_classroom_with_timezone(memory_event_store):
    repository = MemoryClassroomRepository()
    classroom_json = (
        ClassroomJsonBuilderForTest()
        .with_name("advanced classroom")
        .with_start_date(arrow.get("2020-02-11T10:00:00-07:00").datetime)
        .with_position(3)
        .for_trio()
        .with_duration(45, TimeUnit.MINUTE)
        .build()
    )
    RepositoryProviderForTest().for_classroom(repository).provide()

    response = create_classroom(
        ClassroomSchedule.parse_obj(classroom_json),
        Response(),
        CommandBusProviderForTest().provide(),
    )

    assert_response_has_expected_values(
        response,
        "advanced classroom",
        arrow.get("2020-02-11T10:00:00-07:00").datetime,
        3,
        ClassroomSubject.MACHINE_TRIO,
        45,
        "MINUTE",
        arrow.get("2020-02-11T10:45:00-07:00").datetime,
    )
    assert repository.get_by_id(response["id"])


def test_should_create_classroom_with_attendees(memory_event_store):
    client_repository, clients = (
        ClientContextBuilderForTest().with_clients(2).persist().build()
    )
    RepositoryProviderForTest().for_classroom().for_client(client_repository).provide()
    classroom_json = (
        ClassroomJsonBuilderForTest()
        .with_position(2)
        .for_duo()
        .with_attendees([clients[0]._id, clients[1]._id])
        .build()
    )

    response = create_classroom(
        ClassroomSchedule.parse_obj(classroom_json),
        Response(),
        CommandBusProviderForTest().provide(),
    )

    assert_response_has_expected_values(
        response,
        classroom_json["name"],
        datetime.fromisoformat(classroom_json["start_date"]),
        2,
        ClassroomSubject.MACHINE_DUO,
        stop_date=datetime.fromisoformat(classroom_json["start_date"])
        + timedelta(hours=1),
        expected_attendees=[{"id": clients[0]._id}, {"id": clients[1]._id}],
    )


def test_add_attendee_to_classroom(memory_event_store):
    client_repository, clients = (
        ClientContextBuilderForTest().with_clients(2).persist().build()
    )
    classroom_repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest().with_position(2).with_attendee(clients[0]._id)
        )
        .persist()
        .build()
    )
    RepositoryProviderForTest().for_classroom(classroom_repository).for_client(
        client_repository
    ).provide()
    classroom: Classroom = classrooms[0]

    update_classroom(
        classroom._id,
        ClassroomPatchJsonBuilderForTest()
        .with_attendee(clients[0]._id)
        .with_attendee(clients[1]._id)
        .build(),
        CommandBusProviderForTest().provide(),
    )

    patched_classroom: Classroom = classroom_repository.get_by_id(classroom._id)
    assert len(patched_classroom.attendees) == 2
    attendees_ids = list(
        map(lambda attendee: attendee._id, patched_classroom.attendees)
    )
    assert clients[0]._id in attendees_ids
    assert clients[1]._id in attendees_ids


def assert_response_has_expected_values(
    response: dict,
    expected_name: str,
    expected_start: datetime,
    expected_position: int,
    expected_subject: ClassroomSubject,
    expected_duration: int = 1,
    expected_time_unit: str = "HOUR",
    stop_date: datetime = None,
    expected_attendees: [] = [],
):
    assert (
        response.items()
        >= {
            "name": expected_name,
            "schedule": {
                "start": expected_start.astimezone(pytz.utc),
                "stop": stop_date.astimezone(pytz.utc),
            },
            "position": expected_position,
            "subject": expected_subject.value,
            "duration": {
                "duration": expected_duration,
                "time_unit": expected_time_unit,
            },
        }.items()
    )
    for expected_attendee in expected_attendees:
        assert expected_attendee in response["attendees"]
    assert response["id"]
