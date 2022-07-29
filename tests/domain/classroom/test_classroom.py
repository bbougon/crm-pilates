import uuid
from datetime import datetime

import pytest
import pytz
from immobilus import immobilus

from crm_pilates.domain.classroom.classroom import (
    Classroom,
    ScheduledSession,
    ConfirmedSession,
    InvalidSessionStartDateException,
    Session,
)
from crm_pilates.domain.classroom.attendee import Attendee
from crm_pilates.domain.classroom.classroom_type import ClassroomSubject
from crm_pilates.domain.classroom.duration import Duration, HourTimeUnit, MinuteTimeUnit
from crm_pilates.domain.exceptions import DomainException


def test_create_should_create_a_classroom_with_1_hour_duration():
    classroom = Classroom.create(
        "mat class room", datetime(2020, 1, 2, 10, 0), 2, ClassroomSubject.MAT
    )

    assert classroom.schedule.start == datetime(2020, 1, 2, 10, 0)
    assert classroom.schedule.stop == datetime(2020, 1, 2, 11, 0)
    assert classroom.duration == Duration(HourTimeUnit(1))
    assert classroom.subject == ClassroomSubject.MAT


def test_classroom_should_have_a_duration_in_minutes():
    classroom = Classroom.create(
        "machine beginners",
        datetime(2021, 5, 3),
        2,
        ClassroomSubject.MACHINE_DUO,
        duration=Duration(MinuteTimeUnit(45)),
    )

    assert classroom.duration == Duration(MinuteTimeUnit(45))


def test_classroom_should_be_scheduled():
    classroom = Classroom.create(
        "machine",
        datetime(2020, 3, 19),
        3,
        ClassroomSubject.MACHINE_TRIO,
        stop_date=datetime(2020, 6, 19),
    )

    assert classroom.schedule.start == datetime(2020, 3, 19)
    assert classroom.schedule.stop == datetime(2020, 6, 19)


def test_should_not_add_attendees_when_position_overflown():
    classroom = Classroom.create(
        "machine",
        datetime(2020, 3, 19),
        1,
        ClassroomSubject.MACHINE_PRIVATE,
        stop_date=datetime(2020, 6, 19),
    )
    with pytest.raises(DomainException) as e:
        classroom.all_attendees(
            [Attendee.create(uuid.uuid4()), Attendee.create(uuid.uuid4())]
        )

    assert (
        e.value.message
        == "Cannot add anymore attendees (position available: 1 - attendee(s) you try to add: 2)"
    )


@immobilus("2020-9-24 08:24:15.230")
def test_should_retrieve_next_classroom_session():
    classroom = Classroom.create(
        "next session",
        datetime(2020, 9, 10, 10),
        2,
        ClassroomSubject.MACHINE_DUO,
        stop_date=datetime(2021, 6, 10, 11),
    )

    session: ScheduledSession = classroom.next_session()

    assert session
    assert session.name == "next session"
    assert session.start == datetime(2020, 9, 24, 10, tzinfo=pytz.utc)
    assert session.stop == datetime(2020, 9, 24, 11, tzinfo=pytz.utc)
    assert session.position == 2
    assert len(session.attendees) == 0


@immobilus("2020-9-24 08:24:15.230")
def test_should_retrieve_next_classroom_session_with_duration():
    classroom = Classroom.create(
        "next session",
        datetime(2020, 9, 10, 10),
        2,
        ClassroomSubject.MACHINE_DUO,
        stop_date=datetime(2021, 6, 10, 10),
        duration=Duration(MinuteTimeUnit(45)),
    )

    session: ScheduledSession = classroom.next_session()

    assert session.stop == datetime(2020, 9, 24, 10, 45, tzinfo=pytz.utc)


@immobilus("2020-9-23 08:24:15.230")
def test_should_not_retrieve_classroom_next_session_if_no_session_today():
    classroom = Classroom.create(
        "next session",
        datetime(2020, 9, 10, 10),
        2,
        ClassroomSubject.MACHINE_DUO,
        stop_date=datetime(2021, 6, 10, 10),
    )

    assert classroom.next_session() is None


@immobilus("2021-08-22 08:24:15.230")
def test_should_retrieve_next_command_session_if_today_is_sunday_and_next_session_on_monday():
    classroom = Classroom.create(
        "next session",
        datetime(2021, 8, 23, 10),
        2,
        ClassroomSubject.MACHINE_DUO,
        stop_date=datetime(2022, 7, 12, 10),
    )

    assert classroom.next_session()


def test_should_confirm_session_with_scheduled_time():
    classroom: Classroom = Classroom.create(
        "classroom to be confirmed",
        datetime(2019, 6, 7, 10),
        2,
        ClassroomSubject.MACHINE_DUO,
        duration=Duration(MinuteTimeUnit(45)),
    )

    session: ConfirmedSession = classroom.confirm_session_at(datetime(2019, 6, 7, 10))

    assert session.stop == datetime(2019, 6, 7, 10, 45).astimezone(pytz.utc)


def test_should_not_confirm_session_with_invalid_date():
    with pytest.raises(InvalidSessionStartDateException) as e:
        classroom: Classroom = Classroom.create(
            "classroom to be confirmed",
            datetime(2019, 6, 7, 10),
            2,
            ClassroomSubject.MACHINE_DUO,
            duration=Duration(MinuteTimeUnit(45)),
        )
        classroom.confirm_session_at(datetime(2019, 6, 8, 10))

    assert (
        e.value.message
        == f"Classroom 'classroom to be confirmed' starting at '{classroom.schedule.start.isoformat()}' cannot be set at '{datetime(2019, 6, 8, 10).isoformat()}', closest possible dates are '{datetime(2019, 6, 7, 10, tzinfo=pytz.utc).isoformat()}' or '{datetime(2019, 6, 14, 10, tzinfo=pytz.utc).isoformat()}'"
    )


def test_should_not_confirm_session_with_invalid_date_and_time():
    with pytest.raises(InvalidSessionStartDateException) as e:
        classroom: Classroom = Classroom.create(
            "classroom to be confirmed",
            datetime(2020, 6, 1, 10),
            2,
            ClassroomSubject.MACHINE_DUO,
            duration=Duration(MinuteTimeUnit(45)),
        )
        classroom.confirm_session_at(datetime(2020, 6, 8, 10, 30))

    assert (
        e.value.message
        == f"Classroom 'classroom to be confirmed' starting at '{classroom.schedule.start.isoformat()}' cannot be set at '{datetime(2020, 6, 8, 10, 30).isoformat()}', closest possible dates are '{datetime(2020, 6, 8, 10, tzinfo=pytz.utc).isoformat()}' or '{datetime(2020, 6, 15, 10, tzinfo=pytz.utc).isoformat()}'"
    )


def test_should_not_confirm_session_with_date_prior_to_classroom_start_date():
    with pytest.raises(InvalidSessionStartDateException) as e:
        classroom: Classroom = Classroom.create(
            "classroom to be confirmed",
            datetime(2020, 6, 1, 10),
            2,
            ClassroomSubject.MACHINE_DUO,
            duration=Duration(MinuteTimeUnit(45)),
        )
        classroom.confirm_session_at(datetime(2020, 5, 25, 10, 0))

    assert (
        e.value.message
        == f"Classroom 'classroom to be confirmed' starting at '{classroom.schedule.start.isoformat()}' cannot be set before"
    )


def test_session_in_range_should_return_sessions_until_classroom_stops():
    classroom: Classroom = Classroom.create(
        "classroom",
        datetime(2020, 6, 1, 10),
        2,
        ClassroomSubject.MACHINE_DUO,
        datetime(2020, 7, 13, 10, 45),
        duration=Duration(MinuteTimeUnit(45)),
    )

    sessions: [Session] = classroom.sessions_in_range(
        datetime(2020, 7, 1), datetime(2020, 7, 31, 23, 59, 59)
    )

    assert len(sessions) == 2
    assert sessions[-1].start == datetime(2020, 7, 13, 10, tzinfo=pytz.utc)
    assert sessions[-1].stop == datetime(2020, 7, 13, 10, 45, tzinfo=pytz.utc)


def test_checkin_unknown_attendee_should_be_handled():
    classroom: Classroom = Classroom.create(
        "classroom to be confirmed",
        datetime(2019, 6, 7, 10),
        2,
        ClassroomSubject.MACHINE_DUO,
        duration=Duration(MinuteTimeUnit(45)),
    )
    session: ConfirmedSession = classroom.confirm_session_at(datetime(2019, 6, 7, 10))
    unknown_attendee_id = uuid.uuid4()

    with pytest.raises(DomainException) as e:
        session.checkin(Attendee.create(unknown_attendee_id))

    assert (
        e.value.message
        == f"Attendee with id {str(unknown_attendee_id)} could not be checked in"
    )


def test_checkout_unknown_attendee_should_be_handled():
    classroom: Classroom = Classroom.create(
        "classroom to be confirmed",
        datetime(2019, 6, 7, 10),
        2,
        ClassroomSubject.MACHINE_DUO,
        duration=Duration(MinuteTimeUnit(45)),
    )
    session: ConfirmedSession = classroom.confirm_session_at(datetime(2019, 6, 7, 10))
    unknown_attendee_id = uuid.uuid4()

    with pytest.raises(DomainException) as e:
        session.checkout(Attendee.create(unknown_attendee_id))

    assert (
        e.value.message
        == f"Attendee with id {str(unknown_attendee_id)} could not be checked out"
    )
