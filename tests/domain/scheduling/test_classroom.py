import uuid
from datetime import datetime

import pytest

from crm_pilates.domain.scheduling.classroom import (
    Classroom,
)
from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.domain.scheduling.duration import (
    Duration,
    HourTimeUnit,
    MinuteTimeUnit,
)
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
