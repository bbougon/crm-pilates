from domain.classroom.classroom_repository import ClassroomRepository
from infrastructure.repository.memory.memory_repository import MemoryRepository


class MemoryClassroomRepository(ClassroomRepository, MemoryRepository):
    pass