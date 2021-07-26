from fastapi import APIRouter

from web.api import classroom, client

api_router = APIRouter()
api_router.include_router(classroom.router)
api_router.include_router(client.router)
