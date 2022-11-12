import sys

from crm_pilates.infrastructure.migration.migration_script import MigrationScript
import psycopg


class CreateUserTableScript(MigrationScript):
    def __init__(self, argv) -> None:
        super().__init__(self.__class__.__name__, argv)

    def run_script(self):
        with psycopg.connect(self.connection_url) as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS users (id text, username text, password text, config text)"""
            )
            connection.commit()


if __name__ == "__main__":
    CreateUserTableScript(sys.argv[1:]).execute()
