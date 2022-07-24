from __future__ import annotations
from enum import Enum
from uuid import UUID

from crm_pilates.domain.exceptions import DomainException
from crm_pilates.domain.repository import AggregateRoot


class Attendee(AggregateRoot):

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

    def checkout(self):
        if self.attendance is not Attendance.CHECKED_IN:
            raise DomainException("Cannot checkout as attendee is already registered (i.e not checked in).")
        self.attendance = Attendance.REGISTERED

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Attendee) and self.id == o.id


class Attendance(Enum):
    REGISTERED = "REGISTERED"
    CHECKED_IN = "CHECKED_IN"
