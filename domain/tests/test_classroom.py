from datetime import time, datetime

from domain.classroom import Classroom


def test_create_classroom():
    classroom = Classroom.create("mat class room", "11:15", datetime(2020, 1, 2))

    assert classroom.hour == time(hour = 11, minute = 15)
    assert classroom.day == datetime(2020, 1, 2)
    
