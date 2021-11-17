from __future__ import annotations
from uuid import UUID

from domains.classes.classroom.classroom import Session
from event.event_store import Event


class ExistingSessions(Event):

    def __init__(self, sessions: [ExistingSession], root_id: UUID = None) -> None:
        super().__init__(root_id)
        self.sessions = sessions

    def _to_payload(self):
        pass


class ExistingSession(Event):

    def __init__(self, session: Session, root_id: UUID = None) -> None:
        super().__init__(root_id)
        self.root_id = session.id
        self.name = session.name
        self.classroom_id = session.classroom_id
        self.position = session.position
        self.start = session.start
        self.stop = session.stop
        self.attendees = session.attendees

    def _to_payload(self):
        pass
