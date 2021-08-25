from datetime import datetime
from typing import List
from uuid import UUID

from pydantic.main import BaseModel

from web.schema.classroom_schemas import Duration


class Attendee(BaseModel):
    client_id: UUID
    firstname: str
    lastname: str


class Schedule(BaseModel):
    start: datetime
    stop: datetime


class Session(BaseModel):
    name: str
    classroom_id: UUID
    id: UUID
    position: int
    schedule: Schedule
    duration: Duration
    attendees: List[Attendee]
