from typing import List
from uuid import UUID

from domain.exceptions import AggregateNotFoundException
from domain.repository import Repository, AggregateRoot


class MemoryRepository(Repository):

    def __init__(self) -> None:
        super().__init__()
        self.entities = []

    def persist(self, entity: AggregateRoot):
        self.entities.append(entity)

    def get_all(self) -> List:
        yield self.entities

    def get_by_id(self, id: UUID):
        retrieved_entity = [entity for entity in self.entities if entity._id == id]
        if not retrieved_entity:
            raise AggregateNotFoundException(id, self._entity_type)
        return retrieved_entity[0]
