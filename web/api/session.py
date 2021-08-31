import datetime
from http import HTTPStatus
from typing import List

from fastapi import status, APIRouter, Depends, Response, HTTPException

from domain.classroom.next_sessions_command_handler import NextScheduledSessions
from domain.classroom.session_checkin_saga_handler import SessionCheckedIn, SessionCheckedInStatus
from domain.commands import GetNextSessionsCommand
from domain.exceptions import DomainException, AggregateNotFoundException
from domain.sagas import SessionCheckinSaga
from infrastructure.command_bus_provider import CommandBusProvider
from web.presentation.service.classroom_service import to_detailed_attendee
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
            "attendees": list(map(lambda attendee: to_detailed_attendee(attendee["id"], attendee["attendance"]), session.attendees))
        }
        result.append(next_session)
    return result


@router.post("/sessions/checkin",
             status_code=status.HTTP_201_CREATED,
             response_model=SessionResponse
             )
def session_checkin(session_checkin: SessionCheckin, response: Response,
                    command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)):
    try:
        checkin_event: SessionCheckedIn = command_bus_provider.command_bus.send(
            SessionCheckinSaga(session_checkin.classroom_id, session_checkin.session_date, session_checkin.attendee)).event
        if checkin_event.status == SessionCheckedInStatus.UPDATED:
            response.status_code = status.HTTP_200_OK
        return {
            "id": checkin_event.id,
            "name": checkin_event.name,
            "classroom_id": checkin_event.classroom_id,
            "position": checkin_event.position,
            "schedule": {
                "start": checkin_event.start.isoformat(),
                "stop": checkin_event.stop.isoformat()
            },
            "attendees": list(map(lambda attendee: to_detailed_attendee(attendee["id"], attendee["attendance"]), checkin_event.attendees))
        }
    except AggregateNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"{e.entity_type} with id '{str(e.unknown_id)}' not found")
    except DomainException as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=e.message)
