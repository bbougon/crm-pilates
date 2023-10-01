import sys

import psycopg

from crm_pilates.infrastructure.migration.migration_script import MigrationScript


class ThirdMigrationScriptForTest(MigrationScript):
    def __init__(self, argv) -> None:
        super().__init__(self.__class__.__name__, argv)

    def run_script(self):
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(
                "SELECT * FROM event",
            )


if __name__ == "__main__":
    ThirdMigrationScriptForTest(sys.argv[1:]).execute()
