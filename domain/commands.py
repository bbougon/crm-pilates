from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID

from command.command_handler import Command
from web.schema.classroom_creation import Duration


@dataclass
class ClassroomCreationCommand(Command):
    name: str
    position: int
    duration: Duration
    start_date: datetime
    stop_date: datetime = None
    attendees: List[UUID] = field(default_factory=list)
