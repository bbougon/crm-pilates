from datetime import time, date

from web.api.classroom import create_classroom
from web.schema.classroom_creation import ClassroomCreation


def test_create_classroom():
    classroom_json = {"name": "advanced classroom", "schedule": "10:00", "start_date": "2020-02-11",
                      "duration": {"duration": 45, "unit": "MINUTE"}}

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json))

    assert response["name"] == "advanced classroom"
    assert response["schedule"] == time(hour=10, minute=00)
    assert response["start_date"] == date(2020, 2, 11)
    assert response["duration"]["duration"] == 45
    assert response["duration"]["unit"] == "MINUTE"
    assert response["id"]
