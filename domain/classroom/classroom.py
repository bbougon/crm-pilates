from __future__ import annotations

import uuid
from abc import abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
from uuid import UUID

import arrow
import pytz

from domain.classroom.attendee import Attendee
from domain.classroom.classroom_type import ClassroomSubject
from domain.classroom.date_time_comparator import DateTimeComparator, DateComparator
from domain.classroom.duration import Duration, MinuteTimeUnit, HourTimeUnit, TimeUnit
from domain.datetimes import Weekdays
from domain.exceptions import DomainException
from domain.repository import AggregateRoot


@dataclass
class Schedule:
    start: datetime
    stop: datetime


class Classroom(AggregateRoot):

    def __init__(self, name: str, position: int, schedule: Schedule, subject: ClassroomSubject, duration: Duration):
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
    def create(name: str, start_date: datetime, position: int, subject: ClassroomSubject, stop_date: datetime = None,
               duration: Duration = Duration(HourTimeUnit(1))) -> Classroom:
        if not stop_date:
            stop_date = start_date + timedelta(hours=duration.time_unit.to_unit(HourTimeUnit).value)
        classroom = Classroom(name, position, Schedule(start=start_date, stop=stop_date), subject, duration)
        return classroom

    def all_attendees(self, attendees: [Attendee]):
        if self._position < len(attendees):
            raise DomainException(
                f"Cannot add anymore attendees (position available: {self._position - len(self._attendees)} - attendee(s) you try to add: {len(attendees)})")
        self._attendees = attendees

    def next_session(self) -> ScheduledSession:
        if self.__has_session_today() or (self.__today_is_sunday() and self.__next_session_on_monday()):
            start: datetime = datetime.utcnow().replace(hour=self._schedule.start.hour, minute=self._schedule.start.minute, second=0, microsecond=0, tzinfo=self._schedule.start.tzinfo or pytz.utc)
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

    def sessions_in_range(self, start_date: datetime, end_date: datetime) -> List[Session]:
        days: [datetime] = list(map(lambda day_range: day_range.date(), arrow.Arrow.range('day', start_date, end_date)))
        sessions: [Session] = []
        classroom_start_date = self.schedule.start
        for day in days:
            if DateComparator(classroom_start_date.date(), day).same_day().before().compare() \
                    and DateComparator(day, end_date.date()).before().compare() \
                    and DateComparator(day, self.schedule.stop.date()).before().compare():
                sessions.append(Session(self.id, self.name, self.position, self.subject, datetime(day.year, day.month, day.day, classroom_start_date.hour, classroom_start_date.minute, tzinfo=pytz.utc if classroom_start_date.tzinfo is None else classroom_start_date.tzinfo), self.duration.time_unit, self.attendees))
        return sessions


class Session:

    def __init__(self, classroom_id: UUID, name: str, position: int, subject: ClassroomSubject, start: datetime, classroom_duration: TimeUnit, attendees: [Attendee]) -> None:
        self.__name: str = name
        self.__position: int = position
        self.__subject: ClassroomSubject = subject
        self.__attendees: List[Attendee] = deepcopy(attendees)
        self.__start: datetime = start.astimezone(pytz.utc) if start.tzinfo is None else start
        self.__stop: datetime = self.__start + timedelta(minutes=classroom_duration.to_unit(MinuteTimeUnit).value)
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
    def subject(self) -> ClassroomSubject:
        return self.__subject

    @property
    @abstractmethod
    def id(self):
        return None


class ScheduledSession(Session):

    @staticmethod
    def create(classroom: Classroom, start) -> ScheduledSession:
        return ScheduledSession(classroom.id, classroom.name, classroom.position, classroom.subject, start, classroom.duration.time_unit, classroom.attendees)

    @property
    def id(self):
        return None


class ConfirmedSession(Session, AggregateRoot):

    def __init__(self, classroom_id: UUID, name: str, position: int, subject: ClassroomSubject, start: datetime, duration_time_unit: TimeUnit, attendees: [Attendee]) -> None:
        super().__init__(classroom_id, name, position, subject, start, duration_time_unit, attendees)
        self._id = uuid.uuid4()

    @staticmethod
    def create(classroom: Classroom, start: datetime) -> ConfirmedSession:
        if not DateTimeComparator(classroom.schedule.start, start).same_day().same_time().before().compare():
            raise InvalidSessionStartDateException(classroom, start)
        return ConfirmedSession(classroom.id, classroom.name, classroom.position, classroom.subject, start, classroom.duration.time_unit, classroom.attendees)

    @property
    def id(self):
        return self._id

    def checkin(self, attendee: Attendee) -> Attendee:
        try:
            registered_attendee = next(filter(lambda current_attendee: current_attendee == attendee, self.attendees))
            registered_attendee.checkin()
            return registered_attendee
        except StopIteration:
            raise DomainException(f"Attendee with id {str(attendee.id)} could not be checked in")

    def checkout(self, attendee: Attendee) -> Attendee:
        try:
            checkedout_attendee: Attendee = next(filter(lambda current_attendee: current_attendee == attendee, self.attendees))
            checkedout_attendee.checkout()
            return checkedout_attendee
        except StopIteration:
            raise DomainException(f"Attendee with id {str(attendee.id)} could not be checked out")

    def cancel(self, attendee: Attendee) -> None:
        self.attendees.remove(attendee)


class InvalidSessionStartDateException(DomainException):

    def __init__(self, classroom: Classroom, start_date: datetime, *args: object) -> None:
        if start_date < classroom.schedule.start:
            message = f"Classroom '{classroom.name}' starting at '{classroom.schedule.start.isoformat()}' cannot be set before"
        else:
            weekdays_difference = abs(classroom.schedule.start.date().weekday() - start_date.date().weekday())
            closest_prior_date = datetime.combine((start_date.date() - timedelta(days=weekdays_difference)),
                                                  classroom.schedule.start.time()).replace(tzinfo=pytz.utc)
            closest_following_date = datetime.combine((start_date.date() + timedelta(days=7 - weekdays_difference)),
                                                      classroom.schedule.start.time()).replace(tzinfo=pytz.utc)
            message = f"Classroom '{classroom.name}' starting at '{classroom.schedule.start.isoformat()}' cannot be set at '{start_date.isoformat()}', closest possible dates are '{closest_prior_date.isoformat()}' or '{closest_following_date.isoformat()}'"
        super().__init__(message, *args)
