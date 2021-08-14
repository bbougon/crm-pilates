from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, date
from uuid import UUID

from domain.classroom.duration import TimeUnit, Duration
from domain.exceptions import DomainException
from domain.repository import AggregateRoot


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

    def all_attendees(self, attendees: [Attendee]):
        if self.position < len(attendees):
            raise DomainException(
                f"Cannot add anymore attendees (position available: {self.position - len(self.attendees)} - attendee(s) you try to add: {len(attendees)})")
        self.attendees = attendees

    def next_session(self) -> Session:
        if self.schedule.stop and (self.__has_session_today() or (self.__today_is_sunday() and self.__next_session_on_monday())):
            start: datetime = datetime.now().replace(hour=self.schedule.start.hour, minute=self.schedule.start.minute, second=0, microsecond=0)
            stop: datetime = start + timedelta(minutes=self.duration.to_minutes())
            return Session(self, start, stop)

    def __has_session_today(self) -> bool:
        return (datetime.now().date() - self.schedule.start.date()).days % 7 == 0

    def __today_is_sunday(self):
        return datetime.now().today().isoweekday() == 7

    def __next_session_on_monday(self):
        monday:datetime = datetime.now() + timedelta(days=1)
        pass


class Attendee:

    def __init__(self, id: UUID) -> None:
        super().__init__()
        self.id = id

    @staticmethod
    def create(id: UUID) -> Attendee:
        return Attendee(id)


class Session:

    def __init__(self, classroom: Classroom, start: datetime, stop: datetime) -> None:
        super().__init__()
        self.__classroom = classroom
        self.__attendees = classroom.attendees
        self.__start = start
        self.__stop = stop

    @property
    def attendees(self):
        return self.__attendees

    @property
    def name(self):
        return self.__classroom.name

    @property
    def id(self):
        return self.__classroom.id

    @property
    def position(self):
        return self.__classroom.position

    @property
    def duration(self):
        return self.__classroom.duration

    @property
    def start(self):
        return self.__start

    @property
    def stop(self):
        return self.__stop