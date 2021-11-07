from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import settings
from api import api_router
from event.event_store import StoreLocator
from infrastructure.event.postgres.postgres_sql_event_store import PostgresSQLEventStore
from infrastructure.event_to_domain_loader import EventToDomainLoader

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
EventToDomainLoader().load()
