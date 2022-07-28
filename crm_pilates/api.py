from fastapi import APIRouter

from crm_pilates.web.api import classroom, clients, session, health, token

api_router = APIRouter()
api_router.include_router(classroom.router)
api_router.include_router(clients.router)
api_router.include_router(session.router)
api_router.include_router(health.router)
api_router.include_router(token.router)
