from dataclasses import dataclass
from datetime import datetime

from command.command import Command
from web.schema.classroom_creation import Duration


@dataclass
class ClassroomCreationCommand(Command):
  name: str
  duration: Duration
  start_date: datetime