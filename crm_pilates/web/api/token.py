from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from crm_pilates.authenticating.authenticating_user import AuthenticatingUser
from crm_pilates.authenticating.authentication import (
    AuthenticationService,
)
from crm_pilates.infrastructure.services import concrete_authentication_service
from crm_pilates.web.schema.token import Token

router = APIRouter()


@router.post(
    "/token",
    status_code=status.HTTP_201_CREATED,
    tags=["authentication"],
    response_model=Token,
    responses={
        401: {"description": "Unauthorized access due to invalid username or password"}
    },
)
def create_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    authentication_service: AuthenticationService = Depends(
        concrete_authentication_service
    ),
):
    return authentication_service.authenticate(
        AuthenticatingUser(form_data.username, form_data.password)
    )
