from datetime import datetime
from uuid import UUID

from domain.classroom.classroom import Session
from domain.classroom.session.session_repository import SessionRepository
from domain.repository import AggregateRoot
from infrastructure.repository.memory.memory_repository import MemoryRepository


class MemorySessionRepository(SessionRepository, MemoryRepository):

    def get_by_classroom_id_and_date(self, classroom_id: UUID, date: datetime) -> Session:
        for session in self.entities:
            if session.start == date and session.classroom_id == classroom_id:
                return session


class MemorySessionReadRepository(SessionRepository, MemoryRepository):

    def __init__(self, repository: MemorySessionRepository) -> None:
        super().__init__()
        self.repository = repository

    def get_by_classroom_id_and_date(self, classroom_id: UUID, date: datetime) -> Session:
        return self.repository.get_by_classroom_id_and_date(classroom_id, date)

    def get_by_id(self, id: UUID) -> Session:
        return self.repository.get_by_id(id)

    def persist(self, entity: AggregateRoot):
        raise NotImplementedError
