from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from crm_pilates.authenticating.authentication import (
    AuthenticationService,
)
from crm_pilates.infrastructure.services import concrete_authentication_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authentication_service(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthenticationService = Depends(concrete_authentication_service),
):
    auth_service.validate_token(token)
