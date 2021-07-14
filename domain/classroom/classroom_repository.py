from domain.classroom.classroom import Classroom
from domain.repository import Repository


class ClassroomRepository(Repository):
    def _get_entity_type(self) -> str:
        return Classroom.__name__
