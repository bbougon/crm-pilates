from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from crm_pilates import settings
from crm_pilates.api import api_router
from crm_pilates.authenticating.authentication import AuthenticationException
from crm_pilates.domain.exceptions import AggregateNotFoundException, DomainException
from crm_pilates.infrastructure.exception_handlers.http_exception_handlers import (
    aggregate_not_found_handler,
    domain_exception_handler,
    authentication_exception_handler,
)

app = FastAPI(
    title="CRM Pilates",
    openapi_url="/openapi.json",
    version="1",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_exception_handler(
    exc_class_or_status_code=AggregateNotFoundException,
    handler=aggregate_not_found_handler,
)

app.add_exception_handler(
    exc_class_or_status_code=DomainException,
    handler=domain_exception_handler,
)

app.add_exception_handler(
    exc_class_or_status_code=AuthenticationException,
    handler=authentication_exception_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-link", "X-Link"],
)


app.include_router(api_router)
