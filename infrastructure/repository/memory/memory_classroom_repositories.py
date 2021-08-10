from datetime import datetime
from typing import Iterator, List
from uuid import UUID

from domain.classroom.classroom import Classroom
from domain.classroom.classroom_repository import ClassroomRepository
from domain.repository import AggregateRoot
from infrastructure.repository.memory.memory_repository import MemoryRepository


class MemoryClassroomRepository(ClassroomRepository, MemoryRepository):
    pass


class MemoryClassRoomReadRepository(ClassroomRepository, MemoryRepository):

    def __init__(self, repository: ClassroomRepository) -> None:
        super().__init__()
        self.__repository = repository

    def persist(self, entity: AggregateRoot):
        raise NotImplementedError

    def get_by_id(self, id: UUID):
        classroom: Classroom = self.__repository.get_by_id(id)
        return classroom

    def get_next_classrooms_from(self, at_date: datetime) -> Iterator[Classroom]:
        classrooms: List[Classroom] = next(self.__repository.get_all())
        yield [classroom for classroom in classrooms if self.__in_between_dates(classroom, at_date)]

    def __in_between_dates(self, classroom, at_date):
        if classroom.schedule.stop:
            return classroom.schedule.start > at_date < classroom.schedule.stop
        return classroom.schedule.start.date() == at_date.date() and classroom.schedule.start.time() >= at_date.time()
