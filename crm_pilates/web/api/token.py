from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from crm_pilates.infrastructure.services import concrete_authentication_service
from crm_pilates.authenticating.authentication import AuthenticationService
from crm_pilates.authenticating.user import User
from crm_pilates.web.schema.token import Token

router = APIRouter()


@router.post("/token",
             status_code=status.HTTP_201_CREATED,
             response_model=Token
             )
def create_token(form_data: OAuth2PasswordRequestForm = Depends(), authentication_service: AuthenticationService = Depends(concrete_authentication_service)):
    return authentication_service.authenticate(User(form_data.username, form_data.password))
