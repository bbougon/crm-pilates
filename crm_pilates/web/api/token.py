from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from crm_pilates.domain.exceptions import AggregateNotFoundException
from crm_pilates.infrastructure.services import concrete_authentication_service
from crm_pilates.authenticating.authentication import AuthenticationService, AuthenticationException
from crm_pilates.authenticating.authenticating_user import AuthenticatingUser
from crm_pilates.web.schema.token import Token

router = APIRouter()


@router.post("/token",
             status_code=status.HTTP_201_CREATED,
             response_model=Token
             )
def create_token(form_data: OAuth2PasswordRequestForm = Depends(), authentication_service: AuthenticationService = Depends(concrete_authentication_service)):
    try:
        return authentication_service.authenticate(AuthenticatingUser(form_data.username, form_data.password))
    except (AggregateNotFoundException, AuthenticationException):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
