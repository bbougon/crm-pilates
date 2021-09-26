import datetime
import logging
from http import HTTPStatus
from typing import List, Tuple

from fastapi import status, APIRouter, Depends, Response, HTTPException

from command.command_handler import Status
from domain.classroom.classroom import Session
from domain.classroom.next_sessions_command_handler import NextScheduledSessions
from domain.classroom.session_checkin_saga_handler import SessionCheckedIn
from domain.commands import GetNextSessionsCommand
from domain.exceptions import DomainException, AggregateNotFoundException
from domain.sagas import SessionCheckinSaga
from infrastructure.command_bus_provider import CommandBusProvider
from infrastructure.repository_provider import RepositoryProvider
from web.presentation.service.classroom_service import to_detailed_attendee
from web.schema.session_response import SessionResponse
from web.schema.session_schemas import SessionCheckin

router = APIRouter()


@router.get("/sessions/next",
            response_model=List[SessionResponse]
            )
def next_sessions(command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)):
    logging.Logger("repository").debug(msg=f"classes: {RepositoryProvider.read_repositories.classroom.get_all()}")
    from command.response import Response
    next_sessions_result: Tuple[Response, Status] = command_bus_provider.command_bus.send(
        GetNextSessionsCommand(datetime.datetime.now()))
    result = []
    event: NextScheduledSessions = next_sessions_result[0].event
    for session in event.sessions:
        next_session = {
            "id": session.root_id,
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
        from command.response import Response
        checkin_event_result: Tuple[Response, Status] = command_bus_provider.command_bus.send(
            SessionCheckinSaga(session_checkin.classroom_id, session_checkin.session_date, session_checkin.attendee))
        result: SessionCheckedIn = checkin_event_result[0].event
        session: Session = RepositoryProvider.read_repositories.session.get_by_id(result.root_id)
        if checkin_event_result[1] == Status.UPDATED:
            response.status_code = status.HTTP_200_OK
        return {
            "id": result.root_id,
            "name": session.name,
            "classroom_id": session.classroom_id,
            "position": session.position,
            "schedule": {
                "start": session.start.isoformat(),
                "stop": session.stop.isoformat()
            },
            "attendees": list(map(lambda attendee: to_detailed_attendee(attendee.id, attendee.attendance.value), session.attendees))
        }
    except AggregateNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"{e.entity_type} with id '{str(e.unknown_id)}' not found")
    except DomainException as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=e.message)
