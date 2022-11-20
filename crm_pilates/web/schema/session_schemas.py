from datetime import datetime
from typing import Set
from uuid import UUID

from pydantic import BaseModel
from pydantic.class_validators import validator


class SessionCheckin(BaseModel):
    classroom_id: UUID
    session_date: datetime
    attendee: UUID


class SessionCheckout(BaseModel):
    attendee: UUID


class AttendeeSessionCancellation(BaseModel):
    classroom_id: UUID
    session_date: datetime


class AttendeesAddition(BaseModel):
    classroom_id: UUID
    session_date: datetime
    attendees: Set[UUID]

    @validator("attendees", pre=True)
    def check_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError("Please provide at least one attendee")
        return v
