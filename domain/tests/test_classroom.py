from datetime import time, datetime

from domain.classroom import Classroom, TimeUnit, Duration


def test_create_classroom():
    classroom = Classroom.create("mat class room", time(11, 15), datetime(2020, 1, 2))

    assert classroom.schedule == time(hour = 11, minute = 15)
    assert classroom.start_date == datetime(2020, 1, 2)
    assert classroom.duration == Duration(1, TimeUnit.HOUR)
    

def test_classroom_has_a_duration_in_minutes():
    classroom = Classroom.create("machine beginners", time(14, 30), datetime(2021, 5, 3), Duration(45, TimeUnit.MINUTE))

    assert classroom.duration == Duration(45, TimeUnit.MINUTE)