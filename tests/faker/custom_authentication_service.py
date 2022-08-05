from crm_pilates.authenticating.authenticating_user import AuthenticatingUser
from crm_pilates.authenticating.authentication import (
    AuthenticationService,
    AuthenticationException,
)


class CustomAuthenticationService(AuthenticationService):
    def validate_token(self, token):
        pass

    def authenticate(self, user: AuthenticatingUser):
        return {"token": "my-token", "type": "bearer"}


class UnauthorizedAuthenticationService(AuthenticationService):
    def validate_token(self, token):
        pass

    def authenticate(self, user: AuthenticatingUser):
        raise AuthenticationException("Incorrect username or password")


class AuthenticationExceptionAuthenticationService(AuthenticationService):
    def validate_token(self, token):
        raise AuthenticationException("Incorrect username or password")

    def authenticate(self, user: AuthenticatingUser):
        raise AuthenticationException("Incorrect username or password")
