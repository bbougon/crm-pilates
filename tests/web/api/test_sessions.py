import uuid
from datetime import datetime
from http import HTTPStatus

import arrow
import pytest
import pytz
from fastapi import Response, HTTPException, status
from immobilus import immobilus
from mock.mock import ANY

from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.domain.client.client import Client
from crm_pilates.domain.exceptions import AggregateNotFoundException
from crm_pilates.infrastructure.repository.memory.memory_classroom_repositories import (
    MemoryClassroomRepository,
)
from crm_pilates.infrastructure.repository_provider import RepositoryProvider
from tests.builders.builders_for_test import (
    SessionCheckinJsonBuilderForTest,
    ClientContextBuilderForTest,
    ClassroomContextBuilderForTest,
    ClassroomBuilderForTest,
    SessionContextBuilderForTest,
    AttendeeSessionCancellationJsonBuilderForTest,
    ClientBuilderForTest,
)
from tests.builders.providers_for_test import CommandBusProviderForTest
from tests.helpers.helpers import expected_session_response
from crm_pilates.web.api.session import (
    session_checkin,
    next_sessions,
    sessions,
    session_checkout,
    attendee_session_cancellation,
)
from crm_pilates.web.presentation.domain.detailed_attendee import (
    DetailedAttendee,
    AvailableCredits,
)
from crm_pilates.web.schema.session_schemas import (
    SessionCheckin,
    SessionCheckout,
    AttendeeSessionCancellation,
)


def test_should_handle_domain_exception_on_invalid_confirmed_session():
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
    response = Response()
    session_checkin_json = SessionCheckin.parse_obj(
        SessionCheckinJsonBuilderForTest()
        .for_classroom(classroom)
        .for_attendee(clients[0].id)
        .at(datetime(2019, 5, 8, 10, 30))
        .build()
    )

    try:
        session_checkin(
            session_checkin_json, response, CommandBusProviderForTest().provide()
        )
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == [
            {
                "msg": f"Classroom '{classroom.name}' starting at '2019-05-07T10:00:00+00:00' cannot be set at '2019-05-08T10:30:00+00:00', closest possible dates are '2019-05-07T10:00:00+00:00' or '2019-05-14T10:00:00+00:00'",
                "type": "session_checkin",
            }
        ]


def test_should_handle_aggregate_not_found_exception_on_checkin(mocker):
    classroom_id = uuid.uuid4()
    mocker.patch.object(
        MemoryClassroomRepository,
        "get_by_id",
        side_effect=AggregateNotFoundException(classroom_id, "Classroom"),
    )
    session_checkin_json = SessionCheckin.parse_obj(
        SessionCheckinJsonBuilderForTest()
        .for_classroom_id(classroom_id)
        .for_attendee(uuid.uuid4())
        .at(datetime(2019, 5, 8, 10, 30))
        .build()
    )
    try:
        session_checkin(
            session_checkin_json, Response(), CommandBusProviderForTest().provide()
        )
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND
        assert e.detail == [
            {
                "msg": f"Classroom with id '{str(classroom_id)}' not found",
                "type": "session_checkin",
            }
        ]


@immobilus(pytz.timezone("Europe/Paris").localize(datetime(2020, 3, 19, 8, 24)))
def test_get_next_sessions_with_confirmed_sessions():
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
            .starting_at(datetime(2020, 3, 19, 10))
            .with_attendee(clients[0]._id)
            .with_attendee(clients[1]._id),
            ClassroomBuilderForTest()
            .starting_at(datetime(2020, 3, 12, 11))
            .ending_at(datetime(2020, 6, 25, 12))
            .with_attendee(clients[2]._id),
            ClassroomBuilderForTest().starting_at(datetime(2020, 3, 20, 10)),
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    session_repository, session = (
        SessionContextBuilderForTest()
        .with_classroom(classrooms[1])
        .at(datetime(2020, 3, 19, 11))
        .persist(RepositoryProvider.write_repositories.session)
        .build()
    )

    response = next_sessions(CommandBusProviderForTest().provide())

    first_classroom = classrooms[0]
    second_classroom = classrooms[1]
    assert response == [
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2020-03-19T10:00:00+00:00",
            "2020-03-19T11:00:00+00:00",
            [
                DetailedAttendee(
                    clients[0].id,
                    clients[0].firstname,
                    clients[0].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[0], first_classroom.subject),
                ),
                DetailedAttendee(
                    clients[1].id,
                    clients[1].firstname,
                    clients[1].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[1], first_classroom.subject),
                ),
            ],
        ),
        expected_session_response(
            session.id,
            second_classroom.id,
            second_classroom,
            "2020-03-19T11:00:00+00:00",
            "2020-03-19T12:00:00+00:00",
            [
                DetailedAttendee(
                    clients[2].id,
                    clients[2].firstname,
                    clients[2].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[2], session.subject),
                )
            ],
        ),
    ]


@immobilus("2021-09-05 08:24:15.230")
def test_sessions_should_return_sessions_in_current_month_range():
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
            .starting_at(datetime(2021, 9, 2, 10))
            .ending_at(datetime(2022, 6, 25, 11))
            .with_attendee(clients[0]._id)
            .with_attendee(clients[1]._id),
            ClassroomBuilderForTest()
            .starting_at(datetime(2021, 9, 18, 11))
            .ending_at(datetime(2022, 6, 25, 12))
            .with_attendee(clients[2]._id),
            ClassroomBuilderForTest()
            .starting_at(datetime(2021, 10, 1, 10))
            .ending_at(datetime(2022, 6, 25, 11)),
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    session_repository, confirmed_session = (
        SessionContextBuilderForTest()
        .with_classroom(classrooms[1])
        .at(datetime(2021, 9, 25, 11))
        .persist(RepositoryProvider.write_repositories.session)
        .build()
    )

    response = Response()
    result = sessions(response, CommandBusProviderForTest().provide())

    assert (
        response.headers["X-Link"]
        == '</sessions?start_date=2021-08-01T00%3A00%3A00%2B00%3A00&end_date=2021-08-31T23%3A59%3A59%2B00%3A00>; rel="previous", '
        '</sessions?start_date=2021-09-01T00%3A00%3A00%2B00%3A00&end_date=2021-09-30T23%3A59%3A59%2B00%3A00>; rel="current", '
        '</sessions?start_date=2021-10-01T00%3A00%3A00%2B00%3A00&end_date=2021-10-31T23%3A59%3A59%2B00%3A00>; rel="next"'
    )
    first_classroom = classrooms[0]
    second_classroom = classrooms[1]
    assert result == [
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-09-02T10:00:00+00:00",
            "2021-09-02T11:00:00+00:00",
            [
                DetailedAttendee(
                    clients[0].id,
                    clients[0].firstname,
                    clients[0].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[0], first_classroom.subject),
                ),
                DetailedAttendee(
                    clients[1].id,
                    clients[1].firstname,
                    clients[1].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[1], first_classroom.subject),
                ),
            ],
        ),
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-09-09T10:00:00+00:00",
            "2021-09-09T11:00:00+00:00",
            [
                DetailedAttendee(
                    clients[0].id,
                    clients[0].firstname,
                    clients[0].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[0], first_classroom.subject),
                ),
                DetailedAttendee(
                    clients[1].id,
                    clients[1].firstname,
                    clients[1].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[1], first_classroom.subject),
                ),
            ],
        ),
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-09-16T10:00:00+00:00",
            "2021-09-16T11:00:00+00:00",
            [
                DetailedAttendee(
                    clients[0].id,
                    clients[0].firstname,
                    clients[0].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[0], first_classroom.subject),
                ),
                DetailedAttendee(
                    clients[1].id,
                    clients[1].firstname,
                    clients[1].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[1], first_classroom.subject),
                ),
            ],
        ),
        expected_session_response(
            None,
            second_classroom.id,
            second_classroom,
            "2021-09-18T11:00:00+00:00",
            "2021-09-18T12:00:00+00:00",
            [
                DetailedAttendee(
                    clients[2].id,
                    clients[2].firstname,
                    clients[2].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[2], second_classroom.subject),
                )
            ],
        ),
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-09-23T10:00:00+00:00",
            "2021-09-23T11:00:00+00:00",
            [
                DetailedAttendee(
                    clients[0].id,
                    clients[0].firstname,
                    clients[0].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[0], first_classroom.subject),
                ),
                DetailedAttendee(
                    clients[1].id,
                    clients[1].firstname,
                    clients[1].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[1], first_classroom.subject),
                ),
            ],
        ),
        expected_session_response(
            confirmed_session.id,
            second_classroom.id,
            second_classroom,
            "2021-09-25T11:00:00+00:00",
            "2021-09-25T12:00:00+00:00",
            [
                DetailedAttendee(
                    clients[2].id,
                    clients[2].firstname,
                    clients[2].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[2], confirmed_session.subject),
                )
            ],
        ),
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-09-30T10:00:00+00:00",
            "2021-09-30T11:00:00+00:00",
            [
                DetailedAttendee(
                    clients[0].id,
                    clients[0].firstname,
                    clients[0].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[0], first_classroom.subject),
                ),
                DetailedAttendee(
                    clients[1].id,
                    clients[1].firstname,
                    clients[1].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[1], first_classroom.subject),
                ),
            ],
        ),
    ]


@immobilus("2021-09-05 08:24:15.230")
def test_sessions_should_return_sessions_in_december_and_link_in_january():
    repository, classrooms = (
        ClassroomContextBuilderForTest()
        .with_classrooms(
            ClassroomBuilderForTest()
            .starting_at(datetime(2021, 9, 2, 10))
            .ending_at(datetime(2022, 6, 25, 11))
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )

    response = Response()
    result = sessions(
        response,
        CommandBusProviderForTest().provide(),
        datetime(2021, 12, 1),
        datetime(2021, 12, 31, 23, 59, 59),
    )

    assert (
        response.headers["X-Link"]
        == '</sessions?start_date=2021-11-01T00%3A00%3A00%2B00%3A00&end_date=2021-11-30T23%3A59%3A59%2B00%3A00>; rel="previous", '
        '</sessions?start_date=2021-12-01T00%3A00%3A00%2B00%3A00&end_date=2021-12-31T23%3A59%3A59%2B00%3A00>; rel="current", '
        '</sessions?start_date=2022-01-01T00%3A00%3A00%2B00%3A00&end_date=2022-01-31T23%3A59%3A59%2B00%3A00>; rel="next"'
    )
    first_classroom = classrooms[0]
    assert result == [
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-12-02T10:00:00+00:00",
            "2021-12-02T11:00:00+00:00",
            [],
        ),
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-12-09T10:00:00+00:00",
            "2021-12-09T11:00:00+00:00",
            [],
        ),
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-12-16T10:00:00+00:00",
            "2021-12-16T11:00:00+00:00",
            [],
        ),
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-12-23T10:00:00+00:00",
            "2021-12-23T11:00:00+00:00",
            [],
        ),
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-12-30T10:00:00+00:00",
            "2021-12-30T11:00:00+00:00",
            [],
        ),
    ]


@immobilus("2021-09-05 08:24:15.230")
def test_sessions_should_return_sessions_according_to_time_zone():
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
            .starting_at(arrow.get("2021-09-02T10:00:00+03:00").datetime)
            .ending_at(arrow.get("2022-06-25T11:00:00+03:00").datetime)
            .with_attendee(clients[0]._id)
            .with_attendee(clients[1]._id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )

    response = Response()
    result = sessions(
        response,
        CommandBusProviderForTest().provide(),
        start_date=datetime(2021, 9, 2, tzinfo=pytz.timezone("Europe/Moscow")),
        end_date=datetime(
            2021, 9, 9, 23, 59, 59, tzinfo=pytz.timezone("Europe/Moscow")
        ),
    )

    assert (
        response.headers["X-Link"]
        == '</sessions?start_date=2021-08-26T00%3A00%3A00%2B03%3A00&end_date=2021-09-01T23%3A59%3A59%2B03%3A00>; rel="previous", '
        '</sessions?start_date=2021-09-02T00%3A00%3A00%2B03%3A00&end_date=2021-09-09T23%3A59%3A59%2B03%3A00>; rel="current", '
        '</sessions?start_date=2021-09-10T00%3A00%3A00%2B03%3A00&end_date=2021-09-17T23%3A59%3A59%2B03%3A00>; rel="next"'
    )
    first_classroom = classrooms[0]
    assert result == [
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-09-02T10:00:00+03:00",
            "2021-09-02T11:00:00+03:00",
            [
                DetailedAttendee(
                    clients[0].id,
                    clients[0].firstname,
                    clients[0].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[0], first_classroom.subject),
                ),
                DetailedAttendee(
                    clients[1].id,
                    clients[1].firstname,
                    clients[1].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[1], first_classroom.subject),
                ),
            ],
        ),
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2021-09-09T10:00:00+03:00",
            "2021-09-09T11:00:00+03:00",
            [
                DetailedAttendee(
                    clients[0].id,
                    clients[0].firstname,
                    clients[0].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[0], first_classroom.subject),
                ),
                DetailedAttendee(
                    clients[1].id,
                    clients[1].firstname,
                    clients[1].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[1], first_classroom.subject),
                ),
            ],
        ),
    ]


@immobilus(pytz.timezone("Europe/Paris").localize(datetime(2020, 3, 19, 8, 24, 15)))
def test_get_next_sessions_with_time_zone():
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
            .starting_at(arrow.get("2020-03-19T10:00:00+03:00").datetime)
            .with_attendee(clients[0]._id)
            .with_attendee(clients[1]._id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )

    response = next_sessions(CommandBusProviderForTest().provide())

    first_classroom = classrooms[0]
    assert response == [
        expected_session_response(
            None,
            first_classroom.id,
            first_classroom,
            "2020-03-19T10:00:00+03:00",
            "2020-03-19T11:00:00+03:00",
            [
                DetailedAttendee(
                    clients[0].id,
                    clients[0].firstname,
                    clients[0].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[0], first_classroom.subject),
                ),
                DetailedAttendee(
                    clients[1].id,
                    clients[1].firstname,
                    clients[1].lastname,
                    "REGISTERED",
                    __to_available_credits(clients[1], first_classroom.subject),
                ),
            ],
        )
    ]


def test_confirm_session_on_timezone():
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
    session_checkin_json = SessionCheckin.parse_obj(
        SessionCheckinJsonBuilderForTest()
        .for_classroom(classroom)
        .for_attendee(clients[0].id)
        .at(arrow.get("2019-05-14T10:00:00+05:00").datetime)
        .build()
    )

    response = session_checkin(
        session_checkin_json, Response(), CommandBusProviderForTest().provide()
    )

    assert response == expected_session_response(
        ANY,
        classroom.id,
        classroom,
        "2019-05-14T10:00:00+05:00",
        "2019-05-14T11:00:00+05:00",
        [
            DetailedAttendee(
                clients[0].id,
                clients[0].firstname,
                clients[0].lastname,
                "CHECKED_IN",
                __to_available_credits(clients[0], classroom.subject),
            ),
            DetailedAttendee(
                clients[1].id,
                clients[1].firstname,
                clients[1].lastname,
                "REGISTERED",
                __to_available_credits(clients[1], classroom.subject),
            ),
        ],
    )


def test_should_checkout_attendee():
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
    session_checkout_json = SessionCheckout.parse_obj({"attendee": clients[0].id})

    response = session_checkout(
        session.id, session_checkout_json, CommandBusProviderForTest().provide()
    )

    assert response == expected_session_response(
        session.id,
        classroom.id,
        classroom,
        "2019-05-14T10:00:00+05:00",
        "2019-05-14T11:00:00+05:00",
        [
            DetailedAttendee(
                clients[0].id,
                clients[0].firstname,
                clients[0].lastname,
                "REGISTERED",
                __to_available_credits(clients[0], session.subject),
            ),
            DetailedAttendee(
                clients[1].id,
                clients[1].firstname,
                clients[1].lastname,
                "REGISTERED",
                __to_available_credits(clients[1], session.subject),
            ),
        ],
    )


def test_should_handle_unexisting_session_on_checkout():
    session_checkout_json = SessionCheckout.parse_obj({"attendee": uuid.uuid4()})
    session_id = uuid.uuid4()

    with pytest.raises(HTTPException) as e:
        session_checkout(
            session_id, session_checkout_json, CommandBusProviderForTest().provide()
        )

    assert e.value.status_code == HTTPStatus.NOT_FOUND
    assert e.value.detail == [
        {
            "msg": f"Session with id '{str(session_id)}' not found",
            "type": "session_checkout",
        }
    ]


def test_should_handle_attendee_that_cannot_checkout():
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
    session_checkout_json = SessionCheckout.parse_obj({"attendee": unknown_attendee_id})

    with pytest.raises(HTTPException) as e:
        session_checkout(
            session.id, session_checkout_json, CommandBusProviderForTest().provide()
        )

    assert e.value.status_code == HTTPStatus.BAD_REQUEST
    assert e.value.detail == [
        {
            "msg": f"Attendee with id {str(unknown_attendee_id)} could not be checked out",
            "type": "session_checkout",
        }
    ]


def test_should_cancel_attendee():
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
    session_cancellation_json = AttendeeSessionCancellation.parse_obj(
        AttendeeSessionCancellationJsonBuilderForTest()
        .for_classroom(classroom)
        .at(arrow.get("2020-05-19T10:00:00+00:00").datetime)
        .build()
    )

    response = attendee_session_cancellation(
        clients[0].id,
        session_cancellation_json,
        Response(),
        CommandBusProviderForTest().provide(),
    )

    assert response == expected_session_response(
        ANY,
        classroom.id,
        classroom,
        "2020-05-19T10:00:00+00:00",
        "2020-05-19T11:00:00+00:00",
        [
            DetailedAttendee(
                clients[1].id,
                clients[1].firstname,
                clients[1].lastname,
                "REGISTERED",
                __to_available_credits(clients[1], classroom.subject),
            )
        ],
    )


def test_should_handle_unexisting_session_on_attendee_cancellation():
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
    session_cancellation_json = AttendeeSessionCancellation.parse_obj(
        AttendeeSessionCancellationJsonBuilderForTest()
        .for_classroom(classroom)
        .at(arrow.get("2020-05-19T10:00:30+00:00").datetime)
        .build()
    )

    with pytest.raises(HTTPException) as e:
        attendee_session_cancellation(
            clients[0].id,
            session_cancellation_json,
            Response(),
            CommandBusProviderForTest().provide(),
        )

    assert e.value.status_code == HTTPStatus.NOT_FOUND
    assert e.value.detail == [
        {
            "msg": "Cannot cancel attendee for the session starting at 2020-05-19T10:00:30+00:00. Session could not be found",
            "type": "attendee_session_cancellation",
        }
    ]


def test_should_handle_unexisting_classroom_on_attendee_cancellation():
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
    session_cancellation_json = AttendeeSessionCancellation.parse_obj(
        AttendeeSessionCancellationJsonBuilderForTest()
        .for_classroom(classroom)
        .at(arrow.get("2020-05-19T10:00:00+00:00").datetime)
        .build()
    )

    with pytest.raises(HTTPException) as e:
        attendee_session_cancellation(
            clients[0].id,
            session_cancellation_json,
            Response(),
            CommandBusProviderForTest().provide(),
        )

    assert e.value.status_code == HTTPStatus.NOT_FOUND
    assert e.value.detail == [
        {
            "msg": f"Aggregate 'Classroom' with id '{classroom.id}' not found",
            "type": "attendee_session_cancellation",
        }
    ]


@immobilus("2019-07-05 10:20:15.230")
def test_should_return_sessions_for_uncredited_attendees():
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
            .starting_at(arrow.get("2019-07-05T11:00:00+03:00").datetime)
            .ending_at(arrow.get("2019-07-05T12:00:00+03:00").datetime)
            .with_attendee(clients[0]._id)
        )
        .persist(RepositoryProvider.write_repositories.classroom)
        .build()
    )
    response = Response()

    result = sessions(
        response,
        CommandBusProviderForTest().provide(),
        start_date=datetime(2019, 7, 5, tzinfo=pytz.timezone("Europe/Moscow")),
        end_date=datetime(
            2019, 7, 5, 23, 59, 59, tzinfo=pytz.timezone("Europe/Moscow")
        ),
    )

    classroom = classrooms[0]
    assert result == [
        expected_session_response(
            None,
            classroom.id,
            classroom,
            "2019-07-05T11:00:00+03:00",
            "2019-07-05T12:00:00+03:00",
            [
                DetailedAttendee(
                    clients[0].id,
                    clients[0].firstname,
                    clients[0].lastname,
                    "REGISTERED",
                    None,
                )
            ],
        )
    ]


def __to_available_credits(
    client: Client, subject: ClassroomSubject
) -> AvailableCredits:
    _credits = next(
        filter(lambda credit: credit.subject is subject, client.credits), None
    )
    return AvailableCredits(_credits.subject.value, _credits.value)
