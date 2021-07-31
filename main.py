from fastapi import FastAPI

import settings
from api import api_router
from event.event_store import StoreLocator
from infrastructure.event.sqlite.sqlite_event_store import SQLiteEventStore

app = FastAPI(
    title="CRM Pilates",
    openapi_url="/openapi.json",
    version="1",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router)
StoreLocator.store = SQLiteEventStore(settings.EVENT_STORE_PATH)
