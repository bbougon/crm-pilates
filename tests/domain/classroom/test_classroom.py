from datetime import datetime

from domain.classroom.classroom import Classroom, TimeUnit, Duration


def test_create_classroom():
    classroom = Classroom.create("mat class room", datetime(2020, 1, 2, 10, 0))

    assert classroom.schedule.start == datetime(2020, 1, 2, 10, 0)
    assert not classroom.schedule.stop
    assert classroom.duration == Duration(duration=1, time_unit=TimeUnit.HOUR)


def test_classroom_has_a_duration_in_minutes():
    classroom = Classroom.create("machine beginners", datetime(2021, 5, 3), duration=Duration(duration=45, time_unit=TimeUnit.MINUTE))

    assert classroom.duration == Duration(duration=45, time_unit=TimeUnit.MINUTE)


def test_classroom_is_scheduled():
    classroom = Classroom.create("machine", datetime(2020, 3, 19), stop_date=datetime(2020, 6, 19))

    assert classroom.schedule.start == datetime(2020, 3, 19)
    assert classroom.schedule.stop == datetime(2020, 6, 19)
