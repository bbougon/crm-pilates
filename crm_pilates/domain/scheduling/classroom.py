from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from crm_pilates.domain.exceptions import DomainException
from crm_pilates.domain.repository import AggregateRoot
from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.domain.scheduling.duration import (
    Duration,
    HourTimeUnit,
)


@dataclass
class Schedule:
    start: datetime
    stop: datetime


class Classroom(AggregateRoot):
    def __init__(
        self,
        name: str,
        position: int,
        schedule: Schedule,
        subject: ClassroomSubject,
        duration: Duration,
    ):
        super().__init__()
        self._name = name
        self._position = position
        self._schedule = schedule
        self._duration = duration
        self._attendees: [Attendee] = []
        self._subject = subject

    @property
    def name(self) -> str:
        return self._name

    @property
    def position(self) -> int:
        return self._position

    @property
    def schedule(self) -> Schedule:
        return self._schedule

    @property
    def duration(self) -> Duration:
        return self._duration

    @property
    def attendees(self) -> List[Attendee]:
        return self._attendees

    @property
    def subject(self) -> ClassroomSubject:
        return self._subject

    @staticmethod
    def create(
        name: str,
        start_date: datetime,
        position: int,
        subject: ClassroomSubject,
        stop_date: datetime = None,
        duration: Duration = Duration(HourTimeUnit(1)),
    ) -> Classroom:
        if not stop_date:
            stop_date = start_date + timedelta(
                hours=duration.time_unit.to_unit(HourTimeUnit).value
            )
        classroom = Classroom(
            name,
            position,
            Schedule(start=start_date, stop=stop_date),
            subject,
            duration,
        )
        return classroom

    def all_attendees(self, attendees: [Attendee]):
        if self._position < len(attendees):
            raise DomainException(
                f"Cannot add anymore attendees (position available: {self._position - len(self._attendees)} - attendee(s) you try to add: {len(attendees)})"
            )
        self._attendees = attendees
