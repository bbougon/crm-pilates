from crm_pilates.authenticating.domain.user import User
from crm_pilates.authenticating.domain.user_repository import UserRepository
from crm_pilates.domain.exceptions import AggregateNotFoundException
from crm_pilates.infrastructure.repository.memory.memory_repository import (
    MemoryRepository,
)


class MemoryUserRepository(UserRepository, MemoryRepository):
    def get_by_username(self, username: str) -> User:
        for user in self.entities:
            if user.username == username:
                return user
        raise AggregateNotFoundException(username, "User")
