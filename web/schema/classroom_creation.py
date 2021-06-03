from datetime import date, time
from enum import Enum

from pydantic import BaseModel


class TimeUnit(Enum):
    HOUR = "HOUR"
    MINUTE = "MINUTE"


class Duration(BaseModel):
    duration:int
    unit:TimeUnit


class ClassroomCreation(BaseModel):
    name: str
    schedule: time
    start_date: date
    duration: Duration = Duration.parse_obj({"duration": 1, "unit": TimeUnit.HOUR})
