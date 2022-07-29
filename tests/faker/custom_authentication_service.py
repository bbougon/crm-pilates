import uuid

from crm_pilates.authenticating.authentication import AuthenticationService
from crm_pilates.authenticating.user import User
from crm_pilates.domain.exceptions import AggregateNotFoundException


class CustomAuthenticationService(AuthenticationService):

    def authenticate(self, user: User):
        return {"token": "my-token", "type": "bearer"}


class UnauthorizedAuthenticationService(AuthenticationService):

    def authenticate(self, user: User):
        raise AggregateNotFoundException(uuid.uuid4(), "User")
