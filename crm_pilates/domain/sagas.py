from dataclasses import dataclass
from datetime import datetime
from typing import Set
from uuid import UUID

import pytz

from crm_pilates.command.saga_handler import Saga


@dataclass
class SessionDateSaga(Saga):
    _session_date: datetime

    @property
    def session_date(self) -> datetime:
        return (
            self._session_date.astimezone(pytz.utc)
            if self._session_date.tzinfo is None
            else self._session_date
        )


@dataclass
class SessionCheckinSaga(SessionDateSaga):
    classroom_id: UUID
    attendee: UUID


@dataclass
class AttendeeSessionCancellationSaga(SessionDateSaga):
    attendee_id: UUID
    classroom_id: UUID


@dataclass
class AddAttendeesToSessionSaga(SessionDateSaga):
    classroom_id: UUID
    attendees: Set[UUID]
