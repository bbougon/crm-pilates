import uuid
from datetime import datetime

import pytest
from immobilus import immobilus

from domain.classroom.classroom import Classroom, Attendee, ScheduledSession, ConfirmedSession
from domain.classroom.duration import Duration, HourTimeUnit, MinuteTimeUnit
from domain.exceptions import DomainException


def test_create_classroom():
    classroom = Classroom.create("mat class room", datetime(2020, 1, 2, 10, 0), 2)

    assert classroom.schedule.start == datetime(2020, 1, 2, 10, 0)
    assert not classroom.schedule.stop
    assert classroom.duration == Duration(HourTimeUnit(1))


def test_classroom_has_a_duration_in_minutes():
    classroom = Classroom.create("machine beginners", datetime(2021, 5, 3), 2,
                                 duration=Duration(MinuteTimeUnit(45)))

    assert classroom.duration == Duration(MinuteTimeUnit(45))


def test_classroom_is_scheduled():
    classroom = Classroom.create("machine", datetime(2020, 3, 19), 4, stop_date=datetime(2020, 6, 19))

    assert classroom.schedule.start == datetime(2020, 3, 19)
    assert classroom.schedule.stop == datetime(2020, 6, 19)


def test_cannot_add_attendees_when_position_overflown():
    classroom = Classroom.create("machine", datetime(2020, 3, 19), 1, stop_date=datetime(2020, 6, 19))
    with pytest.raises(DomainException) as e:
        classroom.all_attendees([Attendee.create(uuid.uuid4()), Attendee.create(uuid.uuid4())])

    assert e.value.message == "Cannot add anymore attendees (position available: 1 - attendee(s) you try to add: 2)"


@immobilus("2020-9-24 08:24:15.230")
def test_retrieve_next_session():
    classroom = Classroom.create("next session", datetime(2020, 9, 10, 10), 2, stop_date=datetime(2021, 6, 10, 11))

    session: ScheduledSession = classroom.next_session()

    assert session
    assert session.name == "next session"
    assert session.start == datetime(2020, 9, 24, 10)
    assert session.stop == datetime(2020, 9, 24, 11)
    assert session.position == 2
    assert len(session.attendees) == 0


@immobilus("2020-9-24 08:24:15.230")
def test_retrieve_next_session_with_duration():
    classroom = Classroom.create("next session", datetime(2020, 9, 10, 10), 2, stop_date=datetime(2021, 6, 10, 10),
                                 duration=Duration(MinuteTimeUnit(45)))

    session: ScheduledSession = classroom.next_session()

    assert session.stop == datetime(2020, 9, 24, 10, 45)


@immobilus("2020-9-23 08:24:15.230")
def test_do_not_retrieve_next_session_if_no_session_today():
    classroom = Classroom.create("next session", datetime(2020, 9, 10, 10), 2, stop_date=datetime(2021, 6, 10, 10))

    assert classroom.next_session() is None


@immobilus("2021-08-22 08:24:15.230")
def test_retrieve_next_session_if_today_is_sunday_and_next_session_on_monday():
    classroom = Classroom.create("next session", datetime(2021, 8, 23, 10), 2, stop_date=datetime(2022, 7, 12, 10))

    assert classroom.next_session()


def test_confirm_session_with_scheduled_time():
    classroom: Classroom = Classroom.create("classroom to be confirmed", datetime(2019, 6, 7, 10), 2, duration=Duration(MinuteTimeUnit(45)))

    session: ConfirmedSession = classroom.confirm_session_at(datetime(2019, 6, 7, 10))

    assert session.stop == datetime(2019, 6, 7, 10, 45)
