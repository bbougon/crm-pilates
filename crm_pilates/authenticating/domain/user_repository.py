from abc import abstractmethod

from crm_pilates.authenticating.domain.user import User
from crm_pilates.domain.repository import Repository


class UserRepository(Repository):

    def _get_entity_type(self) -> str:
        return User.__name__

    @abstractmethod
    def get_by_username(self, username: str) -> User:
        pass
