from datetime import datetime
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
    start_date: datetime
    duration: Duration = Duration.parse_obj({"duration": 1, "unit": TimeUnit.HOUR})
