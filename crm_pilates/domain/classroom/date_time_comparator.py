from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, date, time


class Comparator:

    def __init__(self, obj_to_compare, obj) -> None:
        super().__init__()
        self._object_to_compare = obj_to_compare
        self._object = obj

    @abstractmethod
    def compare(self) -> bool:
        pass


class SameDayComparator(Comparator):

    def __init__(self, date_: date, date_to_compare: date) -> None:
        super().__init__(date_, date_to_compare)

    def compare(self) -> bool:
        return self._object_to_compare.weekday() == self._object.weekday()


class SameTimeComparator(Comparator):

    def __init__(self, date_to_compare: time, date_: time) -> None:
        super().__init__(date_to_compare, date_)

    def compare(self) -> bool:
        return self._object_to_compare == self._object


class SameDateComparator(Comparator):

    def __init__(self, date_to_compare: date, date_: date) -> None:
        super().__init__(date_to_compare, date_)

    def compare(self) -> bool:
        return self._object_to_compare == self._object


class SameMonthComparator(Comparator):

    def __init__(self, obj_to_compare: date, obj: date) -> None:
        super().__init__(obj_to_compare, obj)

    def compare(self) -> bool:
        return self._object_to_compare.month == self._object.month


class DateComparator(Comparator):

    def __init__(self, date_to_compare: date, date_: date) -> None:
        super().__init__(date_to_compare, date_)
        self.comparisons = []

    def same_date(self) -> DateComparator:
        self.comparisons.append(SameDateComparator(self._object_to_compare, self._object).compare())
        return self

    def same_day(self) -> DateComparator:
        self.comparisons.append(SameDayComparator(self._object_to_compare, self._object).compare())
        return self

    def same_month(self) -> DateComparator:
        self.comparisons.append(SameMonthComparator(self._object_to_compare, self._object).compare())
        return self

    def before(self) -> DateComparator:
        self.comparisons.append(self._object_to_compare <= self._object)
        return self

    def compare(self) -> bool:
        return False if list(filter(lambda result: result is False, self.comparisons)) else True


class DateTimeComparator(DateComparator, Comparator):

    def __init__(self, date_to_compare: datetime, date_: datetime) -> None:
        super().__init__(date_to_compare, date_)
        self.comparisons = []

    def same_time(self) -> DateTimeComparator:
        self.comparisons.append(SameTimeComparator(self._object_to_compare.time(), self._object.time()).compare())
        return self

    def same_date(self) -> DateTimeComparator:
        self.comparisons.append(SameDateComparator(self._object_to_compare.date(), self._object.date()).compare())
        return self

    def compare(self) -> bool:
        return False if list(filter(lambda result: result is False, self.comparisons)) else True
