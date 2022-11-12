import sys

import psycopg

from crm_pilates.infrastructure.migration.migration_script import MigrationScript


class MigrateClassroomToScheduledScript(MigrationScript):
    def __init__(self, argv) -> None:
        super().__init__(self.__class__.__name__, argv)

    def run_script(self):
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(
                "UPDATE event SET type = 'ClassroomScheduled' WHERE type = 'ClassroomCreated' "
            )
            connection.execute(
                "UPDATE event SET payload = jsonb_set(payload, '{version}', '\"2\"', true) WHERE payload ->> 'version' IS NULL OR payload ->> 'version' LIKE '1'"
            )
            connection.commit()


if __name__ == "__main__":
    MigrateClassroomToScheduledScript(sys.argv[1:]).execute()
