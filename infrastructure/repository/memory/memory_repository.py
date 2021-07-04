from uuid import UUID

from domain.repository import Repository, AggregateRoot


class MemoryRepository(Repository):

    def __init__(self) -> None:
        super().__init__()
        self.entities = []

    def persist(self, entity: AggregateRoot):
        self.entities.append(entity)

    def get_by_id(self, id: UUID):
        retrieved_entity = [entity for entity in self.entities if entity.id == id]
        return retrieved_entity[0]
