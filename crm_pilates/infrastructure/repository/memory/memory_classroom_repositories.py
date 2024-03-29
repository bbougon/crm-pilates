import logging
from datetime import datetime
from typing import Iterator, List
from uuid import UUID

import pytz

from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.scheduling.classroom_repository import ClassroomRepository
from crm_pilates.domain.scheduling.date_time_comparator import DateTimeComparator
from crm_pilates.domain.repository import AggregateRoot
from crm_pilates.infrastructure.repository.memory.memory_repository import (
    MemoryRepository,
)


class MemoryClassroomRepository(ClassroomRepository, MemoryRepository):
    def get_classrooms_where_attendee_in(self, attendee_id: UUID) -> List[Classroom]:
        classrooms: List[Classroom] = []
        for classroom in self.entities:
            attendees = filter(
                lambda attendee: attendee.id == attendee_id, classroom.attendees
            )
            if attendees:
                classrooms.append(classroom)
        return classrooms


class MemoryClassRoomReadRepository(ClassroomRepository, MemoryRepository):
    def __init__(self, repository: ClassroomRepository) -> None:
        super().__init__()
        self.__repository = repository

    def persist(self, entity: AggregateRoot):
        raise NotImplementedError

    def get_all(self) -> List:
        return self.__repository.get_all()

    def get_by_id(self, id: UUID):
        classroom: Classroom = self.__repository.get_by_id(id)
        return classroom

    def get_next_classrooms_from(self, at_date: datetime) -> Iterator[Classroom]:
        classrooms: List[Classroom] = next(self.__repository.get_all())
        yield [
            classroom
            for classroom in classrooms
            if self.__in_between_dates(classroom, at_date.astimezone(pytz.utc))
        ]

    def get_classrooms_in_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Classroom]:
        classrooms: List[Classroom] = next(self.__repository.get_all())
        yield [
            classroom
            for classroom in classrooms
            if DateTimeComparator(classroom.schedule.start, end_date).before().compare()
            and DateTimeComparator(start_date, classroom.schedule.stop)
            .before()
            .compare()
        ]

    def __in_between_dates(self, classroom: Classroom, at_date: datetime) -> bool:
        logging.Logger("repository").debug(
            msg=f"classes: {self.__repository.get_all()}"
        )
        if classroom.schedule.stop:
            return (
                classroom.schedule.start.date()
                <= at_date.date()
                <= classroom.schedule.stop.date()
                and classroom.schedule.start.time() >= at_date.time()
            )
