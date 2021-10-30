from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import pytz

from command.saga_handler import Saga


@dataclass
class SessionCheckinSaga(Saga):
    classroom_id: UUID
    _session_date: datetime
    attendee: UUID

    @property
    def session_date(self) -> datetime:
        return self._session_date.astimezone(pytz.utc)
