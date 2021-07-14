import uuid
from abc import abstractmethod
from uuid import UUID


class AggregateRoot:
    def __init__(self):
        self.id = uuid.uuid4()


class Repository():

    @abstractmethod
    def persist(self, entity: AggregateRoot):
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