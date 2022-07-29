import pytest
from mimesis import Datetime

from crm_pilates.web.schema.classroom_schemas import ClassroomCreation, ClassroomPatch


def test_attendees_are_unique_for_creation():
    with pytest.raises(ValueError) as e:
        ClassroomCreation.parse_obj(
            {
                "name": "a name",
                "position": 2,
                "subject": "MAT",
                "start_date": Datetime().datetime(),
                "attendees": [
                    {"id": "ba3344fe-e9c1-4d9f-b35c-2c7c23d77280"},
                    {"id": "ba3344fe-e9c1-4d9f-b35c-2c7c23d77280"},
                ],
            }
        )

    assert (
        e.value.raw_errors[0].exc.args[0]
        == "You provided the same attendee twice or more, please check the attendees and retry"
    )


def test_attendees_are_unique_for_patch():
    with pytest.raises(ValueError) as e:
        ClassroomPatch.parse_obj(
            {
                "attendees": [
                    {"id": "ba3344fe-e9c1-4d9f-b35c-2c7c23d77280"},
                    {"id": "ba3344fe-e9c1-4d9f-b35c-2c7c23d77280"},
                ]
            }
        )

    assert (
        e.value.raw_errors[0].exc.args[0]
        == "You provided the same attendee twice or more, please check the attendees and retry"
    )
