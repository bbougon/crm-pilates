from datetime import datetime
from typing import List
from uuid import UUID

from pydantic.main import BaseModel

from web.schema.classroom_creation import TimeUnit


class ScheduleReadResponse(BaseModel):
    start: datetime
    stop: datetime = None


class DurationReadResponse(BaseModel):
    duration: int
    time_unit: TimeUnit


class ClassroomReadResponse(BaseModel):
    name: str
    id: UUID
    position: int
    schedule: ScheduleReadResponse
    duration: DurationReadResponse
    attendees: List[UUID]