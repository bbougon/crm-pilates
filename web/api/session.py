import datetime

from fastapi import APIRouter, Depends

from domain.classroom.next_sessions_command_handler import NextScheduledSessions
from domain.commands import GetNextSessionsCommand
from infrastructure.command_bus_provider import CommandBusProvider

router = APIRouter()


@router.get("/sessions/next"
            )
def next_sessions(command_bus_provider: CommandBusProvider = Depends(CommandBusProvider)):
    next_sessions_event: NextScheduledSessions = command_bus_provider.command_bus.send(GetNextSessionsCommand(datetime.datetime.now())).event
    result = []
    for session in next_sessions_event.sessions:
        next_session = {
            "name": session.name,
            "id": str(session.id),
            "position": session.position,
            "schedule": {
                "start": session.start.isoformat(),
                "stop": session.stop.isoformat() if session.stop else None
            },
            "duration": {
                "time_unit": session.duration["time_unit"],
                "duration": session.duration["duration"]
            },
            "attendees": session.attendees
        }
        result.append(next_session)
    return result
