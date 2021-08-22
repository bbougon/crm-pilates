from datetime import datetime
from typing import List
from uuid import UUID

from pydantic.main import BaseModel

from domain.classroom.duration import Duration
from web.presentation.domain.units import Units
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


class ClassroomResponse(BaseModel):
    name: str
    id: UUID
    position: int
    schedule: ScheduleReadResponse
    duration: DurationReadResponse


class ClassroomCreatedResponse(ClassroomResponse):
    attendees: List[AttendeeSchema]


class ClassroomReadResponse(ClassroomResponse):
    attendees: List[DetailedAttendee]

    @classmethod
    def to_duration(cls, duration: Duration):
        return {"duration": duration.time_unit.value, "time_unit": Units.units()[duration.time_unit.__class__.__name__]}
