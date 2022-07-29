from typing import Optional, Union, Any

import psycopg

from crm_pilates.authenticating.domain.user import User
from crm_pilates.authenticating.domain.user_repository import UserRepository
from crm_pilates.domain.exceptions import AggregateNotFoundException
from crm_pilates.infrastructure.repository.postgres.postgres_repository import (
    PostgresRepository,
    Mapper,
)
from psycopg import sql
from psycopg.rows import Row


class UserMapper(Mapper):
    def __init__(self, user: User) -> None:
        super().__init__()
        self.__user = user

    def table(self) -> str:
        return "users"

    def fields(self) -> [str]:
        fields: [str] = ["id", "username", "password"]
        fields.extend(self.__user.__dict__)
        fields.remove("_id")
        fields.remove("_username")
        fields.remove("_password")
        return fields

    def values(self) -> list[Union[str, int, Any]]:
        return [
            str(self.__user.id),
            self.__user.username,
            self.__user.password,
            self.__user.config,
        ]


class PostgresUserRepository(UserRepository, PostgresRepository):
    def get_by_username(self, username: str) -> User:
        with psycopg.connect(self.connection_url) as connection:
            query = sql.SQL("SELECT * FROM users WHERE username = {username}").format(
                username=sql.Literal(username)
            )
            row: Optional[Row] = connection.execute(query).fetchone()
        if row is None:
            raise AggregateNotFoundException(username, self._get_entity_type())
        return self._map(row)

    def _map(self, row: Optional[Row]) -> User:
        user = User(row[1], row[2])
        user._id = row[0]
        user.config = row[3]
        return user

    def _mapper(self, entity: User) -> Mapper:
        return UserMapper(entity)

    def _get_entity_type(self) -> str:
        return User.__name__
