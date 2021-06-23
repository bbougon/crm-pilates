from domain.classroom_repository import ClassroomRepository
from infrastructure.tests.memory_repository import MemoryRepository


class MemoryClassroomRepository(ClassroomRepository, MemoryRepository):
    pass