from fastapi import FastAPI

from api import api_router
from infrastructure.event.event_store import StoreLocator
from tests.infrastructure.event.memory_event_store import MemoryEventStore

app = FastAPI(
    title="CRM Pilates",
    openapi_url="/openapi.json",
    version="1",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.include_router(api_router)
StoreLocator.store = MemoryEventStore()