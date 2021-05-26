from fastapi import APIRouter

from web.api import classroom


api_router = APIRouter()
api_router.include_router(classroom.router)
