from fastapi import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from crm_pilates.domain.exceptions import AggregateNotFoundException

resource_map = {"clients": "client"}


async def aggregate_not_found_handler(
    request: Request, exc: AggregateNotFoundException
) -> JSONResponse:
    def extract_type(request) -> str:
        return f"{request.method.lower()} {resource_map[request.scope['path'].split('/')[1]]}"

    details = {
        "detail": [
            {
                "msg": f"{exc.entity_type} with id '{exc.unknown_id}' not found",
                "type": (extract_type(request)),
            }
        ]
    }
    return JSONResponse(content=details, status_code=status.HTTP_404_NOT_FOUND)
