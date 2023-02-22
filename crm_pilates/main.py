import logging

from crm_pilates import settings, app  # noqa
from crm_pilates.domain.services import CipherServiceProvider
from crm_pilates.event.event_store import StoreLocator
from crm_pilates.infrastructure.encryption.fernet_encryption_service import (
    FernetCipherService,
)
from crm_pilates.infrastructure.event.postgres.postgres_sql_event_store import (
    PostgresSQLEventStore,
)
from crm_pilates.infrastructure.event_to_domain_loader import EventToDomainLoader
from crm_pilates.infrastructure.migration.migration import Migration
from crm_pilates.settings import config

StoreLocator.store = PostgresSQLEventStore(settings.DATABASE_URL)
CipherServiceProvider.service = FernetCipherService(config("SECRET_ENCRYPTION_KEY"))
logger = logging.getLogger("migration")
migrations = [migration for migration in Migration(settings.DATABASE_URL).migrate()]
logger.info(f"Migration run {len(migrations)} scripts")

EventToDomainLoader().load()
