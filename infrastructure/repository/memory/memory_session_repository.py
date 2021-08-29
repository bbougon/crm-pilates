from domain.classroom.session_repository import SessionRepository
from infrastructure.repository.memory.memory_repository import MemoryRepository


class MemorySessionRepository(SessionRepository, MemoryRepository):
    pass
