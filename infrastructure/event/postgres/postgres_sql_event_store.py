import json
from datetime import datetime
from enum import Enum
from functools import partial
from typing import List, Any
from uuid import UUID

import arrow
import psycopg
from psycopg.rows import Row
from psycopg.types.json import Jsonb

from event.event_store import EventStore, Event
from infrastructure.event.sqlite.sqlite_event_store import MultipleJsonEncoders


class UUIDEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return str(o)
        return super().default(o)


class EnumEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Enum):
            return o.value
        return super().default(o)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class PostgresSQLEventStore(EventStore):

    def __init__(self, db_url: str) -> None:
        super().__init__()
        self.connection_url = db_url
        with psycopg.connect(self.connection_url) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS event (id uuid, root_id uuid, type varchar(100), timestamp_ timestamp, payload jsonb)")
            connection.commit()

    def persist(self, event: Event):
        with psycopg.connect(self.connection_url) as connection:
            uuid_dumps = partial(json.dumps, cls=MultipleJsonEncoders(UUIDEncoder, EnumEncoder, DateTimeEncoder))
            connection.execute("INSERT INTO event VALUES (%(id)s, %(root_id)s, %(type)s, %(timestamp_)s, %(payload)s)", {
                "id": event.id,
                "root_id": event.root_id,
                "type": event.type,
                "timestamp_": event.timestamp.isoformat(),
                "payload": Jsonb(event.payload, dumps=uuid_dumps)
            })
            connection.commit()

    def get_all(self) -> List[Event]:
        with psycopg.connect(self.connection_url) as connection:
            rows: List[Row] = connection.execute("SELECT * FROM EVENT").fetchall()
            events: List[Event] = list(map(lambda event: self.__map(event), rows))
            return events

    def get_by_id(self, id: UUID) -> Event:
        with psycopg.connect(self.connection_url) as connection:
            row = connection.execute("SELECT * FROM event WHERE id = %(event_id)s", {"event_id": str(id)}).fetchone()
            return self.__map(row)

    def __map(self, row) -> Event:
        event = Event(row[1])
        event.id = row[0]
        event.type = row[2]
        event.timestamp = arrow.get(row[3]).datetime
        event.payload = row[4]
        return event
