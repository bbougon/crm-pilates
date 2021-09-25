from fastapi import APIRouter

from web.api import classroom, client, session
from web.api.health import health

api_router = APIRouter()
api_router.include_router(classroom.router)
api_router.include_router(client.router)
api_router.include_router(session.router)
api_router.include_router(health.router)
