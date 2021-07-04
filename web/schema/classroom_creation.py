from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TimeUnit(Enum):
    HOUR = "HOUR"
    MINUTE = "MINUTE"


class Duration(BaseModel):
    duration:int
    unit:TimeUnit


class ClassroomCreation(BaseModel):
    name: str
    position: int
    start_date: datetime
    stop_date: Optional[datetime]
    duration: Duration = Duration.parse_obj({"duration": 1, "unit": TimeUnit.HOUR})
