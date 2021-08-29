from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from command.saga_handler import Saga


@dataclass
class SessionCheckinSaga(Saga):
    classroom_id: UUID
    session_date: datetime
    attendee: UUID
