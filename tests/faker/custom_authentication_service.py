from fastapi import status

from crm_pilates.authenticating.authenticating_user import AuthenticatingUser
from crm_pilates.authenticating.authentication import (
    AuthenticationService,
)
from crm_pilates.web.api.exceptions import APIHTTPException


class CustomAuthenticationService(AuthenticationService):
    def validate_token(self, token):
        pass

    def authenticate(self, user: AuthenticatingUser):
        return {"token": "my-token", "type": "bearer"}


class UnauthorizedAuthenticationService(AuthenticationService):
    def validate_token(self, token):
        pass

    def authenticate(self, user: AuthenticatingUser):
        raise APIHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )


class AuthenticationExceptionAuthenticationService(AuthenticationService):
    def validate_token(self, token):
        raise APIHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    def authenticate(self, user: AuthenticatingUser):
        raise APIHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
