import calendar
from datetime import datetime
from http import HTTPStatus
from typing import List, Tuple

import arrow
import pytz
from arrow import Arrow
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
        GetNextSessionsCommand(datetime.utcnow()))
    return __map_sessions(next_sessions_result[0].event)


@router.get("/sessions",
            response_model=List[SessionResponse],
            responses={
                200: {
                    "description": "List all sessions for a given period or by default for the current month."
                                   "If you want all the sessions for a specific period, you must provide both start date and end date in iso format (i.e: YYYY-MM-DDTHH:mm:ss)",
                    "headers": {
                        "X-Link": {
                            "description": "The previous, current and next period according to the start date and end date given, otherwise, previous month, current month and next month"
                                           "example: "
                                           "X-Link: </sessions?start_date=2021-08-01T00:00:00&end_date=2021-08-31T23:59:59>; rel='previous',"
                                           "</sessions?start_date=2021-09-01T00:00:00&end_date=2021-09-30T23:59:59>; rel='current',"
                                           "</sessions?start_date=2021-10-01T00:00:00&end_date=2021-10-31T23:59:59>; rel='next'",
                            "schema": {"type": "URL"},
                        }
                    }
                }
            }
            )
def sessions(response: Response, command_bus_provider: CommandBusProvider = Depends(CommandBusProvider), start_date: datetime = None, end_date: datetime = None):
    if start_date and end_date:
        command = GetSessionsInRangeCommand(start_date, end_date)
    else:
        start_date: datetime = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.utc)
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
    previous_header = f'</sessions?start_date={first_day_of_previous_month}&end_date={last_day_of_previous_month}>; rel="previous"'
    current_header = f'</sessions?start_date={first_day_of_current_month}&end_date={last_day_of_current_month}>; rel="current"'
    next_header = f'</sessions?start_date={first_day_of_next_month}&end_date={last_day_of_next_month}>; rel="next"'
    response.headers["X-Link"] = f"{previous_header}, {current_header}, {next_header}"


def __get_dates_for_period(start_date: datetime, end_date: datetime):
    arrow_start: Arrow = Arrow(start_date.year, start_date.month, start_date.day, start_date.hour, start_date.minute, start_date.second, tzinfo=start_date.tzinfo)
    arrow_end: Arrow = Arrow(end_date.year, end_date.month, end_date.day, end_date.hour, end_date.minute, end_date.second, tzinfo=end_date.tzinfo)
    if start_date.day == 1 and end_date.day == calendar.monthrange(start_date.year, start_date.month)[1]:
        first_day_of_previous_period = arrow_start.shift(months=-1).replace(day=1)
        last_day_of_previous_period = arrow_start.shift(months=-1).replace(day=calendar.monthrange(first_day_of_previous_period.year, first_day_of_previous_period.month)[1], hour=23, minute=59, second=59)
        first_day_of_next_period = arrow_start.shift(months=+1).replace(day=1)
        last_day_of_next_period = arrow_start.shift(months=+1).replace(day=calendar.monthrange(first_day_of_next_period.year, first_day_of_next_period.month)[1], hour=23, minute=59, second=59)
    else:
        number_of_days = len(list(arrow.Arrow.span_range('days', start_date, end_date)))
        first_day_of_previous_period = arrow_start.shift(days=-number_of_days + 1)
        last_day_of_previous_period = arrow_end.shift(days=-number_of_days)
        first_day_of_next_period = arrow_start.shift(days=+number_of_days)
        last_day_of_next_period = arrow_end.shift(days=+number_of_days)
    date_format = 'YYYY-MM-DDTHH:mm:ssZZ'
    return arrow_start.format(date_format), first_day_of_next_period.format(date_format), first_day_of_previous_period.format(
        date_format), arrow_end.format(date_format), last_day_of_next_period.format(date_format), last_day_of_previous_period.format(date_format)
