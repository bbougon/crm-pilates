from datetime import datetime
from uuid import UUID

from domain.classroom.classroom import Session
from domain.classroom.session_repository import SessionRepository
from infrastructure.repository.memory.memory_repository import MemoryRepository


class MemorySessionRepository(SessionRepository, MemoryRepository):

    def get_by_classroom_id_and_date(self, classroom_id: UUID, date: datetime) -> Session:
        for session in self.entities:
            if session.start == date and session.classroom_id == classroom_id:
                return session
