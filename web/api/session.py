import calendar
from datetime import datetime, timedelta
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
    return __map_sessions(next_sessions_result[0].event)


@router.get("/sessions",
            response_model=List[SessionResponse]
            )
def sessions(response: Response, command_bus_provider: CommandBusProvider = Depends(CommandBusProvider), start_date: datetime = None, end_date: datetime = None):
    if start_date and end_date:
        command = GetSessionsInRangeCommand(start_date, end_date)
    else:
        start_date: datetime = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date: datetime = start_date.replace(
            day=calendar.monthrange(start_date.year, start_date.month)[1], hour=23, minute=59, second=59, microsecond=0)
        command = GetSessionsInRangeCommand(start_date, end_date)

    __set_link_header(response, *__get_dates_for_period(start_date, end_date))
    from command.response import Response
    result: Tuple[Response, status] = command_bus_provider.command_bus.send(command)
    return __map_sessions(result[0].event)


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


def __map_sessions(event):
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


def __set_link_header(response, first_day_of_current_month, first_day_of_next_month, first_day_of_previous_month,
                      last_day_of_current_month, last_day_of_next_month, last_day_of_previous_month):
    previous_header = f'</sessions?start_date={first_day_of_previous_month.isoformat()}&end_date={last_day_of_previous_month.isoformat()}>; rel="previous"'
    current_header = f'</sessions?start_date={first_day_of_current_month.isoformat()}&end_date={last_day_of_current_month.isoformat()}>; rel="current"'
    next_header = f'</sessions?start_date={first_day_of_next_month.isoformat()}&end_date={last_day_of_next_month.isoformat()}>; rel="next"'
    response.headers["X-Link"] = f"{previous_header}, {current_header}, {next_header}"


def __get_dates_for_period(start_date: datetime, end_date: datetime):
    if start_date.day == 1 and end_date.day == calendar.monthrange(start_date.year, start_date.month)[1]:
        first_day_of_previous_period = start_date.replace(month=start_date.month - 1)
        last_day_of_previous_period = first_day_of_previous_period.replace(day=calendar.monthrange(first_day_of_previous_period.year, first_day_of_previous_period.month)[1], hour=23, minute=59, second=59)
        first_day_of_next_period = start_date.replace(month=start_date.month + 1)
        last_day_of_next_period = first_day_of_next_period.replace(day=calendar.monthrange(first_day_of_next_period.year, first_day_of_next_period.month)[1], hour=23, minute=59, second=59)
    else:
        delta = end_date.date() - start_date.date()
        first_day_of_previous_period = start_date - delta
        last_day_of_previous_period = end_date - delta - timedelta(days=1)
        first_day_of_next_period = start_date + delta + timedelta(days=1)
        last_day_of_next_period = end_date + delta + timedelta(days=1)
    return start_date, first_day_of_next_period, first_day_of_previous_period, end_date, last_day_of_next_period, last_day_of_previous_period
