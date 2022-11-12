from crm_pilates.infrastructure.migration.script_002_create_user_table import (
    CreateUserTableScript,
)
from tests.infrastructure.migration.test_migration import PILATES_TEST
import psycopg


def test_should_create_table_user(drop_tables):
    CreateUserTableScript(PILATES_TEST).execute()

    with psycopg.connect(PILATES_TEST) as connection:
        result = connection.execute(
            "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'public' AND table_type LIKE 'BASE TABLE' AND TABLE_NAME = 'users';"
        )
        assert result is not None
