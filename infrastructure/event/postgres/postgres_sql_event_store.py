import json
from functools import partial
from typing import List, Any
from uuid import UUID

import psycopg
import arrow
from psycopg.types.json import Jsonb

from event.event_store import EventStore, Event


class UUIDEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return str(o)
        return super().default(o)


class PostgresSQLEventStore(EventStore):

    def __init__(self, connection_info: dict) -> None:
        super().__init__()
        self.connection_url = f"postgresql://{connection_info['user']}:{connection_info['password']}@{connection_info['host']}:{connection_info['port']}/{connection_info['dbname']}"
        with psycopg.connect(self.connection_url) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS event (id uuid, root_id uuid, type varchar(100), timestamp_ timestamp, payload jsonb)")
            connection.commit()

    def persist(self, event: Event):
        with psycopg.connect(self.connection_url) as connection:
            uuid_dumps = partial(json.dumps, cls=UUIDEncoder)
            connection.execute("INSERT INTO event VALUES (%(id)s, %(root_id)s, %(type)s, %(timestamp_)s, %(payload)s)", {
                "id": event.id,
                "root_id": event.root_id,
                "type": event.type,
                "timestamp_": event.timestamp.isoformat(),
                "payload": Jsonb(event.payload, dumps=uuid_dumps)
            })
            connection.commit()

    def get_all(self) -> List[Event]:
        pass

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
