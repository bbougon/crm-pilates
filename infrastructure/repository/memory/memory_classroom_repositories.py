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
