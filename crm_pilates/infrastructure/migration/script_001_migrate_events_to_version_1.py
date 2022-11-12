import sys

from crm_pilates.infrastructure.migration.migration_script import MigrationScript
import psycopg


class MigrateEventsToVersion1Script(MigrationScript):
    def __init__(self, argv) -> None:
        super().__init__(self.__class__.__name__, argv)

    def run_script(self):
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(
                "UPDATE event SET payload = jsonb_set(payload, '{subject}', '\"MACHINE_TRIO\"', true) WHERE payload ->> 'position' = '3' AND UPPER(payload ->> 'name') LIKE UPPER('%machine%') AND payload ->> 'version' IS NULL"
            )
            connection.execute(
                "UPDATE event SET payload = jsonb_set(payload, '{subject}', '\"MACHINE_DUO\"', true) WHERE payload ->> 'position' = '2' AND UPPER(payload ->> 'name') LIKE UPPER('%machine%') AND payload ->> 'version' IS NULL"
            )
            connection.execute(
                "UPDATE event SET payload = jsonb_set(payload, '{subject}', '\"MAT\"', true) WHERE UPPER(payload ->> 'name') NOT LIKE UPPER('%machine%') AND payload ->> 'version' IS NULL"
            )
            connection.execute(
                "UPDATE event SET payload = jsonb_set(payload, '{version}', '\"1\"', true) WHERE payload ->> 'version' IS NULL"
            )
            connection.commit()


if __name__ == "__main__":
    MigrateEventsToVersion1Script(sys.argv[1:]).execute()
