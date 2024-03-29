import uuid
from datetime import datetime
from unittest.mock import ANY

import arrow
import pytz
from fastapi import status, Response
from fastapi.testclient import TestClient
from immobilus import immobilus

from crm_pilates.domain.attending.sessions import Sessions
from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.attending.session import ScheduledSession
from crm_pilates.domain.scheduling.attendee import Attendance
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.domain.client.client import Client
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from crm_pilates.app import app
from tests.builders.builders_for_test import (
    ClientContextBuilderForTest,
    ClassroomContextBuilderForTest,
    ClassroomBuilderForTest,
    SessionCheckinJsonBuilderForTest,
    SessionContextBuilderForTest,
    AttendeeSessionCancellationJsonBuilderForTest,
    ClientBuilderForTest,
    SessionAddAttendeesJsonBuilderForTest,
)
from tests.helpers.helpers import expected_session_response

client = TestClient(app)


@immobilus(pytz.timezone("Europe/Paris").localize(datetime(2019, 5, 7, 8, 24)))
def test_get_next_sessions(memory_repositories, event_bus, authenticated_user):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(3)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    first_client = clients[0]
    second_client = clients[1]
    third_client = clients[2]
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classrooms(
            ClassroomBuilderForTest()
            .starting_at(datetime(2019, 5, 7, 10))
            .with_attendee(first_client._id)
            .with_attendee(second_client._id),
            ClassroomBuilderForTest()
            .starting_at(datetime(2019, 5, 7, 11))
            .with_attendee(third_client._id),
            ClassroomBuilderForTest().starting_at(datetime(2019, 5, 8, 10)),
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )

    response: Response = client.get("/sessions/next")

    first_classroom: Classroom = classrooms[0]
    second_classroom: Classroom = classrooms[1]
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        expected_session_response(
            ANY,
            str(str(first_classroom.id)),
            first_classroom,
            "2019-05-07T10:00:00+00:00",
            "2019-05-07T11:00:00+00:00",
            [
                {
                    "id": str(first_client.id),
                    "firstname": first_client.firstname,
                    "lastname": first_client.lastname,
                    "attendance": "REGISTERED",
                    "credits": {"amount": __client_credits(first_client).value},
                },
                {
                    "id": str(second_client.id),
                    "firstname": second_client.firstname,
                    "lastname": second_client.lastname,
                    "attendance": "REGISTERED",
                    "credits": {"amount": __client_credits(second_client).value},
                },
            ],
        ),
        expected_session_response(
            ANY,
            str(second_classroom.id),
            second_classroom,
            "2019-05-07T11:00:00+00:00",
            "2019-05-07T12:00:00+00:00",
            [
                {
                    "id": str(third_client.id),
                    "firstname": third_client.firstname,
                    "lastname": third_client.lastname,
                    "attendance": "REGISTERED",
                    "credits": {"amount": __client_credits(third_client).value},
                }
            ],
        ),
    ]


@immobilus("2019-05-07 08:24:15.230")
def test_should_register_checkin(memory_repositories, event_bus, authenticated_user):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(3)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classrooms(
            ClassroomBuilderForTest()
            .starting_at(datetime(2019, 5, 7, 10))
            .with_attendee(clients[0]._id)
            .with_attendee(clients[1]._id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )

    classroom: Classroom = classrooms[0]
    session: ScheduledSession = Sessions.next_session(classroom)
    response: Response = client.post(
        "/sessions/checkin",
        json=SessionCheckinJsonBuilderForTest()
        .for_session(session)
        .for_attendee(clients[0]._id)
        .build(),
    )

    assert classroom.attendees[0].attendance == Attendance.REGISTERED
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_session_response(
        ANY,
        str(classroom.id),
        classroom,
        "2019-05-07T10:00:00+00:00",
        "2019-05-07T11:00:00+00:00",
        [
            {
                "id": str(clients[0].id),
                "firstname": clients[0].firstname,
                "lastname": clients[0].lastname,
                "attendance": "CHECKED_IN",
                "credits": {"amount": __client_credits(clients[0]).value},
            },
            {
                "id": str(clients[1].id),
                "firstname": clients[1].firstname,
                "lastname": clients[1].lastname,
                "attendance": "REGISTERED",
                "credits": {"amount": __client_credits(clients[1]).value},
            },
        ],
    )


def test_should_handle_domain_exception_on_invalid_confirmed_session(
    authenticated_user,
):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(3)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classrooms(
            ClassroomBuilderForTest()
            .starting_at(datetime(2019, 5, 7, 10))
            .with_attendee(clients[0]._id)
            .with_attendee(clients[1]._id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom: Classroom = classrooms[0]
    session_checkin_json = (
        SessionCheckinJsonBuilderForTest()
        .for_classroom(classroom)
        .for_attendee(clients[0].id)
        .at(datetime(2019, 5, 8, 10, 30))
        .build()
    )

    response: Response = client.post(
        "/sessions/checkin",
        json=session_checkin_json,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == [
        {
            "msg": f"Classroom '{classroom.name}' starting at '2019-05-07T10:00:00+00:00' cannot be set at '2019-05-08T10:30:00+00:00', closest possible dates are '2019-05-07T10:00:00+00:00' or '2019-05-14T10:00:00+00:00'",
            "type": "session checkin",
        }
    ]


def test_should_handle_aggregate_not_found_exception_on_checkin(
    memory_event_store, event_bus, authenticated_user
):
    classroom_id = uuid.uuid4()
    session_checkin_json = (
        SessionCheckinJsonBuilderForTest()
        .for_classroom_id(classroom_id)
        .for_attendee(uuid.uuid4())
        .at(datetime(2019, 5, 8, 10, 30))
        .build()
    )

    response: Response = client.post(
        "/sessions/checkin",
        json=session_checkin_json,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == [
        {
            "msg": f"Classroom with id '{str(classroom_id)}' not found",
            "type": "session checkin",
        }
    ]


@immobilus("2019-03-08 09:24:15.230")
def test_should_checkin_attendee_on_session_with_another_attendee_checked_in(
    memory_event_store, event_bus, authenticated_user
):
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
            .starting_at(datetime(2020, 3, 8, 11, 0))
            .with_attendee(clients[0].id)
            .with_attendee(clients[1].id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom = classrooms[0]
    SessionContextBuilderForTest().with_classroom(classroom).checkin(clients[0].id).at(
        datetime(2020, 3, 8, 11, 0)
    ).persist(RepositoryProvider.write_repositories.session).build()

    response: Response = client.post(
        "/sessions/checkin",
        json=SessionCheckinJsonBuilderForTest()
        .for_classroom(classroom)
        .for_attendee(clients[1]._id)
        .at(datetime(2020, 3, 8, 11, 0))
        .build(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_session_response(
        ANY,
        str(classroom.id),
        classroom,
        "2020-03-08T11:00:00+00:00",
        "2020-03-08T12:00:00+00:00",
        [
            {
                "id": str(clients[0].id),
                "firstname": clients[0].firstname,
                "lastname": clients[0].lastname,
                "attendance": "CHECKED_IN",
                "credits": {"amount": __client_credits(clients[0]).value},
            },
            {
                "id": str(clients[1].id),
                "firstname": clients[1].firstname,
                "lastname": clients[1].lastname,
                "attendance": "CHECKED_IN",
                "credits": {"amount": __client_credits(clients[1]).value},
            },
        ],
    )


@immobilus("2021-09-02 10:00:00")
def test_sessions_should_return_all_sessions_in_range(
    memory_repositories, event_bus, authenticated_user
):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_client(
            ClientBuilderForTest()
            .with_mat_credit(5)
            .with_credit(4, ClassroomSubject.MACHINE_DUO)
            .build()
        )
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    classroom_client = clients[0]
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest()
            .mat()
            .starting_at(datetime(2021, 9, 2, 10, 0))
            .ending_at(datetime(2021, 9, 16, 10, 0))
            .with_attendee(classroom_client.id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )

    response: Response = client.get(
        "/sessions?start_date=2021-09-02T00:00:00Z&end_date=2021-09-09T23:59:59Z"
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.headers["X-Link"]
        == '</sessions?start_date=2021-08-26T00%3A00%3A00%2B00%3A00&end_date=2021-09-01T23%3A59%3A59%2B00%3A00>; rel="previous", '
        '</sessions?start_date=2021-09-02T00%3A00%3A00%2B00%3A00&end_date=2021-09-09T23%3A59%3A59%2B00%3A00>; rel="current", '
        '</sessions?start_date=2021-09-10T00%3A00%3A00%2B00%3A00&end_date=2021-09-17T23%3A59%3A59%2B00%3A00>; rel="next"'
    )
    assert response.json() == [
        expected_session_response(
            None,
            str(classrooms[0].id),
            classrooms[0],
            "2021-09-02T10:00:00+00:00",
            "2021-09-02T11:00:00+00:00",
            [
                {
                    "id": str(classroom_client.id),
                    "firstname": classroom_client.firstname,
                    "lastname": classroom_client.lastname,
                    "attendance": "REGISTERED",
                    "credits": {"amount": __client_credits(clients[0]).value},
                }
            ],
        ),
        expected_session_response(
            None,
            str(classrooms[0].id),
            classrooms[0],
            "2021-09-09T10:00:00+00:00",
            "2021-09-09T11:00:00+00:00",
            [
                {
                    "id": str(classroom_client.id),
                    "firstname": classroom_client.firstname,
                    "lastname": classroom_client.lastname,
                    "attendance": "REGISTERED",
                    "credits": {"amount": __client_credits(clients[0]).value},
                }
            ],
        ),
    ]


@immobilus("2021-09-25 10:00:00", tz_offset=2)
def test_sessions_should_return_all_sessions_from_classroom_for_current_month(
    memory_repositories, event_bus, authenticated_user
):
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest()
            .starting_at(datetime(2021, 8, 13, 10, 0))
            .ending_at(datetime(2022, 6, 16, 10, 0))
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )

    response: Response = client.get(
        "/sessions?start_date=2021-10-01T00:00:00&end_date=2021-10-31T23:59:59"
    )

    assert (
        response.headers["X-Link"]
        == '</sessions?start_date=2021-09-01T00%3A00%3A00%2B00%3A00&end_date=2021-09-30T23%3A59%3A59%2B00%3A00>; rel="previous", '
        '</sessions?start_date=2021-10-01T00%3A00%3A00%2B00%3A00&end_date=2021-10-31T23%3A59%3A59%2B00%3A00>; rel="current", '
        '</sessions?start_date=2021-11-01T00%3A00%3A00%2B00%3A00&end_date=2021-11-30T23%3A59%3A59%2B00%3A00>; rel="next"'
    )
    assert response.json() == [
        expected_session_response(
            None,
            str(classrooms[0].id),
            classrooms[0],
            "2021-10-01T10:00:00+00:00",
            "2021-10-01T11:00:00+00:00",
            [],
        ),
        expected_session_response(
            None,
            str(classrooms[0].id),
            classrooms[0],
            "2021-10-08T10:00:00+00:00",
            "2021-10-08T11:00:00+00:00",
            [],
        ),
        expected_session_response(
            None,
            str(classrooms[0].id),
            classrooms[0],
            "2021-10-15T10:00:00+00:00",
            "2021-10-15T11:00:00+00:00",
            [],
        ),
        expected_session_response(
            None,
            str(classrooms[0].id),
            classrooms[0],
            "2021-10-22T10:00:00+00:00",
            "2021-10-22T11:00:00+00:00",
            [],
        ),
        expected_session_response(
            None,
            str(classrooms[0].id),
            classrooms[0],
            "2021-10-29T10:00:00+00:00",
            "2021-10-29T11:00:00+00:00",
            [],
        ),
    ]


def test_register_checkout(memory_repositories, event_bus, authenticated_user):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(3)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classrooms(
            ClassroomBuilderForTest()
            .starting_at(arrow.get("2019-05-07T10:00:00+05:00").datetime)
            .with_attendee(clients[0]._id)
            .with_attendee(clients[1]._id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom: Classroom = classrooms[0]
    repository, session = (
        SessionContextBuilderForTest()
        .with_classroom(classroom)
        .checkin(clients[0].id)
        .at(arrow.get("2019-05-14T10:00:00+05:00").datetime)
        .persist(RepositoryProvider.write_repositories.session)
        .build()
    )

    response: Response = client.post(
        f"/sessions/{str(session.id)}/checkout", json={"attendee": str(clients[0].id)}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_session_response(
        str(session.id),
        str(classroom.id),
        classroom,
        "2019-05-14T10:00:00+05:00",
        "2019-05-14T11:00:00+05:00",
        [
            {
                "id": str(clients[0].id),
                "firstname": clients[0].firstname,
                "lastname": clients[0].lastname,
                "attendance": "REGISTERED",
                "credits": {"amount": __client_credits(clients[0]).value},
            },
            {
                "id": str(clients[1].id),
                "firstname": clients[1].firstname,
                "lastname": clients[1].lastname,
                "attendance": "REGISTERED",
                "credits": {"amount": __client_credits(clients[1]).value},
            },
        ],
    )


def test_should_handle_attendee_that_cannot_checkout(authenticated_user):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(3)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classrooms(
            ClassroomBuilderForTest()
            .starting_at(arrow.get("2019-05-07T10:00:00+05:00").datetime)
            .with_attendee(clients[0]._id)
            .with_attendee(clients[1]._id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom: Classroom = classrooms[0]
    repository, session = (
        SessionContextBuilderForTest()
        .with_classroom(classroom)
        .checkin(clients[0].id)
        .at(arrow.get("2019-05-14T10:00:00+05:00").datetime)
        .persist(RepositoryProvider.write_repositories.session)
        .build()
    )
    unknown_attendee_id = uuid.uuid4()

    response: Response = client.post(
        f"/sessions/{str(session.id)}/checkout",
        json={"attendee": str(unknown_attendee_id)},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == [
        {
            "msg": f"Attendee with id {str(unknown_attendee_id)} could not be checked out",
            "type": "session checkout",
        }
    ]


@immobilus("2019-05-07 08:24:15.230")
def test_register_cancellation(memory_repositories, event_bus, authenticated_user):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(3)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classrooms(
            ClassroomBuilderForTest()
            .starting_at(arrow.get("2019-05-07T10:00:00+00:00").datetime)
            .with_attendee(clients[0]._id)
            .with_attendee(clients[1]._id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )

    classroom: Classroom = classrooms[0]
    response: Response = client.post(
        f"/sessions/cancellation/{clients[1].id}",
        json=AttendeeSessionCancellationJsonBuilderForTest()
        .for_classroom(classroom)
        .at(arrow.get("2019-05-21T10:00:00+00:00").datetime)
        .build(),
    )

    assert classroom.attendees[0].attendance == Attendance.REGISTERED
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_session_response(
        ANY,
        str(classroom.id),
        classroom,
        "2019-05-21T10:00:00+00:00",
        "2019-05-21T11:00:00+00:00",
        [
            {
                "id": str(clients[0].id),
                "firstname": clients[0].firstname,
                "lastname": clients[0].lastname,
                "attendance": "REGISTERED",
                "credits": {"amount": __client_credits(clients[0]).value},
            }
        ],
    )


def test_should_return_not_found_session_on_attendee_cancellation(authenticated_user):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(3)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classrooms(
            ClassroomBuilderForTest()
            .starting_at(arrow.get("2020-05-12T10:00:00+00:00").datetime)
            .with_attendee(clients[0]._id)
            .with_attendee(clients[1]._id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom: Classroom = classrooms[0]
    session_cancellation_json = (
        AttendeeSessionCancellationJsonBuilderForTest()
        .for_classroom(classroom)
        .at(arrow.get("2020-05-19T10:00:30+00:00").datetime)
        .build()
    )

    response: Response = client.post(
        f"/sessions/cancellation/{clients[1].id}",
        json=session_cancellation_json,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == [
        {
            "msg": "Cannot cancel attendee for the session starting at 2020-05-19T10:00:30+00:00. Session could not be found",
            "type": "attendee session cancellation",
        }
    ]


def test_should_return_classroom_not_found_on_attendee_cancellation(authenticated_user):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(3)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    classroom: Classroom = (
        ClassroomBuilderForTest()
        .starting_at(arrow.get("2020-05-12T10:00:00+00:00").datetime)
        .with_attendee(clients[0]._id)
        .build()
    )
    session_cancellation_json = (
        AttendeeSessionCancellationJsonBuilderForTest()
        .for_classroom(classroom)
        .at(arrow.get("2020-05-19T10:00:00+00:00").datetime)
        .build()
    )

    response: Response = client.post(
        f"/sessions/cancellation/{clients[0].id}",
        json=session_cancellation_json,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == [
        {
            "msg": f"Classroom with id '{classroom.id}' not found",
            "type": "attendee session cancellation",
        }
    ]


@immobilus("2019-03-08 09:24:15.230")
def test_should_add_attendees(memory_repositories, event_bus, authenticated_user):
    client_repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(2)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classroom(
            ClassroomBuilderForTest().starting_at(datetime(2020, 3, 8, 11, 0))
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    classroom = classrooms[0]

    response: Response = client.post(
        "/sessions/attendees",
        json=SessionAddAttendeesJsonBuilderForTest()
        .for_classroom(classroom)
        .for_attendee(clients[1]._id)
        .at(datetime(2020, 3, 8, 11, 0))
        .build(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_session_response(
        ANY,
        str(classroom.id),
        classroom,
        "2020-03-08T11:00:00+00:00",
        "2020-03-08T12:00:00+00:00",
        [
            {
                "id": str(clients[1].id),
                "firstname": clients[1].firstname,
                "lastname": clients[1].lastname,
                "attendance": "REGISTERED",
                "credits": {"amount": __client_credits(clients[1]).value},
            },
        ],
    )


@immobilus("2022-11-15 10:20:15")
def test_should_return_400_if_session_not_at_expected_time(authenticated_user):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_client(ClientBuilderForTest().build())
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classrooms(
            ClassroomBuilderForTest()
            .starting_at(arrow.get("2022-11-15T11:00:00+03:00").datetime)
            .ending_at(arrow.get("2022-11-15T12:00:00+03:00").datetime)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )

    response: Response = client.post(
        "/sessions/attendees",
        json=SessionAddAttendeesJsonBuilderForTest()
        .for_classroom(classrooms[0])
        .for_attendee(clients[0]._id)
        .at(datetime.now())
        .build(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == [
        {
            "msg": "Cannot add attendees for the session starting at 2022-11-15T10:20:15+00:00.",
            "type": "add attendees to session",
        }
    ]


@immobilus("2022-11-15 10:20:15.230")
def test_should_not_validate_if_too_much_attendees_given(authenticated_user):
    repository, clients = (
        ClientContextBuilderForTest()
        .with_clients(4)
        .persist(RepositoryProvider.write_repositories.client)
        .build()
    )
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classrooms(
            ClassroomBuilderForTest()
            .starting_at(arrow.get("2022-11-15T11:00:00+03:00").datetime)
            .ending_at(arrow.get("2022-11-15T12:00:00+03:00").datetime)
            .with_position(1)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )

    response: Response = client.post(
        "/sessions/attendees",
        json=SessionAddAttendeesJsonBuilderForTest()
        .for_classroom(classrooms[0])
        .for_attendee(clients[0]._id)
        .for_attendee(clients[1]._id)
        .at(arrow.get("2022-11-15T11:00:00+03:00").datetime)
        .build(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == [
        {
            "msg": "Cannot add attendees for the session starting at '2022-11-15T11:00:00+03:00', there is 1 position(s) available, you tried to add 2 attendee(s)",
            "type": "add attendees to session",
        }
    ]


def __client_credits(client: Client):
    return client.credits[0]
