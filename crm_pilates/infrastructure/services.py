from crm_pilates.authenticating.authentication import AuthenticationService
from crm_pilates.infrastructure.authentication.JWTAuthenticationService import (
    JWTAuthenticationService,
)

concrete_authentication_service: AuthenticationService = JWTAuthenticationService
