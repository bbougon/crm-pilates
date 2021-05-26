from fastapi import FastAPI

from api import api_router

app = FastAPI(
    title="CRM Pilates"
)

app.include_router(api_router)
