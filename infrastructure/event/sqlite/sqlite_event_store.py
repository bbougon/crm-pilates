import json
import sqlite3
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from event.event_store import EventStore, Event


class MultipleJsonEncoders():
    def __init__(self, *encoders):
        self.encoders = encoders
        self.args = ()
        self.kwargs = {}

    def default(self, obj):
        for encoder in self.encoders:
            try:
                return encoder(*self.args, **self.kwargs).default(obj)
            except TypeError:
                pass
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        encoder = json.JSONEncoder(*args, **kwargs)
        encoder.default = self.default
        return encoder


class UUIDEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return o.hex
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


class SQLiteEventStore(EventStore):

    def __init__(self, db_file: str) -> None:
        super().__init__()
        self.db_file = db_file

    def persist(self, event: Event):
        connect, cursor = self.__connect_and_get_cursor()
        cursor.execute("INSERT INTO event VALUES (?, ?, ?, ?, ?)", (str(event.id), str(event.root_id), event.type, event.timestamp.isoformat(), json.dumps(event.payload, cls = MultipleJsonEncoders(UUIDEncoder, EnumEncoder, DateTimeEncoder))))
        connect.commit()
        connect.close()
        pass

    def get_by_id(self, id: UUID) -> Event:
        connect, cursor = self.__connect_and_get_cursor()
        cursor.execute("SELECT * FROM event WHERE id=:event_id", {"event_id": str(id)})
        row = cursor.fetchone()
        event = self.__map(row)
        connect.close()
        return event

    def __connect_and_get_cursor(self):
        connect = sqlite3.connect(self.db_file)
        cursor = connect.cursor()
        return connect, cursor

    def __map(self, row) -> Event:
        event = Event(UUID(row[1]))
        event.id = UUID(row[0])
        event.type = row[2]
        event.timestamp = datetime.fromisoformat(row[3])
        return event
