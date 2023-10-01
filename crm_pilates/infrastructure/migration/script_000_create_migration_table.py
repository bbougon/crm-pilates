import sys
from sqlite3 import Row
from typing import List

import psycopg

from crm_pilates.domain.services import CipherServiceProvider
from crm_pilates.event.event_store import EVENT_VERSION
from crm_pilates.infrastructure.encryption.fernet_encryption_service import (
    FernetCipherService,
)
from crm_pilates.infrastructure.migration.migration_script import MigrationScript
from crm_pilates.settings import config


class MigrateEncryptSensitiveData(MigrationScript):
    def __init__(self, argv) -> None:
        super().__init__(self.__class__.__name__, argv)

    def run_script(self):
        with psycopg.connect(self.connection_url) as connection:
            rows: List[Row] = connection.execute(
                "SELECT id, payload::json#>'{firstname}', payload::json#>'{lastname}' FROM event WHERE type = "
                "'ClientCreated' AND payload ->> 'lastname' NOT LIKE '%==%' "
            ).fetchall()
            for row in rows:
                connection.execute(
                    "UPDATE event e SET payload = jsonb_set(jsonb_set(payload, '{firstname}', %(encrypted_firstname)s, true), '{lastname}', %(encrypted_lastname)s, true) WHERE id = %(id)s AND type = 'ClientCreated'",
                    {
                        "id": row[0],
                        "encrypted_firstname": f'"{CipherServiceProvider.service.encrypt(row[1]).decode("utf-8")}"',
                        "encrypted_lastname": f'"{CipherServiceProvider.service.encrypt(row[2]).decode("utf-8")}"',
                    },
                )
            connection.execute(
                "UPDATE event SET payload = jsonb_set(payload, '{version}', %(version)s, true) WHERE payload ->> 'version' IS NULL OR payload ->> 'version' LIKE '2'",
                {"version": f'"{EVENT_VERSION}"'},
            )
            connection.commit()


if __name__ == "__main__":
    CipherServiceProvider.service = FernetCipherService(config("SECRET_ENCRYPTION_KEY"))
    MigrateEncryptSensitiveData(sys.argv[1:]).execute()
