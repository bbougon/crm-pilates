from __future__ import annotations

import uuid
from abc import abstractmethod
from typing import List
from uuid import UUID


class AggregateRoot:
    def __init__(self):
        self._id = uuid.uuid4()

    @property
    def id(self) -> UUID:
        return self._id


class ValueObject:
    pass


class Repository:
    @abstractmethod
    def persist(self, entity: AggregateRoot):
        pass

    @abstractmethod
    def get_all(self) -> List:
        pass

    @abstractmethod
    def get_by_id(self, id: UUID):
        pass

    @abstractmethod
    def _get_entity_type(self) -> str:
        pass

    @property
    def _entity_type(self) -> str:
        return self._get_entity_type()
