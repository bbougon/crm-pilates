from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import pytz

from command.command_handler import Command
from command.saga_handler import Saga


@dataclass
class SessionCheckinSaga(Saga):
    classroom_id: UUID
    _session_date: datetime
    attendee: UUID

    @property
    def session_date(self) -> datetime:
        return self._session_date.astimezone(pytz.utc) if self._session_date.tzinfo is None else self._session_date


@dataclass
class AttendeeSessionCancellationSaga(Command):
    attendee_id: UUID
    classroom_id: UUID
    _session_date: datetime

    @property
    def session_date(self) -> datetime:
        return self._session_date.astimezone(pytz.utc) if self._session_date.tzinfo is None else self._session_date
