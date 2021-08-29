from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SessionCheckin(BaseModel):
    classroom_id: UUID
    session_date: datetime
    attendee: UUID
