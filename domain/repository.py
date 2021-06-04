from abc import abstractmethod
from uuid import UUID


class AggregateRoot:
    pass


class Repository():

    @abstractmethod
    def persist(self, entity: AggregateRoot):
        pass

    @abstractmethod
    def get_by_id(self, id: UUID):
        pass