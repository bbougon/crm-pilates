from __future__ import annotations

import uuid
from abc import abstractmethod
from copy import deepcopy
from datetime import datetime, timedelta
from typing import List
from uuid import UUID

import pytz

from crm_pilates.domain.exceptions import DomainException
from crm_pilates.domain.repository import AggregateRoot

from crm_pilates.domain.scheduling.attendee import Attendee
from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.scheduling.classroom_type import ClassroomSubject
from crm_pilates.domain.scheduling.date_time_comparator import DateTimeComparator
from crm_pilates.domain.scheduling.duration import TimeUnit, MinuteTimeUnit


class Session:
    def __init__(
        self,
        classroom_id: UUID,
        name: str,
        position: int,
        subject: ClassroomSubject,
        start: datetime,
        classroom_duration: TimeUnit,
        attendees: [Attendee],
    ) -> None:
        self.__name: str = name
        self.__position: int = position
        self.__subject: ClassroomSubject = subject
        self.__attendees: List[Attendee] = deepcopy(attendees)
        self.__start: datetime = (
            start.astimezone(pytz.utc) if start.tzinfo is None else start
        )
        self.__stop: datetime = self.__start + timedelta(
            minutes=classroom_duration.to_unit(MinuteTimeUnit).value
        )
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
        return ScheduledSession(
            classroom.id,
            classroom.name,
            classroom.position,
            classroom.subject,
            start,
            classroom.duration.time_unit,
            classroom.attendees,
        )

    @property
    def id(self):
        return None


class ConfirmedSession(Session, AggregateRoot):
    def __init__(
        self,
        classroom_id: UUID,
        name: str,
        position: int,
        subject: ClassroomSubject,
        start: datetime,
        duration_time_unit: TimeUnit,
        attendees: [Attendee],
    ) -> None:
        super().__init__(
            classroom_id, name, position, subject, start, duration_time_unit, attendees
        )
        self._id = uuid.uuid4()

    @staticmethod
    def create(classroom: Classroom, start: datetime) -> ConfirmedSession:
        if (
            not DateTimeComparator(classroom.schedule.start, start)
            .same_day()
            .same_time()
            .before()
            .compare()
        ):
            raise InvalidSessionStartDateException(classroom, start)
        return ConfirmedSession(
            classroom.id,
            classroom.name,
            classroom.position,
            classroom.subject,
            start,
            classroom.duration.time_unit,
            classroom.attendees,
        )

    @property
    def id(self):
        return self._id

    def checkin(self, attendee: Attendee) -> Attendee:
        try:
            registered_attendee = next(
                filter(
                    lambda current_attendee: current_attendee == attendee,
                    self.attendees,
                )
            )
            registered_attendee.checkin()
            return registered_attendee
        except StopIteration:
            raise DomainException(
                f"Attendee with id {str(attendee.id)} could not be checked in"
            )

    def checkout(self, attendee: Attendee) -> Attendee:
        try:
            checked_out_attendee: Attendee = next(
                filter(
                    lambda current_attendee: current_attendee == attendee,
                    self.attendees,
                )
            )
            checked_out_attendee.checkout()
            return checked_out_attendee
        except StopIteration:
            raise DomainException(
                f"Attendee with id {str(attendee.id)} could not be checked out"
            )

    def cancel(self, attendee: Attendee) -> None:
        self.attendees.remove(attendee)

    def add_attendees(self, attendees: [Attendee]) -> None:
        if len(attendees) > self.position:
            raise DomainException(
                f"Cannot add attendees, there is {self.position} positions available, you tried to add {len(attendees)} attendees"
            )
        self.attendees.extend(list(set(attendees) - set(self.attendees)))


class InvalidSessionStartDateException(DomainException):
    def __init__(
        self, classroom: Classroom, start_date: datetime, *args: object
    ) -> None:
        if start_date < classroom.schedule.start:
            message = f"Classroom '{classroom.name}' starting at '{classroom.schedule.start.isoformat()}' cannot be set before"
        else:
            weekdays_difference = abs(
                classroom.schedule.start.date().weekday() - start_date.date().weekday()
            )
            closest_prior_date = datetime.combine(
                (start_date.date() - timedelta(days=weekdays_difference)),
                classroom.schedule.start.time(),
            ).replace(tzinfo=pytz.utc)
            closest_following_date = datetime.combine(
                (start_date.date() + timedelta(days=7 - weekdays_difference)),
                classroom.schedule.start.time(),
            ).replace(tzinfo=pytz.utc)
            message = f"Classroom '{classroom.name}' starting at '{classroom.schedule.start.isoformat()}' cannot be set at '{start_date.isoformat()}', closest possible dates are '{closest_prior_date.isoformat()}' or '{closest_following_date.isoformat()}'"
        super().__init__(message, *args)
