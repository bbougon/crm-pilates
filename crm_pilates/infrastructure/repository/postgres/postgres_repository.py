from abc import abstractmethod
from typing import List, Union
from uuid import UUID

import psycopg
from psycopg import sql

from crm_pilates.domain.repository import Repository, AggregateRoot


class Mapper:

    @abstractmethod
    def table(self) -> str:
        pass

    @abstractmethod
    def fields(self) -> [str]:
        pass

    @abstractmethod
    def values(self) -> Union[str, int]:
        pass


class PostgresRepository(Repository):

    def __init__(self, connection_url: str) -> None:
        super().__init__()
        self.__connection_url = connection_url

    @property
    def connection_url(self):
        return self.__connection_url

    @abstractmethod
    def _mapper(self, entity) -> Mapper:
        pass

    def persist(self, entity: AggregateRoot):
        with psycopg.connect(self.__connection_url) as connection:
            mapper: Mapper = self._mapper(entity)
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(mapper.table()), sql.SQL(",").join(map(sql.Identifier, mapper.fields())),
                sql.SQL(",").join(map(sql.Literal, mapper.values())))
            connection.execute(query)
            connection.commit()

    def get_all(self) -> List:
        raise NotImplementedError

    def get_by_id(self, id: UUID):
        raise NotImplementedError
