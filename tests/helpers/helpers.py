from domain.classroom.classroom import Classroom


def expected_session_response(session_id, classroom_id, classroom: Classroom, start_date: str, end_date: str,
                              attendees: []):
    return {
        "id": session_id,
        "name": classroom.name,
        "classroom_id": classroom_id,
        "position": classroom.position,
        "schedule": {
            "start": start_date,
            "stop": end_date
        },
        "attendees": attendees

    }
