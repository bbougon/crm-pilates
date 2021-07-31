import pytest
import uuid
from datetime import datetime

from domain.classroom.classroom import Classroom, TimeUnit, Duration, Attendee
from domain.exceptions import DomainException


def test_create_classroom():
    classroom = Classroom.create("mat class room", datetime(2020, 1, 2, 10, 0), 2)

    assert classroom.schedule.start == datetime(2020, 1, 2, 10, 0)
    assert not classroom.schedule.stop
    assert classroom.duration == Duration(duration=1, time_unit=TimeUnit.HOUR)


def test_classroom_has_a_duration_in_minutes():
    classroom = Classroom.create("machine beginners", datetime(2021, 5, 3), 2, duration=Duration(duration=45, time_unit=TimeUnit.MINUTE))

    assert classroom.duration == Duration(duration=45, time_unit=TimeUnit.MINUTE)


def test_classroom_is_scheduled():
    classroom = Classroom.create("machine", datetime(2020, 3, 19), 4, stop_date=datetime(2020, 6, 19))

    assert classroom.schedule.start == datetime(2020, 3, 19)
    assert classroom.schedule.stop == datetime(2020, 6, 19)


def test_cannot_add_attendees_when_position_overflown():
    classroom = Classroom.create("machine", datetime(2020, 3, 19), 1, stop_date=datetime(2020, 6, 19))
    with pytest.raises(DomainException) as e:
        classroom.add_attendees([Attendee.create(uuid.uuid4()), Attendee.create(uuid.uuid4())])

    assert e.value.message == "Cannot add anymore attendees (position available: 1 - attendee(s) you try to add: 2)"


def test_cannot_add_more_attendees_hence_position_is_full():
    classroom = Classroom.create("machine", datetime(2020, 3, 19), 2, stop_date=datetime(2020, 6, 19))
    classroom.add_attendees([Attendee.create(uuid.uuid4()), Attendee.create(uuid.uuid4())])
    with pytest.raises(DomainException) as e:
        classroom.add_attendees([Attendee.create(uuid.uuid4())])

    assert e.value.message == "Cannot add anymore attendees (position available: 0 - attendee(s) you try to add: 1)"
