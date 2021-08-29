from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID

from command.command_handler import Command
from web.schema.classroom_schemas import Duration


@dataclass
class ClassroomCreationCommand(Command):
    name: str
    position: int
    duration: Duration
    start_date: datetime
    stop_date: datetime = None
    attendees: List[UUID] = field(default_factory=list)


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
    current_time: datetime


@dataclass
class SessionCreationCommand(Command):
    classroom_id: UUID
    session_date: datetime
