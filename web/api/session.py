import datetime
from typing import List

from fastapi import status, APIRouter, Depends

from domain.classroom.next_sessions_command_handler import NextScheduledSessions
from domain.classroom.session_checkin_saga_handler import SessionCheckedIn
from domain.commands import GetNextSessionsCommand
from domain.sagas import SessionCheckinSaga
from infrastructure.command_bus_provider import CommandBusProvider
from web.schema.session_response import SessionResponse
from web.schema.session_schemas import SessionCheckin

router = APIRouter()


@router.get("/sessions/next",
            response_model=List[SessionResponse]
            )
def next_sessions(command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)):
    next_sessions_event: NextScheduledSessions = command_bus_provider.command_bus.send(
        GetNextSessionsCommand(datetime.datetime.now())).event
    result = []
    for session in next_sessions_event.sessions:
        next_session = {
            "name": session.name,
            "classroom_id": session.classroom_id,
            "position": session.position,
            "schedule": {
                "start": session.start.isoformat(),
                "stop": session.stop.isoformat() if session.stop else None
            },
            "duration": {
                "unit": session.duration["time_unit"],
                "duration": session.duration["duration"]
            },
            "attendees": session.attendees
        }
        result.append(next_session)
    return result


@router.post("/sessions/checkin",
             status_code=status.HTTP_201_CREATED
             )
def session_checkin(session_checkin: SessionCheckin,
                    command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)):
    checkin_event: SessionCheckedIn = command_bus_provider.command_bus.send(
        SessionCheckinSaga(session_checkin.classroom_id, session_checkin.session_date, session_checkin.attendee)).event
    return {
        "id": checkin_event.id,
        "name": checkin_event.name,
        "classroom_id": checkin_event.classroom_id,
        "position": checkin_event.position,
        "schedule": {
            "start": checkin_event.start.isoformat(),
            "stop": checkin_event.stop.isoformat()
        },
        "attendees": checkin_event.attendees
    }
