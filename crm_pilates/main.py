from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from crm_pilates import settings
from crm_pilates.api import api_router
from crm_pilates.event.event_store import StoreLocator
from crm_pilates.infrastructure.event.postgres.postgres_sql_event_store import PostgresSQLEventStore
from crm_pilates.infrastructure.event_to_domain_loader import EventToDomainLoader
from crm_pilates.infrastructure.migration.migration import Migration

app = FastAPI(
    title="CRM Pilates",
    openapi_url="/openapi.json",
    version="1",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-link", "X-Link"]
)


app.include_router(api_router)

StoreLocator.store = PostgresSQLEventStore(settings.DATABASE_URL)
Migration(settings.DATABASE_URL).migrate()
EventToDomainLoader().load()
