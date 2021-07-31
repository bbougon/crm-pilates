from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from domain.exceptions import DomainException
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
        self.attendees: [Attendee] = []

    @staticmethod
    def create(name: str, start_date: datetime, position: int, stop_date: datetime = None,
               duration: Duration = Duration(duration=1, time_unit=TimeUnit.HOUR)) -> Classroom:
        classroom = Classroom(name, position, Schedule(start=start_date, stop=stop_date), duration)
        classroom.name = name
        classroom.position = position
        classroom.schedule = Schedule(start=start_date, stop=stop_date)
        classroom.duration = duration
        return classroom

    def add_attendees(self, attendees: [Attendee]):
        if self.position < len(attendees) or self.position == len(self.attendees):
            raise DomainException(
                f"Cannot add anymore attendees (position available: {self.position - len(self.attendees)} - attendee(s) you try to add: {len(attendees)})")
        self.attendees = attendees


class Attendee:

    def __init__(self, id: UUID) -> None:
        super().__init__()
        self.id = id

    @staticmethod
    def create(id: UUID) -> Attendee:
        return Attendee(id)
