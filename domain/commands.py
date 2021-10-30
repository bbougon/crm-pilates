from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID

import pytz

from command.command_handler import Command
from web.schema.classroom_schemas import Duration


@dataclass
class ClassroomCreationCommand(Command):
    name: str
    position: int
    duration: Duration
    _start_date: datetime
    _stop_date: datetime = None
    attendees: List[UUID] = field(default_factory=list)

    @property
    def start_date(self) -> datetime:
        return self._start_date.astimezone(pytz.utc)

    @property
    def stop_date(self) -> datetime:
        return self._stop_date.astimezone(pytz.utc) if self._stop_date else None


@dataclass
class ClientCreationCommand(Command):
    firstname: str
    lastname: str


@dataclass
class ClassroomPatchCommand(Command):
    classroom_id: UUID
    attendees: List[UUID] = field(default_factory=list)


@dataclass
class GetNextSessionsCommand(Command):
    _current_time: datetime

    @property
    def current_time(self) -> datetime:
        return self._current_time.astimezone(pytz.utc) if self._current_time.tzinfo is None else self._current_time


@dataclass
class SessionCreationCommand(Command):
    classroom_id: UUID
    _session_date: datetime

    @property
    def session_date(self) -> datetime:
        return self._session_date.astimezone(pytz.utc) if self._session_date.tzinfo is None else self._session_date


@dataclass
class GetSessionsInRangeCommand(Command):
    _start_date: datetime
    _end_date: datetime

    @property
    def start_date(self) -> datetime:
        return self._start_date.astimezone(pytz.utc) if self._start_date.tzinfo is None else self._start_date

    @property
    def end_date(self) -> datetime:
        return self._end_date.astimezone(pytz.utc) if self._end_date.tzinfo is None else self._end_date
