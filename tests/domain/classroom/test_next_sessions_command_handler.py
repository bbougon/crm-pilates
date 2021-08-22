from datetime import datetime

from immobilus import immobilus

from domain.classroom.next_sessions_command_handler import NextSessionsCommandHandler, NextScheduledSessions
from domain.commands import GetNextSessionsCommand


@immobilus("2021-08-22T14:50")
def test_has_no_next_sessions():
    next_sessions: NextScheduledSessions = NextSessionsCommandHandler().execute(GetNextSessionsCommand(datetime.now()))

    assert next_sessions.sessions == []
