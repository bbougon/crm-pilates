from abc import abstractmethod
from datetime import datetime

from domain.classroom.classroom import Classroom
from domain.repository import Repository


class ClassroomRepository(Repository):
    def _get_entity_type(self) -> str:
        return Classroom.__name__

    @abstractmethod
    def get_next_sessions_from(self, at_date: datetime):
        pass
