from domain.classroom.classroom import Session
from domain.repository import Repository


class SessionRepository(Repository):
    def _get_entity_type(self) -> str:
        return Session.__name__
