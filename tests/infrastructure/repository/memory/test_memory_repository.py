import uuid

import pytest

from domain.exceptions import AggregateNotFoundException
from domain.repository import Repository
from infrastructure.repository.memory.memory_repository import MemoryRepository


class Custom:
    pass


class CustomRepository(Repository):
    def _get_entity_type(self):
        return Custom.__name__


class CustomMemoryRepository(CustomRepository, MemoryRepository):
    pass


def test_aggregate_not_found():
    unknown_id = uuid.uuid4()
    with pytest.raises(AggregateNotFoundException) as e:
        CustomMemoryRepository().get_by_id(unknown_id)

    assert e.value.unknown_id == unknown_id
    assert e.value.message == f"Aggregate 'Custom' with id '{unknown_id}' not found"
