import uuid

from crm_pilates.authenticating.authenticating_user import AuthenticatingUser
from crm_pilates.authenticating.authentication import (
    AuthenticationService,
    AuthenticationException,
)
from crm_pilates.domain.exceptions import AggregateNotFoundException


class CustomAuthenticationService(AuthenticationService):
    def validate_token(self, token):
        pass

    def authenticate(self, user: AuthenticatingUser):
        return {"token": "my-token", "type": "bearer"}


class UnauthorizedAuthenticationService(AuthenticationService):
    def validate_token(self, token):
        pass

    def authenticate(self, user: AuthenticatingUser):
        raise AggregateNotFoundException(uuid.uuid4(), "User")


class AuthenticationExceptionAuthenticationService(AuthenticationService):
    def validate_token(self, token):
        raise AuthenticationException

    def authenticate(self, user: AuthenticatingUser):
        raise AuthenticationException
