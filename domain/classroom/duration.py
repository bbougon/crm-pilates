import math
from dataclasses import dataclass
from enum import Enum


class TimeUnit(Enum):
    HOUR = "HOUR"
    MINUTE = "MINUTE"


class TimeUnitConvertor:

    def __init__(self, conversion_ratio: dict) -> None:
        super().__init__()
        self.conversion_ratio = conversion_ratio

    def convert(self, from_time_unit: TimeUnit, duration: int) -> int:
        return math.ceil(self.conversion_ratio[from_time_unit.value] * duration)


class HourConvertor(TimeUnitConvertor):

    def __init__(self) -> None:
        super().__init__({TimeUnit.HOUR.value: 1})


class MinuteConvertor(TimeUnitConvertor):

    def __init__(self) -> None:
        super().__init__({TimeUnit.MINUTE.value: 1, TimeUnit.HOUR.value: 60})


class TimeUnitConvertors:
    __time_unit_convertors: dict = {
        TimeUnit.HOUR: HourConvertor(),
        TimeUnit.MINUTE: MinuteConvertor()
    }

    @classmethod
    def to_time_unit(cls, to_time_unit: TimeUnit, from_time_unit: TimeUnit, duration):
        return TimeUnitConvertors.__time_unit_convertors[to_time_unit].convert(from_time_unit, duration)


@dataclass
class Duration:
    time_unit: TimeUnit
    duration: int

    def to_minutes(self):
        return TimeUnitConvertors.to_time_unit(TimeUnit.MINUTE, self.time_unit, self.duration)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Duration) and self.duration == o.duration and self.time_unit == o.time_unit
