from datetime import datetime
from typing import List
from uuid import UUID

from pydantic.main import BaseModel

from web.schema.classroom_schemas import TimeUnit, AttendeeSchema


class ScheduleReadResponse(BaseModel):
    start: datetime
    stop: datetime = None


class DurationReadResponse(BaseModel):
    duration: int
    time_unit: TimeUnit


class DetailedAttendee(AttendeeSchema):
    firstname: str
    lastname: str


class ClassroomReadResponse(BaseModel):
    name: str
    id: UUID
    position: int
    schedule: ScheduleReadResponse
    duration: DurationReadResponse
    attendees: List[DetailedAttendee]
