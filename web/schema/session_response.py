from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic.main import BaseModel


class Attendee(BaseModel):
    id: UUID
    firstname: str
    lastname: str
    attendance: str


class Schedule(BaseModel):
    start: datetime
    stop: datetime


class SessionResponse(BaseModel):
    id: Optional[UUID]
    name: str
    classroom_id: UUID
    subject: str
    position: int
    schedule: Schedule
    attendees: List[Attendee]
