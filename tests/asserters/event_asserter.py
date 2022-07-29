import datetime
from uuid import UUID


class EventAsserter:
    @classmethod
    def assert_classroom_created(
        cls,
        payload: dict,
        id: UUID,
        name: str,
        position: int,
        subject: str,
        duration: tuple[int, str],
        schedule: tuple[datetime, datetime],
        attendees: [],
    ):
        expected_payload = {
            "id": id,
            "name": name,
            "position": position,
            "subject": subject,
            "duration": {"duration": duration[0], "time_unit": duration[1]},
            "schedule": {"start": schedule[0], "stop": schedule[1]},
            "attendees": attendees,
        }
        cls.__assert_payload(payload, expected_payload)

    @classmethod
    def assert_client_created(
        cls,
        payload: dict,
        expected_id: UUID,
        expected_firstname: str,
        expected_name: str,
        expected_credits: [] = None,
    ):
        expected_payload = {
            "id": expected_id,
            "firstname": expected_firstname,
            "lastname": expected_name,
        }
        if expected_credits:
            expected_payload["credits"] = expected_credits
        cls.__assert_payload(payload, expected_payload)

    @classmethod
    def assert_client_credits_updated(
        cls, payload: dict, expected_id: UUID, expected_credits: [] = []
    ):
        expected_payload = {"id": expected_id, "credits": expected_credits}
        cls.__assert_payload(payload, expected_payload)

    @classmethod
    def assert_all_attendees_added(cls, payload, expected_attendees: [] = []):
        expected_payload = {"attendees": expected_attendees}
        cls.__assert_payload(payload, expected_payload)

    @classmethod
    def assert_attendee_session_cancelled(
        cls, payload, expected_id, expected_attendee_id
    ):
        expected_payload = {
            "session_id": expected_id,
            "attendee": {
                "id": expected_attendee_id,
            },
        }
        cls.__assert_payload(payload, expected_payload)

    @classmethod
    def assert_session_checkin(
        cls, payload, expected_id, expected_attendee_id, expected_attendance
    ):
        expected_payload = {
            "session_id": expected_id,
            "attendee": {"id": expected_attendee_id, "attendance": expected_attendance},
        }
        cls.__assert_payload(payload, expected_payload)

    @classmethod
    def assert_confirmed_session(
        cls,
        payload: dict,
        expected_root_id: UUID,
        expected_id: UUID,
        expected_name: str,
        expected_position: int,
        expected_subject: str,
        expected_duration: tuple[datetime, datetime],
        expected_attendees: [],
    ):
        expected_payload = {
            "id": expected_root_id,
            "classroom_id": expected_id,
            "name": expected_name,
            "position": expected_position,
            "subject": expected_subject,
            "schedule": {"start": expected_duration[0], "stop": expected_duration[1]},
            "attendees": expected_attendees,
        }
        cls.__assert_payload(payload, expected_payload)

    @classmethod
    def __assert_payload(cls, payload, expected_payload):
        expected_payload["version"] = "1"
        assert payload == expected_payload
