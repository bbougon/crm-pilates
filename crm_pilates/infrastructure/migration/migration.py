from uuid import UUID

import psycopg

from crm_pilates.infrastructure.event.sqlite.sqlite_event_store import MultipleJsonEncoders, UUIDEncoder, EnumEncoder, \
    DateTimeEncoder


class Migration:

    def __init__(self, connection_url: str) -> None:
        super().__init__()
        self.connection_url = connection_url
        self.encoders = MultipleJsonEncoders(UUIDEncoder, EnumEncoder, DateTimeEncoder)

    def migrate(self):
        self.__migrate_to_version_1()

    def get_event(self, id: UUID):
        with psycopg.connect(self.connection_url) as connection:
            row = connection.execute("SELECT * FROM event WHERE id = %(event_id)s", {"event_id": str(id)}).fetchone()
            return row

    def __migrate_to_version_1(self):
        with psycopg.connect(self.connection_url) as connection:
            connection.execute("UPDATE event SET payload = jsonb_set(payload, '{subject}', '\"MACHINE_TRIO\"', true) WHERE payload ->> 'position' = '3' AND UPPER(payload ->> 'name') LIKE UPPER('%machine%') AND payload ->> 'version' IS NULL")
            connection.execute("UPDATE event SET payload = jsonb_set(payload, '{subject}', '\"MACHINE_DUO\"', true) WHERE payload ->> 'position' = '2' AND UPPER(payload ->> 'name') LIKE UPPER('%machine%') AND payload ->> 'version' IS NULL")
            connection.execute("UPDATE event SET payload = jsonb_set(payload, '{subject}', '\"MAT\"', true) WHERE UPPER(payload ->> 'name') NOT LIKE UPPER('%machine%') AND payload ->> 'version' IS NULL")
            connection.execute("UPDATE event SET payload = jsonb_set(payload, '{version}', '\"1\"', true) WHERE payload ->> 'version' IS NULL")
            connection.commit()
