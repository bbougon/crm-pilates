from __future__ import annotations

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

    def __init__(self, name: str, position: int, schedule: Schedule, duration: Duration):
        super().__init__()
        self.name = name
        self.position = position
        self.schedule = schedule
        self.duration = duration
        self.attendees = []

    @staticmethod
    def create(name: str, start_date: datetime, position: int, stop_date: datetime = None,
               duration: Duration = Duration(duration=1, time_unit=TimeUnit.HOUR)) -> Classroom:
        classroom = Classroom(name, position, Schedule(start=start_date, stop=stop_date), duration)
        classroom.name = name
        classroom.position = position
        classroom.schedule = Schedule(start=start_date, stop=stop_date)
        classroom.duration = duration
        return classroom

    def add_attendees(self, attendees):
        self.attendees = attendees
