from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer

from crm_pilates.authenticating.authentication import (
    AuthenticationService,
    AuthenticationException,
)
from crm_pilates.domain.exceptions import AggregateNotFoundException
from crm_pilates.infrastructure.services import concrete_authentication_service
from crm_pilates.web.api.exceptions import APIHTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authentication_service(
    token: str = Depends(oauth2_scheme),
    authentication_service: AuthenticationService = Depends(
        concrete_authentication_service
    ),
):
    try:
        authentication_service.validate_token(token)
    except AuthenticationException as e:
        raise APIHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message if e.message is not None else "Unauthorized",
        )
    except AggregateNotFoundException:
        raise APIHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
