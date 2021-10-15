from __future__ import annotations

import uuid
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List
from uuid import UUID

from domain.classroom.date_time_comparator import DateTimeComparator
from domain.classroom.duration import Duration, MinuteTimeUnit, HourTimeUnit, TimeUnit
from domain.datetimes import Weekdays
from domain.exceptions import DomainException
from domain.repository import AggregateRoot


@dataclass
class Schedule:
    start: datetime
    stop: datetime


class Classroom(AggregateRoot):

    def __init__(self, name: str, position: int, schedule: Schedule, duration: Duration):
        super().__init__()
        self._name = name
        self._position = position
        self._schedule = schedule
        self._duration = duration
        self._attendees: [Attendee] = []

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

    @staticmethod
    def create(name: str, start_date: datetime, position: int, stop_date: datetime = None,
               duration: Duration = Duration(HourTimeUnit(1))) -> Classroom:
        classroom = Classroom(name, position, Schedule(start=start_date, stop=stop_date), duration)
        classroom._duration = duration
        return classroom

    def all_attendees(self, attendees: [Attendee]):
        if self._position < len(attendees):
            raise DomainException(
                f"Cannot add anymore attendees (position available: {self._position - len(self._attendees)} - attendee(s) you try to add: {len(attendees)})")
        self._attendees = attendees

    def next_session(self) -> ScheduledSession:
        if self.__has_session_today() or (self.__today_is_sunday() and self.__next_session_on_monday()):
            start: datetime = datetime.now().replace(hour=self._schedule.start.hour, minute=self._schedule.start.minute,
                                                     second=0, microsecond=0)
            return ScheduledSession.create(self, start)

    def __has_session_today(self) -> bool:
        return DateTimeComparator(self._schedule.start, datetime.now()).same_date().compare() or (self._schedule.stop and DateTimeComparator(datetime.now(), self._schedule.start).same_day().compare())

    def __today_is_sunday(self):
        return datetime.now().today().isoweekday() == Weekdays.SUNDAY

    def __next_session_on_monday(self):
        monday: datetime = datetime.now() + timedelta(days=1)
        return monday.isoweekday() == Weekdays.MONDAY

    def confirm_session_at(self, session_date: datetime) -> ConfirmedSession:
        return ConfirmedSession.create(self, session_date)


class Attendance(Enum):
    REGISTERED = "REGISTERED"
    CHECKED_IN = "CHECKED_IN"


class Attendee:

    def __init__(self, id: UUID) -> None:
        super().__init__()
        self._id: UUID = id
        self.attendance: Attendance = Attendance.REGISTERED

    @property
    def id(self) -> UUID:
        return self._id

    @staticmethod
    def create(id: UUID) -> Attendee:
        return Attendee(id)

    def checkin(self):
        self.attendance = Attendance.CHECKED_IN

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Attendee) and self.id == o.id


class Session:

    def __init__(self, classroom_id: UUID, name: str, position: int, start: datetime, classroom_duration: TimeUnit, attendees: [Attendee]) -> None:
        self.__name: str = name
        self.__position: int = position
        self.__attendees: List[Attendee] = attendees
        self.__start: datetime = start
        self.__stop: datetime = start + timedelta(minutes=classroom_duration.to_unit(MinuteTimeUnit).value)
        self.__classroom_id: UUID = classroom_id

    @property
    def classroom_id(self):
        return self.__classroom_id

    @property
    def attendees(self):
        return self.__attendees

    @property
    def name(self):
        return self.__name

    @property
    def position(self):
        return self.__position

    @property
    def start(self):
        return self.__start

    @property
    def stop(self):
        return self.__stop

    @property
    @abstractmethod
    def id(self):
        return None


class ScheduledSession(Session):

    @staticmethod
    def create(classroom: Classroom, start) -> ScheduledSession:
        return ScheduledSession(classroom.id, classroom.name, classroom.position, start, classroom.duration.time_unit, classroom.attendees)

    @property
    def id(self):
        return None


class ConfirmedSession(Session, AggregateRoot):

    def __init__(self, classroom_id: UUID, name: str, position: int, start: datetime, duration_time_unit: TimeUnit, attendees: [Attendee]) -> None:
        super().__init__(classroom_id, name, position, start, duration_time_unit, attendees)
        self._id = uuid.uuid4()

    @staticmethod
    def create(classroom: Classroom, start: datetime) -> ConfirmedSession:
        if not DateTimeComparator(classroom.schedule.start, start).same_day().same_time().before().compare():
            raise InvalidSessionStartDateException(classroom, start)
        return ConfirmedSession(classroom.id, classroom.name, classroom.position, start, classroom.duration.time_unit, classroom.attendees)

    @property
    def id(self):
        return self._id

    def checkin(self, attendee: Attendee) -> Attendee:
        for registered_attendee in self.attendees:
            if registered_attendee == attendee:
                registered_attendee.checkin()
                return registered_attendee


class InvalidSessionStartDateException(DomainException):

    def __init__(self, classroom: Classroom, start_date: datetime, *args: object) -> None:
        if start_date < classroom.schedule.start:
            message = f"Classroom '{classroom.name}' starting at '{classroom.schedule.start.isoformat()}' cannot be set before"
        else:
            weekdays_difference = abs(classroom.schedule.start.date().weekday() - start_date.date().weekday())
            closest_prior_date = datetime.combine((start_date.date() - timedelta(days=weekdays_difference)),
                                                  classroom.schedule.start.time())
            closest_following_date = datetime.combine((start_date.date() + timedelta(days=7 - weekdays_difference)),
                                                      classroom.schedule.start.time())
            message = f"Classroom '{classroom.name}' starting at '{classroom.schedule.start.isoformat()}' cannot be set at '{start_date.isoformat()}', closest possible dates are '{closest_prior_date.isoformat()}' or '{closest_following_date.isoformat()}'"
        super().__init__(message, *args)
