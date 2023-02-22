from abc import abstractmethod
from datetime import datetime
from typing import List
from uuid import UUID

from crm_pilates.domain.scheduling.classroom import Classroom
from crm_pilates.domain.repository import Repository


class ClassroomRepository(Repository):
    def _get_entity_type(self) -> str:
        return Classroom.__name__

    @abstractmethod
    def get_next_classrooms_from(self, at_date: datetime):
        pass

    @abstractmethod
    def get_classrooms_in_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Classroom]:
        pass

    @abstractmethod
    def get_classrooms_where_attendee_in(self, attendee_id: UUID) -> List[Classroom]:
        pass
