from fastapi import APIRouter

from web.api import classroom, clients, session, health

api_router = APIRouter()
api_router.include_router(classroom.router)
api_router.include_router(clients.router)
api_router.include_router(session.router)
api_router.include_router(health.router)
