import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from domain.repository import AggregateRoot


class TimeUnit(Enum):
    HOUR = "HOUR"
    MINUTE = "MINUTE"


@dataclass
class Duration:
    time_unit: TimeUnit
    duration: int

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Duration) and self.duration == o.duration and self.time_unit == o.time_unit


@dataclass
class Schedule:
    start: datetime
    stop: datetime


class Classroom(AggregateRoot):
    name: str
    position: int
    schedule: Schedule
    duration: Duration

    def __init__(self):
        self.id = uuid.uuid4()

    @staticmethod
    def create(name: str, start_date: datetime, position: int, stop_date: datetime = None,
               duration: Duration = Duration(duration=1, time_unit=TimeUnit.HOUR)):
        classroom = Classroom()
        classroom.name = name
        classroom.position = position
        classroom.schedule = Schedule(start=start_date, stop=stop_date)
        classroom.duration = duration
        return classroom
