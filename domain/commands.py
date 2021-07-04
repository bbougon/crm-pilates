from dataclasses import dataclass
from datetime import datetime

from command.command_handler import Command
from web.schema.classroom_creation import Duration


@dataclass
class ClassroomCreationCommand(Command):
    name: str
    position: int
    duration: Duration
    start_date: datetime
    stop_date: datetime
