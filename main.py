from fastapi import FastAPI

import settings
from api import api_router
from event.event_store import StoreLocator
from infrastructure.event.sqlite.sqlite_event_store import SQLiteEventStore
from infrastructure.event_to_domain_loader import EventToDomainLoader
from fastapi.middleware.cors import CORSMiddleware

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
)


app.include_router(api_router)
StoreLocator.store = SQLiteEventStore(settings.EVENT_STORE_PATH)
EventToDomainLoader().load()
