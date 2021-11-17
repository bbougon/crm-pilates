from abc import abstractmethod
from datetime import datetime
from uuid import UUID

from domains.classes.classroom.classroom import Session
from domains.repository import Repository


class SessionRepository(Repository):
    def _get_entity_type(self) -> str:
        return Session.__name__

    @abstractmethod
    def get_by_classroom_id_and_date(self, classroom_id: UUID, date: datetime) -> Session:
        pass