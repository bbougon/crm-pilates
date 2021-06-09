from datetime import datetime

from domain.classroom import Classroom, TimeUnit, Duration


def test_create_classroom():
    classroom = Classroom.create("mat class room", datetime(2020, 1, 2, 10, 0))

    assert classroom.start_date == datetime(2020, 1, 2, 10, 0)
    assert classroom.duration == Duration(1, TimeUnit.HOUR)
    

def test_classroom_has_a_duration_in_minutes():
    classroom = Classroom.create("machine beginners", datetime(2021, 5, 3), Duration(45, TimeUnit.MINUTE))

    assert classroom.duration == Duration(45, TimeUnit.MINUTE)