import uuid
from datetime import date, time
from enum import Enum

from domain.repository import AggregateRoot


class TimeUnit(Enum):
    HOUR = "HOUR"
    MINUTE = "MINUTE"


class Duration():

    time_unit: TimeUnit
    duration: int

    def __init__(self, duration: int, time_unit: TimeUnit) -> None:
        super().__init__()
        self.duration = duration
        self.time_unit = time_unit

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Duration) and self.duration == o.duration and self.time_unit == o.time_unit


class Classroom(AggregateRoot):

    name:str
    schedule:str
    start_date:date
    duration:Duration

    def __init__(self):
        self.id = uuid.uuid4()


    @staticmethod
    def create(name:str, schedule:time, start_date: date, duration: Duration = Duration(1, TimeUnit.HOUR)):
        classroom = Classroom()
        classroom.name = name
        classroom.schedule = schedule
        classroom.start_date = start_date
        classroom.duration = duration
        return classroom