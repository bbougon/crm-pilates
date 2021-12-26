from dataclasses import dataclass, field
from typing import List
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
    credits: List[AvailableCredits] = field(default_factory=list)
