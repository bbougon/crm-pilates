from uuid import UUID


class DomainException(Exception):

    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)
        self.message = message


class AggregateNotFoundException(DomainException):

    def __init__(self, aggregate_id: UUID, entity_type: str, *args: object) -> None:
        super().__init__(f"Aggregate '{entity_type}' with id '{aggregate_id}' not found", *args)
        self.unknown_id: UUID = aggregate_id