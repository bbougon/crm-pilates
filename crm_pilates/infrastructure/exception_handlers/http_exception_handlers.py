from fastapi import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from crm_pilates.authenticating.authentication import AuthenticationException
from crm_pilates.domain.exceptions import AggregateNotFoundException, DomainException


async def aggregate_not_found_handler(
    request: Request, exc: AggregateNotFoundException
) -> JSONResponse:

    details = {
        "detail": [
            {
                "msg": f"{exc.entity_type} with id '{exc.unknown_id}' not found",
                "type": request.scope["endpoint"].__name__.replace("_", " "),
            }
        ]
    }
    return JSONResponse(content=details, status_code=status.HTTP_404_NOT_FOUND)


async def domain_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    details = {
        "detail": [
            {
                "msg": f"{exc.message}",
                "type": request.scope["endpoint"].__name__.replace("_", " "),
            }
        ]
    }
    return JSONResponse(content=details, status_code=status.HTTP_400_BAD_REQUEST)


async def authentication_exception_handler(
    request: Request, exc: AuthenticationException
) -> JSONResponse:
    details = {
        "detail": [
            {
                "msg": f"{exc.message}",
                "type": request.scope["endpoint"].__name__.replace("_", " "),
            }
        ]
    }
    return JSONResponse(content=details, status_code=status.HTTP_401_UNAUTHORIZED)
