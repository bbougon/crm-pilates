from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Type


class TimeUnit:
    def __init__(self, value: int) -> None:
        super().__init__()
        self._value = value

    @abstractmethod
    def to_unit(self, to_unit: Type[TimeUnit]):
        pass

    @property
    def value(self) -> int:
        return self._value


class HourTimeUnit(TimeUnit):
    units: dict = {"MinuteTimeUnit": 60, "HourTimeUnit": 1}

    def to_unit(self, to_unit: Type[TimeUnit]) -> TimeUnit:
        return to_unit(self._value * self.units[to_unit.__name__])


class MinuteTimeUnit(TimeUnit):
    units: dict = {"MinuteTimeUnit": 1, "HourTimeUnit": 1 / 60}

    def to_unit(self, to_unit: Type[TimeUnit]) -> TimeUnit:
        return to_unit(self._value * self.units[to_unit.__name__])


class TimeUnits:

    time_units: dict = {"HOUR": HourTimeUnit, "MINUTE": MinuteTimeUnit}

    @classmethod
    def from_duration(cls, unit, duration) -> TimeUnit:
        return cls.time_units[unit](duration)


@dataclass
class Duration:
    time_unit: TimeUnit

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Duration)
            and isinstance(o.time_unit, self.time_unit.__class__)
            and self.time_unit.value == o.time_unit.value
        )
