from dataclasses import dataclass
from uuid import UUID


@dataclass
class AvailableCredits:
    subject: str
    amount: int


@dataclass
class DetailedAttendee:
    id: UUID
    firstname: str
    lastname: str
    attendance: str
    credits: AvailableCredits = None
