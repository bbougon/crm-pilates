import uuid

from crm_pilates.authenticating.authentication import AuthenticationService
from crm_pilates.authenticating.authenticatinguser import AuthenticatingUser
from crm_pilates.domain.exceptions import AggregateNotFoundException


class CustomAuthenticationService(AuthenticationService):

    def authenticate(self, user: AuthenticatingUser):
        return {"token": "my-token", "type": "bearer"}


class UnauthorizedAuthenticationService(AuthenticationService):

    def authenticate(self, user: AuthenticatingUser):
        raise AggregateNotFoundException(uuid.uuid4(), "User")
