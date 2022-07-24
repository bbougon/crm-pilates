from datetime import datetime
from enum import Enum
from typing import Optional, Set
from uuid import UUID

from pydantic import BaseModel
from pydantic.class_validators import validator


class TimeUnit(Enum):
    HOUR = "HOUR"
    MINUTE = "MINUTE"


class Duration(BaseModel):
    duration: int
    unit: TimeUnit


class AttendeeSchema(BaseModel):
    id: UUID

    def __hash__(self) -> int:
        return hash(self.id)


def check_unique_attendees(v):
    unique_ids = set()
    for item in v:
        unique_ids.add(item["id"])
    if len(v) != len(unique_ids):
        raise ValueError("You provided the same attendee twice or more, please check the attendees and retry")
    return v


class ClassroomCreation(BaseModel):
    name: str
    position: int
    subject: str
    start_date: datetime
    stop_date: Optional[datetime]
    duration: Duration = Duration.parse_obj({"duration": 1, "unit": TimeUnit.HOUR})
    attendees: Optional[Set[AttendeeSchema]] = set()

    @validator("attendees", pre=True)
    def unique_attendees(cls, v):
        return check_unique_attendees(v)


class ClassroomPatch(BaseModel):
    attendees: Optional[Set[AttendeeSchema]] = set()

    @validator("attendees", pre=True)
    def unique_attendees(cls, v):
        return check_unique_attendees(v)
