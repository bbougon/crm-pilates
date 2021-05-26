from web.api.classroom import create_classroom
from web.schema.classroom_creation import ClassroomCreation


def test_create_classroom():
    classroom_json = {"name":"advanced classroom", "hour":"10:00"}

    response = create_classroom(ClassroomCreation.parse_obj(classroom_json))

    assert response["name"] == "advanced classroom"
    assert response["hour"] == "10:00"
    assert response["id"]