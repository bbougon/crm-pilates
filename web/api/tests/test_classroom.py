from datetime import datetime

from fastapi import Response

from infrastructure.tests.memory_classroom_repository import MemoryClassroomRepository
from web.api.classroom import create_classroom
from web.schema.classroom_creation import ClassroomCreation


def test_create_classroom():
    repository = MemoryClassroomRepository()
    classroom_json = {"name": "advanced classroom", "start_date": "2020-02-11T10:00:00",
                      "duration": {"duration": 45, "unit": "MINUTE"}}

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json), Response(), repository)

    assert response["name"] == "advanced classroom"
    assert response["start_date"] == datetime(2020, 2, 11, 10, 0)
    assert response["duration"]["duration"] == 45
    assert response["duration"]["unit"] == "MINUTE"
    assert response["id"]
    assert repository.get_by_id(response["id"])
