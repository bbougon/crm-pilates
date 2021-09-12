from __future__ import annotations

from abc import abstractmethod
from datetime import datetime


class Comparator:

    def __init__(self, obj, object_to_compare) -> None:
        super().__init__()
        self._obj = obj
        self._obj_to_compare = object_to_compare

    @abstractmethod
    def compare(self) -> bool:
        pass


class SameDayComparator(Comparator):

    def __init__(self, date: datetime, date_to_compare: datetime) -> None:
        super().__init__(date, date_to_compare)

    def compare(self) -> bool:
        return self._obj.date().weekday() == self._obj_to_compare.date().weekday()


class SameTimeComparator(Comparator):

    def __init__(self, obj, object_to_compare) -> None:
        super().__init__(obj, object_to_compare)

    def compare(self) -> bool:
        return self._obj.time() == self._obj_to_compare.time()


class SameDateComparator(Comparator):

    def __init__(self, obj, object_to_compare) -> None:
        super().__init__(obj, object_to_compare)

    def compare(self) -> bool:
        return self._obj.date() == self._obj_to_compare.date()


class DateTimeComparator(Comparator):

    def __init__(self, date: datetime, date_to_compare: datetime) -> None:
        super().__init__(date, date_to_compare)
        self.comparisons = []

    def same_day(self) -> DateTimeComparator:
        self.comparisons.append(SameDayComparator(self._obj, self._obj_to_compare).compare())
        return self

    def same_time(self) -> DateTimeComparator:
        self.comparisons.append(SameTimeComparator(self._obj, self._obj_to_compare).compare())
        return self

    def before(self) -> DateTimeComparator:
        self.comparisons.append(not self._obj_to_compare < self._obj)
        return self

    def same_date(self) -> DateTimeComparator:
        self.comparisons.append(SameDateComparator(self._obj, self._obj_to_compare).compare())
        return self

    def compare(self) -> bool:
        return False if list(filter(lambda result: result is False, self.comparisons)) else True
