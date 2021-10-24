import calendar
from datetime import datetime
from http import HTTPStatus
from typing import List, Tuple

from fastapi import status, APIRouter, Depends, Response, HTTPException

from command.command_handler import Status
from domain.classroom.classroom import Session
from domain.classroom.session_checkin_saga_handler import SessionCheckedIn
from domain.commands import GetNextSessionsCommand, GetSessionsInRangeCommand
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
    from command.response import Response
    next_sessions_result: Tuple[Response, Status] = command_bus_provider.command_bus.send(
        GetNextSessionsCommand(datetime.now()))
    return map_sessions(next_sessions_result[0].event)


def map_sessions(event):
    result = []
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
            "attendees": list(
                map(lambda attendee: to_detailed_attendee(attendee["id"], attendee["attendance"]), session.attendees))
        }
        result.append(next_session)
    return result


@router.get("/sessions",
            response_model=List[SessionResponse]
            )
def sessions(response: Response, command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)):
    # headers = {"X-Link": '</sessions?from=previous>; rel="previous", </sessions?from=current>; rel="current", </sessions?from=next>; rel="next"'}
    current_date = datetime.now()
    first_day_of_current_month: datetime = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_of_current_month: datetime = current_date.replace(
        day=calendar.monthrange(current_date.year, current_date.month)[1], hour=23, minute=59, second=59, microsecond=0)
    __set_link_header(response, first_day_of_current_month, last_day_of_current_month)
    from command.response import Response
    result: Tuple[Response, status] = command_bus_provider.command_bus.send(
        GetSessionsInRangeCommand(first_day_of_current_month, last_day_of_current_month))
    return map_sessions(result[0].event)


def __set_link_header(response: Response, first_day_of_current_month: datetime, last_day_of_current_month: datetime):
    first_day_of_previous_month = first_day_of_current_month.replace(month=first_day_of_current_month.month - 1)
    last_day_of_previous_month = first_day_of_previous_month.replace(
        day=calendar.monthrange(first_day_of_previous_month.year, first_day_of_previous_month.month)[1], hour=23,
        minute=59, second=59)
    first_day_of_next_month = first_day_of_current_month.replace(month=first_day_of_current_month.month + 1)
    last_day_of_next_month = first_day_of_next_month.replace(day=calendar.monthrange(first_day_of_next_month.year, first_day_of_next_month.month)[1], hour=23, minute=59, second=59)
    previous_header = f'</sessions?start_date={first_day_of_previous_month.isoformat()}&end_date={last_day_of_previous_month.isoformat()}>; rel="previous"'
    current_header = f'</sessions?start_date={first_day_of_current_month.isoformat()}&end_date={last_day_of_current_month.isoformat()}>; rel="current"'
    next_header = f'</sessions?start_date={first_day_of_next_month.isoformat()}&end_date={last_day_of_next_month.isoformat()}>; rel="next"'
    response.headers["X-Link"] = f"{previous_header}, {current_header}, {next_header}"


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
            "attendees": list(
                map(lambda attendee: to_detailed_attendee(attendee.id, attendee.attendance.value), session.attendees))
        }
    except AggregateNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f"{e.entity_type} with id '{str(e.unknown_id)}' not found")
    except DomainException as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=e.message)
