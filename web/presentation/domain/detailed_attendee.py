from dataclasses import dataclass
from uuid import UUID


@dataclass
class DetailedAttendee:
    id: UUID
    firstname: str
    lastname: str
    attendance: str
